#!/usr/bin/env python3
"""
POSIX File Locking Utility

Provides cross-platform file locking with stale lock detection and recovery.
Uses fcntl on POSIX systems for advisory locking.

Usage:
    from lockfile import LockFile

    # Context manager (recommended)
    with LockFile("/path/to/lockfile", timeout=30) as lock:
        # Critical section - only one process can be here
        do_exclusive_work()

    # Manual lock management
    lock = LockFile("/path/to/lockfile")
    try:
        lock.acquire(timeout=30)
        do_exclusive_work()
    finally:
        lock.release()
"""

import fcntl
import json
import logging
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


@dataclass
class LockMetadata:
    """Metadata stored in lock files for debugging and stale lock detection."""

    pid: int
    hostname: str
    acquired_at: float
    purpose: str
    owner: str


class LockError(Exception):
    """Base exception for lock-related errors."""

    pass


class LockTimeout(LockError):
    """Raised when lock acquisition times out."""

    pass


class StaleLockError(LockError):
    """Raised when a stale lock is detected."""

    pass


class LockFile:
    """
    POSIX file lock with stale lock detection.

    This class provides advisory file locking using fcntl (POSIX) with
    additional features:
    - Stale lock detection (process no longer exists)
    - Lock metadata for debugging
    - Timeout support
    - Context manager interface
    """

    def __init__(
        self,
        lock_path: str,
        stale_timeout: Optional[float] = None,
        purpose: str = "generic",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize a file lock.

        Args:
            lock_path: Path to the lock file
            stale_timeout: Optional timeout in seconds before considering lock stale
            purpose: Human-readable description of what this lock protects
            logger: Optional logger instance
        """
        self.lock_path = Path(lock_path)
        self.stale_timeout = stale_timeout
        self.purpose = purpose
        self.logger = logger or logging.getLogger(__name__)

        self._fd: Optional[int] = None
        self._acquired = False

    def _is_process_running(self, pid: int) -> bool:
        """
        Check if a process with given PID is running.

        Args:
            pid: Process ID to check

        Returns:
            True if process exists, False otherwise
        """
        try:
            # Send signal 0 - doesn't actually send a signal, just checks existence
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def _read_lock_metadata(self) -> Optional[LockMetadata]:
        """
        Read metadata from an existing lock file.

        Returns:
            LockMetadata if lock file exists and is valid, None otherwise
        """
        if not self.lock_path.exists():
            return None

        try:
            with open(self.lock_path, "r") as f:
                data = json.load(f)
                return LockMetadata(**data)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            self.logger.warning(f"Invalid lock metadata in {self.lock_path}: {e}")
            return None

    def _write_lock_metadata(self):
        """Write lock metadata to the lock file."""
        import socket

        metadata = LockMetadata(
            pid=os.getpid(),
            hostname=socket.gethostname(),
            acquired_at=time.time(),
            purpose=self.purpose,
            owner=os.environ.get("USER", "unknown"),
        )

        # Ensure parent directory exists
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.lock_path, "w") as f:
            json.dump(asdict(metadata), f, indent=2)

    def _check_stale_lock(self) -> bool:
        """
        Check if the current lock is stale.

        A lock is stale if:
        1. The owning process no longer exists, OR
        2. The lock has exceeded stale_timeout (if set)

        Returns:
            True if lock is stale, False otherwise
        """
        metadata = self._read_lock_metadata()

        if metadata is None:
            # No metadata means no valid lock
            return False

        # Check if process still exists
        if not self._is_process_running(metadata.pid):
            self.logger.warning(
                f"Stale lock detected: Process {metadata.pid} no longer exists"
            )
            return True

        # Check timeout if configured
        if self.stale_timeout is not None:
            age = time.time() - metadata.acquired_at
            if age > self.stale_timeout:
                self.logger.warning(
                    f"Stale lock detected: Lock age {age:.1f}s exceeds timeout {self.stale_timeout}s"
                )
                return True

        return False

    def acquire(self, timeout: Optional[float] = None, check_stale: bool = True):
        """
        Acquire the lock.

        Args:
            timeout: Optional timeout in seconds. None means block forever.
            check_stale: If True, check for and clear stale locks

        Raises:
            LockTimeout: If timeout is reached
            StaleLockError: If stale lock detected and could not be cleared
            LockError: If lock acquisition fails for other reasons
        """
        if self._acquired:
            raise LockError("Lock already acquired by this instance")

        # Check for stale lock first
        if check_stale and self._check_stale_lock():
            self.logger.info(f"Clearing stale lock: {self.lock_path}")
            try:
                self.lock_path.unlink(missing_ok=True)
            except OSError as e:
                raise StaleLockError(f"Could not clear stale lock: {e}")

        # Ensure parent directory exists
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)

        # Open lock file
        self._fd = os.open(str(self.lock_path), os.O_CREAT | os.O_RDWR)

        start_time = time.time()
        while True:
            try:
                # Try to acquire lock (non-blocking)
                fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

                # Success - write metadata
                self._write_lock_metadata()
                self._acquired = True

                self.logger.debug(f"Lock acquired: {self.lock_path}")
                return

            except BlockingIOError:
                # Lock is held by another process
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        os.close(self._fd)
                        self._fd = None
                        raise LockTimeout(
                            f"Could not acquire lock within {timeout}s: {self.lock_path}"
                        )

                # Wait a bit before retrying
                time.sleep(0.1)

            except Exception as e:
                # Clean up on error
                if self._fd is not None:
                    os.close(self._fd)
                    self._fd = None
                raise LockError(f"Failed to acquire lock: {e}")

    def release(self):
        """
        Release the lock.

        This is idempotent - calling multiple times is safe.
        """
        if not self._acquired:
            return

        try:
            if self._fd is not None:
                # Release lock
                fcntl.flock(self._fd, fcntl.LOCK_UN)
                os.close(self._fd)
                self._fd = None

            # Remove lock file
            self.lock_path.unlink(missing_ok=True)

            self._acquired = False
            self.logger.debug(f"Lock released: {self.lock_path}")

        except Exception as e:
            self.logger.error(f"Error releasing lock: {e}")
            # Still mark as released to avoid double-release attempts
            self._acquired = False
            raise LockError(f"Failed to release lock: {e}")

    def is_locked(self) -> bool:
        """
        Check if the lock is currently held by this instance.

        Returns:
            True if lock is acquired, False otherwise
        """
        return self._acquired

    def __enter__(self):
        """Context manager entry."""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
        return False

    def __del__(self):
        """Destructor - ensure lock is released."""
        if self._acquired:
            self.logger.warning(
                f"Lock not explicitly released, cleaning up: {self.lock_path}"
            )
            try:
                self.release()
            except Exception:
                pass


def main():
    """CLI entry point for testing and debugging."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test file locking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Acquire lock and hold for 10 seconds
  %(prog)s --lock /tmp/test.lock --duration 10

  # Check if lock is stale
  %(prog)s --check-stale /tmp/test.lock

  # Force clear a lock
  %(prog)s --clear /tmp/test.lock
        """,
    )

    parser.add_argument("--lock", type=str, help="Path to lock file")
    parser.add_argument(
        "--duration", type=float, default=5, help="Hold lock for N seconds"
    )
    parser.add_argument(
        "--timeout", type=float, default=10, help="Timeout for lock acquisition"
    )
    parser.add_argument(
        "--check-stale", type=str, metavar="LOCKFILE", help="Check if lock is stale"
    )
    parser.add_argument(
        "--clear", type=str, metavar="LOCKFILE", help="Force clear a lock file"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if args.check_stale:
        lock = LockFile(args.check_stale)
        if lock._check_stale_lock():
            print(f"✗ Lock is stale: {args.check_stale}")
            metadata = lock._read_lock_metadata()
            if metadata:
                print(f"  PID: {metadata.pid}")
                print(f"  Host: {metadata.hostname}")
                print(f"  Acquired: {metadata.acquired_at}")
                print(f"  Purpose: {metadata.purpose}")
            return 1
        else:
            print(f"✓ Lock is valid: {args.check_stale}")
            return 0

    if args.clear:
        print(f"Clearing lock: {args.clear}")
        Path(args.clear).unlink(missing_ok=True)
        print("✓ Lock cleared")
        return 0

    if args.lock:
        print(f"Attempting to acquire lock: {args.lock}")
        lock = LockFile(args.lock, purpose="CLI test")
        try:
            lock.acquire(timeout=args.timeout)
            print(f"✓ Lock acquired, holding for {args.duration} seconds...")
            time.sleep(args.duration)
            print("Releasing lock...")
            lock.release()
            print("✓ Lock released")
            return 0
        except LockTimeout:
            print(f"✗ Failed to acquire lock within {args.timeout} seconds")
            return 1
        except Exception as e:
            print(f"✗ Error: {e}")
            return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
