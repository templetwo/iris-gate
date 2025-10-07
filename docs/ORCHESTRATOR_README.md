# IRIS Gate Orchestrator - Parallel Agent Execution

## Overview

The IRIS Gate Orchestrator provides safe, isolated parallel execution for agent-based workflows. It uses git worktrees for filesystem isolation, ensuring agents can work concurrently without conflicts.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Orchestrator Runner                       │
│  - Max 3 concurrent workers (configurable)                   │
│  - Semaphore-based concurrency control                       │
│  - Merge gates for pre-integration validation                │
└──────────┬───────────────────────────────────────────────────┘
           │
           ├──> Worker 1 ──> Git Worktree 1 ──> Execute Job
           ├──> Worker 2 ──> Git Worktree 2 ──> Execute Job
           └──> Worker 3 ──> Git Worktree 3 ──> Execute Job
                   │
                   ├──> Run Merge Gates (tests, linting, etc.)
                   └──> Merge changes back to main
```

### Components

1. **Job Queue** (`scripts/job_queue.py`)
   - Filesystem-based JSON queue
   - Priority support (lower number = higher priority)
   - Automatic archiving of completed jobs
   - Thread-safe with file locking

2. **Lock Manager** (`scripts/lockfile.py`)
   - POSIX file locks for concurrency control
   - Stale lock detection (abandoned processes)
   - Context manager interface for safety

3. **Orchestrator Runner** (`scripts/orchestrator_runner.py`)
   - Git worktree management
   - Worker thread coordination
   - Merge gate execution
   - Job lifecycle management

4. **CI Gates** (`scripts/ci_gates.sh`)
   - Pre-merge validation gates
   - Code style checking (ruff)
   - Test suite execution (pytest)
   - Security scanning (secrets detection)
   - File size validation

## Quick Start

### 1. Initialize Orchestrator

```bash
make ork-init
```

This creates:
- `.ork/queue/` - Job queue files
- `.ork/archive/` - Completed/failed job history
- `.ork/locks/` - File locks for concurrency
- `.ork/worktrees/` - Git worktrees for isolation

### 2. Enqueue Jobs

```bash
# Enqueue a bug-fixing job
make ork-enqueue \
  ROLE=bug-catcher \
  DESC="Fix test failures in S4 extraction" \
  CMD="pytest tests/test_extraction.py --fix" \
  PRIORITY=10

# Enqueue a style formatting job
make ork-enqueue \
  ROLE=style-warden \
  DESC="Format Python files" \
  CMD="ruff format scripts/ tests/" \
  PRIORITY=50

# Enqueue test creation
make ork-enqueue \
  ROLE=test-weaver \
  DESC="Add tests for MCP integration" \
  CMD="pytest tests/test_mcp_init.py --create" \
  PRIORITY=30
```

### 3. Run Orchestrator

```bash
# Daemon mode (runs until interrupted)
make ork-run WORKERS=3

# Process queue once and exit
make ork-run-once

# Dry-run mode (shows what would happen)
make ork-test
```

### 4. Monitor Status

```bash
# View queue and worker status
make ork-status

# List all jobs
python3 scripts/job_queue.py list

# List only pending jobs
python3 scripts/job_queue.py list --status pending

# Get queue statistics
python3 scripts/job_queue.py stats
```

### 5. Cleanup

```bash
# Clean stale worktrees and archived jobs
make ork-clean

# Clear jobs older than 7 days
python3 scripts/job_queue.py clear --max-age 7
```

## Agent Roles

Roles define behavioral constraints and allowed tools for each agent. Configured in `config/agent_roles.yaml`:

| Role | Description | Allowed Tools |
|------|-------------|---------------|
| **bug-catcher** | Reproduce, diagnose, and fix bugs | pytest, python, bash, ruff, grep |
| **style-warden** | Enforce code style consistency | ruff, black, isort, bash |
| **patch-surgeon** | Polish and prepare code for merge | git, pytest, ruff, bash |
| **test-weaver** | Create and repair tests (TDD) | pytest, python, bash |
| **code-implementer** | Implement code from specifications | python, pytest, ruff, bash |
| **code-planner** | Transform tasks into structured plans | bash, grep, find, git |

### Forbidden Patterns (All Roles)

All roles have these global safety restrictions:
- No destructive operations: `rm -rf /`, `dd if=/dev/zero`, etc.
- No force pushes to main/master
- No `git push --force origin main`

## Configuration

### Orchestrator Settings (`config/orchestrator.yaml`)

```yaml
orchestrator:
  max_concurrent: 3              # Maximum parallel workers
  worktree_base: ".ork/worktrees"
  queue_dir: ".ork/queue"
  job_timeout: 1800              # 30 minutes
  stale_lock_timeout: 3600       # 1 hour

merge_gates:
  - name: "style_check"
    command: "ruff check scripts/ tests/"
    required: true
    timeout: 60

  - name: "test_suite"
    command: "pytest tests/ -v"
    required: true
    timeout: 300
```

### Job Priority Levels

Priority determines execution order (lower = higher priority):

- **0-9**: Critical (emergency fixes)
- **10-49**: High (bugs, regressions)
- **50-99**: Normal (features, refactoring)
- **100+**: Low (cleanup, documentation)

## Advanced Usage

### Direct Python API

```python
from scripts.job_queue import FSQueue, Job, JobStatus

# Create queue
queue = FSQueue(".ork/queue")

