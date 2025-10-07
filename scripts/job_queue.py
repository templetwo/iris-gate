#!/usr/bin/env python3
"""
Filesystem-Based Job Queue

Provides a simple, dependency-free job queue using JSON files.
Designed for orchestrating parallel agent execution with priority support.

Usage:
    from job_queue import FSQueue, Job

    # Create queue
    queue = FSQueue(".ork/queue")

    # Enqueue a job
    job = Job(
        role="bug-catcher",
        description="Fix regression in S4 extraction",
        command="pytest tests/test_extraction.py --fix",
        priority=10
    )
    queue.enqueue(job)

    # Dequeue next job
    job = queue.dequeue()
    if job:
        print(f"Processing: {job.description}")
        # ... execute job ...
        queue.mark_complete(job.id)
"""

import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from lockfile import LockFile


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """
    Represents a single job in the queue.

    Attributes:
        role: Agent role to execute this job (e.g., "bug-catcher")
        description: Human-readable job description
        command: Shell command to execute
        priority: Lower number = higher priority (default: 50)
        timeout: Job timeout in seconds (default: 1800)
        max_retries: Maximum retry attempts (default: 2)
        id: Unique job identifier (auto-generated)
        status: Current job status
        created_at: Unix timestamp when job was created
        started_at: Unix timestamp when job started execution
        completed_at: Unix timestamp when job completed
        retry_count: Number of times this job has been retried
        error: Error message if job failed
        result: Job result data
        metadata: Additional job metadata
    """

    role: str
    description: str
    command: str
    priority: int = 50
    timeout: int = 1800
    max_retries: int = 2
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = JobStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    error: Optional[str] = None
    result: Optional[Dict] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert job to dictionary for serialization."""
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "Job":
        """Create job from dictionary."""
        # Convert status string to enum
        if "status" in data and isinstance(data["status"], str):
            data["status"] = JobStatus(data["status"])
        return cls(**data)


class FSQueue:
    """
    Filesystem-based job queue with priority support.

    Jobs are stored as JSON files in a queue directory. File locking
    ensures safe concurrent access.
    """

    def __init__(
        self,
        queue_dir: str,
        archive_dir: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the queue.

        Args:
            queue_dir: Directory to store queue files
            archive_dir: Optional directory for completed/failed jobs
            logger: Optional logger instance
        """
        self.queue_dir = Path(queue_dir)
        self.archive_dir = Path(archive_dir) if archive_dir else None
        self.logger = logger or logging.getLogger(__name__)

        # Ensure directories exist
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        if self.archive_dir:
            self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Lock file for queue operations
        self.lock_path = self.queue_dir / ".queue.lock"

    def _job_file_path(self, job: Job) -> Path:
        """
        Get the file path for a job.

        File naming: job_{priority}_{timestamp}_{id}.json
        This allows natural sorting by priority, then creation time.
        """
        timestamp = int(job.created_at * 1000)  # Milliseconds for uniqueness
        return self.queue_dir / f"job_{job.priority:03d}_{timestamp}_{job.id}.json"

    def _write_job(self, job: Job, path: Optional[Path] = None):
        """Write job to disk."""
        if path is None:
            path = self._job_file_path(job)

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(job.to_dict(), f, indent=2)

    def _read_job(self, path: Path) -> Optional[Job]:
        """Read job from disk."""
        try:
            with open(path, "r") as f:
                data = json.load(f)
                return Job.from_dict(data)
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            self.logger.error(f"Error reading job file {path}: {e}")
            return None

    def enqueue(self, job: Job) -> str:
        """
        Add a job to the queue.

        Args:
            job: Job to enqueue

        Returns:
            Job ID
        """
        with LockFile(
            str(self.lock_path), purpose="queue enqueue", logger=self.logger
        ):
            job.status = JobStatus.PENDING
            job.created_at = time.time()

            job_path = self._job_file_path(job)
            self._write_job(job, job_path)

            self.logger.info(f"Enqueued job: {job.id} (role={job.role}, priority={job.priority})")

        return job.id

    def dequeue(self, role_filter: Optional[str] = None) -> Optional[Job]:
        """
        Get the next pending job from the queue.

        Jobs are returned in priority order (lower priority number first),
        then by creation time (oldest first).

        Args:
            role_filter: If provided, only return jobs matching this role

        Returns:
            Next job to execute, or None if queue is empty
        """
        with LockFile(
            str(self.lock_path), purpose="queue dequeue", logger=self.logger
        ):
            # List all job files, sorted by filename (which encodes priority + timestamp)
            job_files = sorted(self.queue_dir.glob("job_*.json"))

            for job_file in job_files:
                job = self._read_job(job_file)

                if job is None:
                    continue

                # Skip non-pending jobs
                if job.status != JobStatus.PENDING:
                    continue

                # Apply role filter if provided
                if role_filter and job.role != role_filter:
                    continue

                # Mark as running
                job.status = JobStatus.RUNNING
                job.started_at = time.time()
                self._write_job(job, job_file)

                self.logger.info(f"Dequeued job: {job.id} (role={job.role})")
                return job

            return None

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get a specific job by ID.

        Args:
            job_id: Job ID to retrieve

        Returns:
            Job if found, None otherwise
        """
        with LockFile(str(self.lock_path), purpose="queue get", logger=self.logger):
            for job_file in self.queue_dir.glob("job_*.json"):
                if job_id in job_file.name:
                    return self._read_job(job_file)

            # Check archive if configured
            if self.archive_dir:
                for job_file in self.archive_dir.glob("job_*.json"):
                    if job_id in job_file.name:
                        return self._read_job(job_file)

        return None

    def update_job(self, job: Job):
        """
        Update an existing job.

        Args:
            job: Job with updated fields
        """
        with LockFile(
            str(self.lock_path), purpose="queue update", logger=self.logger
        ):
            # Find existing job file
            for job_file in self.queue_dir.glob("job_*.json"):
                if job.id in job_file.name:
                    self._write_job(job, job_file)
                    return

            # If not in queue, check archive
            if self.archive_dir:
                for job_file in self.archive_dir.glob("job_*.json"):
                    if job.id in job_file.name:
                        self._write_job(job, job_file)
                        return

            self.logger.warning(f"Job not found for update: {job.id}")

    def mark_complete(self, job_id: str, result: Optional[Dict] = None):
        """
        Mark a job as completed.

        Args:
            job_id: Job ID to mark complete
            result: Optional result data
        """
        job = self.get_job(job_id)
        if not job:
            self.logger.error(f"Job not found: {job_id}")
            return

        job.status = JobStatus.COMPLETED
        job.completed_at = time.time()
        job.result = result

        self._archive_job(job)

        self.logger.info(f"Job completed: {job_id}")

    def mark_failed(
        self, job_id: str, error: str, retry: bool = True
    ) -> Optional[Job]:
        """
        Mark a job as failed.

        Args:
            job_id: Job ID to mark failed
            error: Error message
            retry: If True and retries remaining, re-enqueue

        Returns:
            Re-enqueued job if retried, None otherwise
        """
        job = self.get_job(job_id)
        if not job:
            self.logger.error(f"Job not found: {job_id}")
            return None

        job.error = error
        job.retry_count += 1

        # Check if we should retry
        if retry and job.retry_count < job.max_retries:
            self.logger.info(
                f"Job failed, retrying ({job.retry_count}/{job.max_retries}): {job_id}"
            )
            job.status = JobStatus.PENDING
            job.started_at = None
            self.update_job(job)
            return job
        else:
            self.logger.error(f"Job failed permanently: {job_id} - {error}")
            job.status = JobStatus.FAILED
            job.completed_at = time.time()
            self._archive_job(job)
            return None

    def cancel_job(self, job_id: str):
        """
        Cancel a pending or running job.

        Args:
            job_id: Job ID to cancel
        """
        job = self.get_job(job_id)
        if not job:
            self.logger.error(f"Job not found: {job_id}")
            return

        if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
            self.logger.warning(f"Cannot cancel completed/failed job: {job_id}")
            return

        job.status = JobStatus.CANCELLED
        job.completed_at = time.time()
        self._archive_job(job)

        self.logger.info(f"Job cancelled: {job_id}")

    def _archive_job(self, job: Job):
        """Move a job to the archive directory."""
        if not self.archive_dir:
            # No archive configured, just delete from queue
            for job_file in self.queue_dir.glob(f"*{job.id}*.json"):
                job_file.unlink(missing_ok=True)
            return

        with LockFile(
            str(self.lock_path), purpose="queue archive", logger=self.logger
        ):
            # Find job file in queue
            for job_file in self.queue_dir.glob(f"*{job.id}*.json"):
                # Move to archive
                archive_path = self.archive_dir / job_file.name
                self._write_job(job, archive_path)
                job_file.unlink(missing_ok=True)
                return

    def list_jobs(
        self, status_filter: Optional[JobStatus] = None, role_filter: Optional[str] = None
    ) -> List[Job]:
        """
        List all jobs in the queue.

        Args:
            status_filter: Optional status to filter by
            role_filter: Optional role to filter by

        Returns:
            List of jobs matching filters
        """
        jobs = []

        with LockFile(str(self.lock_path), purpose="queue list", logger=self.logger):
            # Read from queue
            for job_file in sorted(self.queue_dir.glob("job_*.json")):
                job = self._read_job(job_file)
                if job:
                    jobs.append(job)

            # Read from archive if configured
            if self.archive_dir:
                for job_file in sorted(self.archive_dir.glob("job_*.json")):
                    job = self._read_job(job_file)
                    if job:
                        jobs.append(job)

        # Apply filters
        if status_filter:
            jobs = [j for j in jobs if j.status == status_filter]

        if role_filter:
            jobs = [j for j in jobs if j.role == role_filter]

        return jobs

    def clear_completed(self, max_age_days: Optional[int] = None):
        """
        Clear completed and failed jobs from archive.

        Args:
            max_age_days: Optional age threshold in days
        """
        if not self.archive_dir:
            return

        cutoff = time.time() - (max_age_days * 86400) if max_age_days else 0

        with LockFile(
            str(self.lock_path), purpose="queue clear", logger=self.logger
        ):
            for job_file in self.archive_dir.glob("job_*.json"):
                job = self._read_job(job_file)

                if not job:
                    continue

                # Skip if job is too recent
                if job.completed_at and job.completed_at > cutoff:
                    continue

                # Delete if completed or failed
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                    job_file.unlink(missing_ok=True)
                    self.logger.debug(f"Cleared archived job: {job.id}")

    def get_stats(self) -> Dict:
        """
        Get queue statistics.

        Returns:
            Dictionary with queue metrics
        """
        jobs = self.list_jobs()

        stats = {
            "total": len(jobs),
            "pending": sum(1 for j in jobs if j.status == JobStatus.PENDING),
            "running": sum(1 for j in jobs if j.status == JobStatus.RUNNING),
            "completed": sum(1 for j in jobs if j.status == JobStatus.COMPLETED),
            "failed": sum(1 for j in jobs if j.status == JobStatus.FAILED),
            "cancelled": sum(1 for j in jobs if j.status == JobStatus.CANCELLED),
            "by_role": {},
        }

        # Count by role
        for job in jobs:
            if job.role not in stats["by_role"]:
                stats["by_role"][job.role] = {"pending": 0, "running": 0, "completed": 0}

            if job.status == JobStatus.PENDING:
                stats["by_role"][job.role]["pending"] += 1
            elif job.status == JobStatus.RUNNING:
                stats["by_role"][job.role]["running"] += 1
            elif job.status == JobStatus.COMPLETED:
                stats["by_role"][job.role]["completed"] += 1

        return stats


def main():
    """CLI entry point for queue management."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage job queue",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enqueue a job
  %(prog)s enqueue --role bug-catcher --description "Fix bug" --command "pytest tests/"

  # List all jobs
  %(prog)s list

  # List pending jobs
  %(prog)s list --status pending

  # Dequeue next job
  %(prog)s dequeue

  # Get queue stats
  %(prog)s stats

  # Clear completed jobs older than 7 days
  %(prog)s clear --max-age 7
        """,
    )

    parser.add_argument(
        "action",
        choices=["enqueue", "dequeue", "list", "stats", "clear", "cancel"],
        help="Action to perform",
    )

    parser.add_argument("--queue-dir", default=".ork/queue", help="Queue directory")
    parser.add_argument(
        "--archive-dir", default=".ork/archive", help="Archive directory"
    )

    # Enqueue options
    parser.add_argument("--role", help="Job role")
    parser.add_argument("--description", help="Job description")
    parser.add_argument("--command", help="Command to execute")
    parser.add_argument("--priority", type=int, default=50, help="Job priority")

    # List options
    parser.add_argument(
        "--status",
        choices=["pending", "running", "completed", "failed", "cancelled"],
        help="Filter by status",
    )

    # Clear options
    parser.add_argument(
        "--max-age", type=int, help="Maximum age in days for clear operation"
    )

    # Cancel options
    parser.add_argument("--job-id", help="Job ID to cancel")

    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Create queue
    queue = FSQueue(args.queue_dir, args.archive_dir)

    if args.action == "enqueue":
        if not all([args.role, args.description, args.command]):
            print("Error: --role, --description, and --command required for enqueue")
            return 1

        job = Job(
            role=args.role,
            description=args.description,
            command=args.command,
            priority=args.priority,
        )

        job_id = queue.enqueue(job)
        print(f"✓ Enqueued job: {job_id}")
        return 0

    elif args.action == "dequeue":
        job = queue.dequeue()
        if job:
            print(f"✓ Dequeued job: {job.id}")
            print(f"  Role: {job.role}")
            print(f"  Description: {job.description}")
            print(f"  Command: {job.command}")
            return 0
        else:
            print("Queue is empty")
            return 1

    elif args.action == "list":
        status_filter = JobStatus(args.status) if args.status else None
        jobs = queue.list_jobs(status_filter=status_filter)

        if not jobs:
            print("No jobs found")
            return 0

        print(f"\n{'ID':<38} {'Role':<20} {'Status':<12} {'Description':<40}")
        print("-" * 110)

        for job in jobs:
            print(
                f"{job.id:<38} {job.role:<20} {job.status.value:<12} {job.description[:40]:<40}"
            )

        print(f"\nTotal: {len(jobs)} jobs")
        return 0

    elif args.action == "stats":
        stats = queue.get_stats()
        print("\n=== Queue Statistics ===")
        print(json.dumps(stats, indent=2))
        return 0

    elif args.action == "clear":
        queue.clear_completed(max_age_days=args.max_age)
        print("✓ Cleared completed jobs")
        return 0

    elif args.action == "cancel":
        if not args.job_id:
            print("Error: --job-id required for cancel")
            return 1

        queue.cancel_job(args.job_id)
        print(f"✓ Cancelled job: {args.job_id}")
        return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
