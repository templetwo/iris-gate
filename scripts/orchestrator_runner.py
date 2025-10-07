#!/usr/bin/env python3
"""
IRIS Gate Orchestrator - Parallel Agent Execution with Git Worktrees

Coordinates parallel agent execution using git worktrees for isolation.
Implements concurrency control, merge gates, and role-based execution.

Usage:
    # Start orchestrator with 3 workers
    python scripts/orchestrator_runner.py --workers 3

    # Process queue once and exit
    python scripts/orchestrator_runner.py --once

    # Dry-run mode
    python scripts/orchestrator_runner.py --dry-run

Architecture:
    - Each agent runs in an isolated git worktree
    - Filesystem-based job queue with priority support
    - Merge gates validate changes before integration
    - Role-based tool whitelisting (configured in agent_roles.yaml)
    - Semaphore-based concurrency control
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from job_queue import FSQueue, Job, JobStatus
from lockfile import LockFile


class WorktreeManager:
    """Manages git worktrees for agent isolation."""

    def __init__(self, base_dir: str, logger: logging.Logger):
        """
        Initialize worktree manager.

        Args:
            base_dir: Base directory for worktrees
            logger: Logger instance
        """
        self.base_dir = Path(base_dir)
        self.logger = logger

        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_worktree(self, role: str, job_id: str) -> Optional[Path]:
        """
        Create a new git worktree for job execution.

        Args:
            role: Agent role name
            job_id: Job identifier

        Returns:
            Path to worktree directory, or None on error
        """
        timestamp = int(time.time())
        worktree_name = f"ork-{role}-{timestamp}-{job_id[:8]}"
        worktree_path = self.base_dir / worktree_name

        try:
            # Create worktree from main branch
            result = subprocess.run(
                ["git", "worktree", "add", str(worktree_path), "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )

            self.logger.info(f"Created worktree: {worktree_path}")
            return worktree_path

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create worktree: {e.stderr}")
            return None

    def remove_worktree(self, worktree_path: Path, force: bool = False):
        """
        Remove a git worktree.

        Args:
            worktree_path: Path to worktree to remove
            force: If True, force removal even if dirty
        """
        try:
            cmd = ["git", "worktree", "remove", str(worktree_path)]
            if force:
                cmd.append("--force")

            subprocess.run(cmd, capture_output=True, text=True, check=True)

            self.logger.info(f"Removed worktree: {worktree_path}")

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to remove worktree: {e.stderr}")

            # Try to clean up manually
            if worktree_path.exists():
                shutil.rmtree(worktree_path, ignore_errors=True)

    def cleanup_stale_worktrees(self, max_age_hours: int = 24):
        """
        Remove abandoned worktrees older than max_age_hours.

        Args:
            max_age_hours: Maximum age before considering worktree stale
        """
        cutoff = time.time() - (max_age_hours * 3600)

        for worktree_dir in self.base_dir.glob("ork-*"):
            if not worktree_dir.is_dir():
                continue

            # Check age
            mtime = worktree_dir.stat().st_mtime
            if mtime > cutoff:
                continue

            self.logger.warning(f"Cleaning up stale worktree: {worktree_dir}")
            self.remove_worktree(worktree_dir, force=True)


class MergeGateRunner:
    """Runs merge gates to validate changes before integration."""

    def __init__(self, gates_config: List[Dict], logger: logging.Logger):
        """
        Initialize merge gate runner.

        Args:
            gates_config: List of gate configurations from orchestrator.yaml
            logger: Logger instance
        """
        self.gates = gates_config
        self.logger = logger

    def run_gates(self, worktree_path: Path) -> bool:
        """
        Run all merge gates in the worktree.

        Args:
            worktree_path: Path to worktree directory

        Returns:
            True if all gates pass, False otherwise
        """
        if not self.gates:
            self.logger.info("No merge gates configured, skipping validation")
            return True

        self.logger.info(f"Running {len(self.gates)} merge gates...")

        for gate in self.gates:
            gate_name = gate.get("name", "unnamed")
            gate_type = gate.get("type", "shell")
            required = gate.get("required", True)
            timeout = gate.get("timeout", 60)

            if gate_type != "shell":
                self.logger.warning(f"Unknown gate type '{gate_type}', skipping")
                continue

            command = gate.get("command")
            if not command:
                self.logger.error(f"Gate '{gate_name}' has no command")
                if required:
                    return False
                continue

            self.logger.info(f"Running gate: {gate_name}")

            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=worktree_path,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

                if result.returncode == 0:
                    self.logger.info(f"✓ Gate passed: {gate_name}")
                else:
                    self.logger.error(
                        f"✗ Gate failed: {gate_name}\n{result.stdout}\n{result.stderr}"
                    )
                    if required:
                        return False

            except subprocess.TimeoutExpired:
                self.logger.error(f"✗ Gate timeout: {gate_name} (>{timeout}s)")
                if required:
                    return False

            except Exception as e:
                self.logger.error(f"✗ Gate error: {gate_name} - {e}")
                if required:
                    return False

        self.logger.info("✓ All merge gates passed")
        return True


class AgentWorker:
    """Worker thread that processes jobs from the queue."""

    def __init__(
        self,
        worker_id: int,
        queue: FSQueue,
        worktree_mgr: WorktreeManager,
        gate_runner: MergeGateRunner,
        config: Dict,
        semaphore: threading.Semaphore,
        logger: logging.Logger,
        dry_run: bool = False,
    ):
        """
        Initialize agent worker.

        Args:
            worker_id: Unique worker identifier
            queue: Job queue
            worktree_mgr: Worktree manager
            gate_runner: Merge gate runner
            config: Orchestrator configuration
            semaphore: Concurrency semaphore
            logger: Logger instance
            dry_run: If True, don't actually execute jobs
        """
        self.worker_id = worker_id
        self.queue = queue
        self.worktree_mgr = worktree_mgr
        self.gate_runner = gate_runner
        self.config = config
        self.semaphore = semaphore
        self.logger = logger
        self.dry_run = dry_run

        self.stop_flag = threading.Event()

    def run(self):
        """Main worker loop."""
        self.logger.info(f"Worker {self.worker_id} started")

        while not self.stop_flag.is_set():
            # Acquire semaphore slot
            if not self.semaphore.acquire(timeout=1.0):
                continue

            try:
                # Dequeue next job
                job = self.queue.dequeue()

                if job is None:
                    # No jobs available, wait a bit
                    time.sleep(1.0)
                    continue

                self.logger.info(f"Worker {self.worker_id} processing job {job.id}")

                # Process job
                success = self.process_job(job)

                if success:
                    self.queue.mark_complete(job.id)
                else:
                    self.queue.mark_failed(job.id, "Job execution failed")

            finally:
                # Always release semaphore
                self.semaphore.release()

        self.logger.info(f"Worker {self.worker_id} stopped")

    def process_job(self, job: Job) -> bool:
        """
        Process a single job.

        Args:
            job: Job to process

        Returns:
            True if job succeeded, False otherwise
        """
        if self.dry_run:
            self.logger.info(f"[DRY-RUN] Would execute: {job.command}")
            time.sleep(2)  # Simulate work
            return True

        # Create worktree
        worktree_path = self.worktree_mgr.create_worktree(job.role, job.id)

        if worktree_path is None:
            self.logger.error(f"Failed to create worktree for job {job.id}")
            return False

        try:
            # Execute job command in worktree
            self.logger.info(f"Executing command in worktree: {job.command}")

            result = subprocess.run(
                job.command,
                shell=True,
                cwd=worktree_path,
                capture_output=True,
                text=True,
                timeout=job.timeout,
            )

            if result.returncode != 0:
                self.logger.error(
                    f"Command failed:\n{result.stdout}\n{result.stderr}"
                )
                return False

            # Run merge gates
            if not self.gate_runner.run_gates(worktree_path):
                self.logger.error("Merge gates failed, not merging changes")
                return False

            # Merge changes back to main
            if not self.merge_changes(worktree_path, job):
                self.logger.error("Failed to merge changes")
                return False

            self.logger.info(f"Job completed successfully: {job.id}")
            return True

        except subprocess.TimeoutExpired:
            self.logger.error(f"Job timeout after {job.timeout}s: {job.id}")
            return False

        except Exception as e:
            self.logger.error(f"Job execution error: {e}")
            return False

        finally:
            # Clean up worktree
            auto_cleanup = self.config.get("worktree", {}).get("auto_cleanup", True)
            preserve_on_failure = self.config.get("worktree", {}).get(
                "preserve_on_failure", True
            )

            if auto_cleanup or not preserve_on_failure:
                self.worktree_mgr.remove_worktree(worktree_path)

    def merge_changes(self, worktree_path: Path, job: Job) -> bool:
        """
        Merge changes from worktree back to main branch.

        Args:
            worktree_path: Path to worktree
            job: Job that generated the changes

        Returns:
            True if merge succeeded, False otherwise
        """
        try:
            # Check if there are changes to merge
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                check=True,
            )

            if not result.stdout.strip():
                self.logger.info("No changes to merge")
                return True

            # Commit changes in worktree
            subprocess.run(
                ["git", "add", "-A"],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                check=True,
            )

            commit_msg = f"{job.role}: {job.description}\n\nJob ID: {job.id}"

            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Get current branch name
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                check=True,
            )
            branch_name = result.stdout.strip()

            # Merge into main (from main repo directory)
            subprocess.run(
                ["git", "merge", "--no-ff", branch_name, "-m", f"Merge {job.role} job {job.id}"],
                capture_output=True,
                text=True,
                check=True,
            )

            self.logger.info("Changes merged successfully")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Merge failed: {e.stderr}")
            return False

    def stop(self):
        """Signal worker to stop."""
        self.stop_flag.set()


class Orchestrator:
    """Main orchestrator coordinating parallel agent execution."""

    def __init__(self, config_path: str = "config/orchestrator.yaml", dry_run: bool = False):
        """
        Initialize orchestrator.

        Args:
            config_path: Path to orchestrator configuration
            dry_run: If True, don't actually execute jobs
        """
        self.config_path = Path(config_path)
        self.dry_run = dry_run

        # Load configuration
        self.config = self._load_config()

        # Set up logging
        log_level = logging.DEBUG if self.config.get("debug", {}).get("enabled") else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

        # Initialize components
        orch_config = self.config.get("orchestrator", {})

        self.queue = FSQueue(
            queue_dir=orch_config.get("queue_dir", ".ork/queue"),
            archive_dir=self.config.get("queue", {}).get("archive_dir", ".ork/archive"),
            logger=self.logger,
        )

        self.worktree_mgr = WorktreeManager(
            base_dir=orch_config.get("worktree_base", ".ork/worktrees"),
            logger=self.logger,
        )

        merge_gates = self.config.get("merge_gates", [])
        self.gate_runner = MergeGateRunner(merge_gates, self.logger)

        # Concurrency control
        max_concurrent = orch_config.get("max_concurrent", 3)
        self.semaphore = threading.Semaphore(max_concurrent)

        self.workers: List[AgentWorker] = []
        self.worker_threads: List[threading.Thread] = []

    def _load_config(self) -> Dict:
        """Load orchestrator configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration not found: {self.config_path}")

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def start(self, num_workers: int = 3, run_once: bool = False):
        """
        Start orchestrator workers.

        Args:
            num_workers: Number of worker threads to spawn
            run_once: If True, process queue once and exit
        """
        self.logger.info(f"Starting orchestrator with {num_workers} workers")

        # Clean up stale worktrees
        max_age = self.config.get("worktree", {}).get("max_age_hours", 24)
        self.worktree_mgr.cleanup_stale_worktrees(max_age_hours=max_age)

        # Create workers
        for i in range(num_workers):
            worker = AgentWorker(
                worker_id=i,
                queue=self.queue,
                worktree_mgr=self.worktree_mgr,
                gate_runner=self.gate_runner,
                config=self.config,
                semaphore=self.semaphore,
                logger=self.logger,
                dry_run=self.dry_run,
            )

            self.workers.append(worker)

            if run_once:
                # Run synchronously
                job = self.queue.dequeue()
                if job:
                    worker.process_job(job)
                else:
                    self.logger.info("No jobs in queue to process")
            else:
                # Start worker thread
                thread = threading.Thread(target=worker.run, name=f"Worker-{i}")
                thread.daemon = True
                thread.start()
                self.worker_threads.append(thread)

        if not run_once:
            self.logger.info("Orchestrator running (Ctrl+C to stop)")

            # Wait for threads
            try:
                for thread in self.worker_threads:
                    thread.join()
            except KeyboardInterrupt:
                self.logger.info("Shutting down orchestrator...")
                self.stop()

    def stop(self):
        """Stop all workers."""
        for worker in self.workers:
            worker.stop()

        for thread in self.worker_threads:
            thread.join(timeout=5.0)

        self.logger.info("Orchestrator stopped")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="IRIS Gate Orchestrator - Parallel Agent Execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with 3 workers (daemon mode)
  %(prog)s --workers 3

  # Process queue once and exit
  %(prog)s --once

  # Dry-run mode (no actual execution)
  %(prog)s --dry-run

  # Custom config
  %(prog)s --config config/orchestrator.yaml --workers 5
        """,
    )

    parser.add_argument(
        "--config",
        default="config/orchestrator.yaml",
        help="Path to orchestrator config (default: config/orchestrator.yaml)",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=3,
        help="Number of worker threads (default: 3)",
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Process queue once and exit (default: daemon mode)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run mode (show what would happen)",
    )

    args = parser.parse_args()

    try:
        orchestrator = Orchestrator(config_path=args.config, dry_run=args.dry_run)
        orchestrator.start(num_workers=args.workers, run_once=args.once)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nShutdown requested")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