# Enqueue job programmatically
job = Job(
    role="bug-catcher",
    description="Fix S4 extraction bug",
    command="python scripts/fix_s4_bug.py",
    priority=10,
    timeout=600
)

job_id = queue.enqueue(job)

# Check job status
job = queue.get_job(job_id)
print(f"Status: {job.status}")

# Mark complete
queue.mark_complete(job_id, result={"fixed": True})
```

### Custom Merge Gates

Add custom validation gates in `config/orchestrator.yaml`:

```yaml
merge_gates:
  - name: "custom_validator"
    type: "shell"
    command: "./scripts/my_validator.sh"
    required: true
    timeout: 120

  - name: "integration_tests"
    command: "pytest tests/integration/ -v"
    required: false  # Optional gate
    timeout: 600
```

### Worktree Isolation

Each job runs in an isolated git worktree:

```
.ork/worktrees/
├── ork-bug-catcher-1696348800-f78ee6a4/
│   ├── scripts/
│   ├── tests/
│   └── ... (full repo copy)
├── ork-style-warden-1696348801-c677e1bf/
└── ork-test-weaver-1696348802-20b037a2/
```

Benefits:
- No file conflicts between agents
- Safe parallel execution
- Clean rollback on failure
- Isolated test runs

### Job Lifecycle

```
PENDING → (dequeue) → RUNNING → (success) → COMPLETED
                         ↓
                     (failure)
                         ↓
                   (retry < max_retries) → PENDING
                         ↓
                    (retry exhausted) → FAILED
```

Jobs can also be manually cancelled:
```bash
python3 scripts/job_queue.py cancel --job-id <JOB_ID>
```

## Troubleshooting

### Stale Locks

If orchestrator crashes, stale locks may remain:

```bash
# Check for stale locks
python3 scripts/lockfile.py --check-stale .ork/locks/queue.lock

# Force clear a lock
python3 scripts/lockfile.py --clear .ork/locks/queue.lock
```

### Orphaned Worktrees

If jobs fail, worktrees may not be cleaned up:

```bash
# List all worktrees
git worktree list

# Remove orphaned worktrees
git worktree prune

# Or use orchestrator cleanup
make ork-clean
```

### Job Failures

Check archived jobs for failure details:

```bash
# List failed jobs
python3 scripts/job_queue.py list --status failed

# Inspect specific job
python3 scripts/job_queue.py list | grep <JOB_ID>
```

Failed job files in `.ork/archive/` contain:
- Error messages (`error` field)
- Retry count (`retry_count`)
- Execution timestamps
- Full command that was attempted

### Merge Conflicts

If a worktree has uncommitted changes from a previous run:

```bash
# Check worktree status
cd .ork/worktrees/ork-<role>-<timestamp>-<id>
git status

# Abandon changes and remove
cd ../../../
git worktree remove --force .ork/worktrees/ork-<role>-<timestamp>-<id>
```

## Integration with CI/CD

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run CI gates before commit
./scripts/ci_gates.sh
exit $?
```

### GitHub Actions

```yaml
name: Orchestrator Tests

on: [push, pull_request]

jobs:
  test-orchestrator:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Initialize orchestrator
        run: make ork-init

      - name: Run orchestrator tests
        run: make ork-test

      - name: Run CI gates
        run: ./scripts/ci_gates.sh all
```

## Performance

### Benchmarks

Tested on MacBook Pro M1, 16GB RAM:

| Metric | Value |
|--------|-------|
| Job enqueue | ~10ms |
| Job dequeue | ~15ms |
| Lock acquire/release | ~1ms |
| Worktree creation | ~500ms |
| Worktree removal | ~300ms |
| Full job cycle (dry-run) | ~2s |

### Scaling

- **Queue**: Handles 1000+ jobs efficiently
- **Workers**: Recommended 3-5 (diminishing returns beyond 5)
- **Disk Space**: Each worktree ~100MB (varies by repo size)
- **Memory**: ~50MB per worker thread

## Best Practices

1. **Start Small**: Begin with 1-2 workers, scale as needed
2. **Use Priorities**: Critical fixes = low numbers, cleanup = high numbers
3. **Set Timeouts**: Prevent runaway jobs from blocking queue
4. **Monitor Status**: Use `make ork-status` regularly
5. **Clean Regularly**: Archive old jobs with `make ork-clean`
6. **Test Dry-Run**: Always test with `--dry-run` first
7. **Check Gates**: Ensure merge gates are fast (<5min total)
8. **Log Everything**: Review `.ork/orchestrator.log` for issues

## Comparison with Other Systems

| Feature | IRIS Orchestrator | Jenkins | GitHub Actions | Celery |
|---------|-------------------|---------|----------------|--------|
| Setup Complexity | Low | High | Medium | Medium |
| Dependencies | None (filesystem) | Java | GitHub | Redis/RabbitMQ |
| Isolation | Git worktrees | Workspaces | Containers | Process |
| Local-first | ✓ | ✗ | ✗ | ✗ |
| Priority Queue | ✓ | ✓ | Limited | ✓ |
| Merge Gates | ✓ | Via plugins | Via workflows | Manual |

## Version History

### v0.3.4 (Current)
- Initial orchestrator implementation
- 3-worker concurrency support
- Git worktree isolation
- Filesystem-based job queue
- Role-based tool whitelisting
- Pre-merge validation gates
- Makefile integration

## References

- Git Worktrees: https://git-scm.com/docs/git-worktree
- POSIX File Locking: https://linux.die.