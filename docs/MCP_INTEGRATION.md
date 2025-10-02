# MCP Integration for IRIS Gate

**Version:** 1.0
**Last Updated:** 2025-10-02
**Protocol Tier:** Tier 1 (Local-First)

## Overview

The Model Context Protocol (MCP) integration provides IRIS Gate with persistent context storage, semantic search capabilities, and automated version control. This document describes the complete MCP architecture, installation, usage, and troubleshooting.

## Architecture

IRIS Gate implements a **Tier 1 (Local-First)** MCP architecture with three core servers:

```
┌─────────────────────────────────────────────────────────┐
│                     IRIS Gate                           │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   ChromaDB   │  │     Git      │  │  Quick-Data  │ │
│  │   (Vector    │  │  (Version    │  │  (Key-Value  │ │
│  │    Store)    │  │   Control)   │  │   Storage)   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                 │                  │         │
│         └─────────────────┴──────────────────┘         │
│                           │                            │
│                  iris_vault/.mcp/                      │
└─────────────────────────────────────────────────────────┘
```

### Server Capabilities

| Server | Purpose | Capabilities | Storage Location |
|--------|---------|--------------|------------------|
| **ChromaDB** | Vector database for semantic search | - Scroll embedding<br>- S4 state retrieval<br>- Cross-session search | `iris_vault/chromadb/` |
| **Git** | Version control for S4 states | - Auto-commit states<br>- Change tracking<br>- Diff generation | `.git/` |
| **Quick-Data** | Fast key-value storage | - Session metadata<br>- Ephemeral data<br>- Run statistics | `iris_vault/quickdata/` |

## Installation

### Prerequisites

- Python 3.10+
- Git installed and initialized
- 500MB+ free disk space (for embeddings)

### Quick Start

```bash
# 1. Install MCP dependencies
make mcp-init

# 2. Test connectivity
make mcp-test

# 3. Index existing scrolls (if any)
make mcp-index

# 4. Verify status
make mcp-status
```

### Manual Installation

If you prefer manual setup:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize MCP environment
python scripts/init_mcp.py --init

# Test all servers
python scripts/init_mcp.py --test-all
```

## Configuration

MCP servers are configured in `.mcp-config.json`:

```json
{
  "version": "1.0",
  "servers": {
    "chromadb": {
      "enabled": true,
      "config": {
        "persist_directory": "./iris_vault/chromadb",
        "collection_name": "iris_context",
        "anonymized_telemetry": false
      }
    },
    "git": {
      "enabled": true,
      "config": {
        "repo_path": ".",
        "auto_commit": false,
        "track_changes": true
      }
    },
    "quickdata": {
      "enabled": true,
      "config": {
        "data_path": "./iris_vault/quickdata",
        "format": "json",
        "auto_backup": true
      }
    }
  }
}
```

### Customizing Configuration

To modify server behavior:

1. Edit `.mcp-config.json`
2. Re-run `make mcp-init`
3. Test with `make mcp-test`

**Common customizations:**

- **Change ChromaDB location:** Modify `persist_directory`
- **Enable auto-commit:** Set `git.config.auto_commit` to `true`
- **Adjust backup frequency:** Change `quickdata.config.backup_interval_hours`

## Usage

### 1. ChromaDB - Semantic Scroll Search

ChromaDB enables semantic search across all IRIS scroll archives.

#### Index Scrolls

```bash
# Index all sessions
make mcp-index

# Index specific session
python scripts/index_scrolls.py --session BIOELECTRIC_CHAMBERED_20251001054935

# View indexing statistics
python scripts/index_scrolls.py --stats
```

#### Search for Similar S4 States

```bash
# Search by natural language query
python scripts/index_scrolls.py --search "concentric rings with high convergence" \
    --chamber S4 --top-k 10

# Filter by mirror (model)
python scripts/index_scrolls.py --search "stable attractor state" \
    --mirror "anthropic_claude-sonnet-4.5" \
    --chamber S4

# Filter by convergence threshold
python scripts/index_scrolls.py --search "bioelectric pattern formation" \
    --convergence 0.7 \
    --top-k 5
```

#### Example Output

```
=== Search Results (top 3) ===
Query: concentric rings with high convergence

1. Similarity: 0.923
   ID: BIOELECTRIC_20251001_anthropic_claude-sonnet-4.5_S4_turn_025
   Chamber: S4
   Mirror: anthropic_claude-sonnet-4.5
   Turn: 25
   Convergence: 0.85
   Pressure: 1.0/5
   Document preview: Living Scroll: Concentric rings radiating outward...

2. Similarity: 0.891
   [... additional results ...]
```

#### Python API

```python
from scripts.index_scrolls import ScrollIndexer

# Initialize indexer
indexer = ScrollIndexer(vault_path="iris_vault")

# Search for similar states
results = indexer.search_similar_s4_states(
    query="stable bioelectric convergence",
    top_k=10,
    filters={"chamber": "S4", "convergence_threshold": 0.8}
)

# Process results
for result in results:
    print(f"Similarity: {result['similarity_score']:.3f}")
    print(f"Metadata: {result['metadata']}")
```

### 2. Git MCP Wrapper - Auto-Commit S4 States

The Git wrapper provides safe, automated version control for S4 states.

#### Auto-Commit S4 State Extraction

```bash
# Commit a newly extracted S4 state
python scripts/git_mcp_wrapper.py --auto-commit \
    --state-path sandbox/states/BIOELECTRIC_20251001.json \
    --session-id BIOELECTRIC_CHAMBERED_20251001054935

# Include additional files
python scripts/git_mcp_wrapper.py --auto-commit \
    --state-path sandbox/states/state.json \
    --session-id BIOELECTRIC_20251001 \
    --additional-files sandbox/states/metadata.json reports/summary.md

# Dry-run mode (test without committing)
python scripts/git_mcp_wrapper.py --auto-commit \
    --state-path sandbox/states/state.json \
    --session-id BIOELECTRIC_20251001 \
    --dry-run
```

#### Validate Working Tree

```bash
# Check for uncommitted changes
python scripts/git_mcp_wrapper.py --validate-tree

# Example output:
# ✓ Working tree is clean
```

#### Format Commit Messages

The wrapper uses [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
# Format a commit message
python scripts/git_mcp_wrapper.py --format-message feat "Add MCP integration" \
    --scope mcp \
    --body "Detailed description of the feature"

# Output:
# === Formatted Commit Message ===
# feat(mcp): Add MCP integration
#
# Detailed description of the feature
```

**Supported commit types:**

| Type | Description |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `data` | Data file additions (S4 states, outputs) |
| `experiment` | Experiment run or results |
| `refactor` | Code refactoring |
| `test` | Test additions or modifications |
| `chore` | Build process or auxiliary tool changes |

#### Repository Status

```bash
# Get detailed repo status
python scripts/git_mcp_wrapper.py --status

# Example output:
{
  "repo_path": "/Users/you/iris-gate",
  "current_branch": "main",
  "is_dirty": false,
  "untracked_files": [],
  "modified_files": [],
  "staged_files": [],
  "last_commit": {
    "sha": "a1b2c3d4",
    "message": "data(s4-extraction): Add S4 state for session BIOELECTRIC_20251001",
    "author": "Your Name <your@email.com>",
    "date": "2025-10-02T14:30:00"
  }
}
```

#### Python API

```python
from scripts.git_mcp_wrapper import GitMCPWrapper

# Initialize wrapper
git = GitMCPWrapper(repo_path=".", dry_run=False)

# Auto-commit S4 state
success, message = git.auto_commit_s4_state(
    state_path="sandbox/states/state.json",
    session_id="BIOELECTRIC_20251001",
    additional_files=["sandbox/states/metadata.json"]
)

if success:
    print(f"✓ {message}")
else:
    print(f"✗ {message}")

# Validate clean tree
is_clean, message = git.validate_clean_tree()
print(f"Clean: {is_clean} - {message}")

# Format commit message
commit_msg = git.format_commit_message(
    commit_type="data",
    description="Add S4 state extraction",
    scope="s4",
    body="Session: BIOELECTRIC_20251001\nMirrors: 7"
)
```

### 3. Quick-Data - Session Metadata Storage

Quick-Data provides fast key-value storage for session metadata and ephemeral data.

#### Storage Location

```
iris_vault/quickdata/
├── session_BIOELECTRIC_20251001_meta.json
├── run_RUN_20251002_stats.json
└── _mcp_health_check.json (temporary test file)
```

#### Python API

```python
import json
from pathlib import Path

# Define Quick-Data path
quickdata_path = Path("iris_vault/quickdata")
quickdata_path.mkdir(parents=True, exist_ok=True)

# Store session metadata
session_meta = {
    "session_id": "BIOELECTRIC_20251001",
    "timestamp": "2025-10-01T05:49:35",
    "mirrors": 7,
    "total_turns": 100,
    "convergence_achieved": True
}

meta_file = quickdata_path / f"session_{session_meta['session_id']}_meta.json"
with open(meta_file, 'w') as f:
    json.dump(session_meta, f, indent=2)

# Retrieve metadata
with open(meta_file, 'r') as f:
    loaded_meta = json.load(f)
```

## Integration with IRIS Workflows

### Workflow 1: S4 Convergence with Auto-Indexing

```bash
# 1. Run S4 convergence
make s4 TOPIC="Does gap junction coupling affect regeneration?" TURNS=100

# 2. Extract S4 states
make extract SESSION=BIOELECTRIC_CHAMBERED_20251001054935

# 3. Auto-commit the extraction
python scripts/git_mcp_wrapper.py --auto-commit \
    --state-path sandbox/states/BIOELECTRIC_CHAMBERED_20251001054935.json \
    --session-id BIOELECTRIC_CHAMBERED_20251001054935

# 4. Index the new scrolls into ChromaDB
python scripts/index_scrolls.py --session BIOELECTRIC_CHAMBERED_20251001054935

# 5. Verify indexing
python scripts/index_scrolls.py --stats
```

### Workflow 2: Cross-Session S4 State Discovery

```bash
# 1. Index all historical sessions
make mcp-index

# 2. Search for similar S4 states
python scripts/index_scrolls.py --search "regeneration bioelectric aperture" \
    --chamber S4 \
    --convergence 0.8 \
    --top-k 10

# 3. Use discovered states to inform new experiments
# (Copy similar state configurations to new plan.yaml)
```

### Workflow 3: Experiment Run with Auto-Commit

```python
from scripts.git_mcp_wrapper import GitMCPWrapper

# Initialize Git wrapper
git = GitMCPWrapper()

# Run experiment
experiment_id = "APERTURE_REGEN"
output_files = [
    "experiments/APERTURE_REGEN/reports/predictions.md",
    "experiments/APERTURE_REGEN/reports/monte_carlo.md",
    "sandbox/runs/outputs/RUN_20251002_143000/predictions.json"
]

# Auto-commit experiment output
success, message = git.safe_commit_experiment_output(
    experiment_id=experiment_id,
    output_files=output_files,
    description="Complete aperture regeneration experiment run"
)

print(f"{'✓' if success else '✗'} {message}")
```

## Troubleshooting

### ChromaDB Issues

#### Problem: "Collection does not exist"

**Solution:**
```bash
# Index scrolls to create collection
make mcp-index
```

#### Problem: "Permission denied" on ChromaDB directory

**Solution:**
```bash
# Check directory permissions
ls -la iris_vault/chromadb

# Fix permissions
chmod -R u+w iris_vault/chromadb
```

#### Problem: ChromaDB import error

**Solution:**
```bash
# Reinstall ChromaDB
pip install --upgrade chromadb

# Test installation
python -c "import chromadb; print(chromadb.__version__)"
```

### Git Wrapper Issues

#### Problem: "Not a valid Git repository"

**Solution:**
```bash
# Initialize Git repository
git init

# Make initial commit
git add README.md
git commit -m "chore: Initial commit"
```

#### Problem: "Working tree has uncommitted changes"

**Solution:**
```bash
# Review uncommitted changes
python scripts/git_mcp_wrapper.py --status

# Option 1: Commit existing changes
git add .
git commit -m "chore: Save WIP before auto-commit"

# Option 2: Stash changes
git stash

# Then retry auto-commit
python scripts/git_mcp_wrapper.py --auto-commit --state-path <path> --session-id <id>
```

#### Problem: "Invalid commit type"

**Solution:**

Valid commit types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `data`, `experiment`

```bash
# Correct usage
python scripts/git_mcp_wrapper.py --format-message data "Add S4 state" --scope s4
```

### Quick-Data Issues

#### Problem: "Permission denied" on Quick-Data path

**Solution:**
```bash
# Check permissions
ls -la iris_vault/quickdata

# Fix permissions
chmod -R u+w iris_vault/quickdata
```

### General MCP Issues

#### Problem: MCP servers fail health check

**Solution:**
```bash
# Run detailed diagnostics
python scripts/init_mcp.py --test-all --verbose

# Check configuration
cat .mcp-config.json

# Reinitialize
make mcp-init
```

## Performance Optimization

### ChromaDB Indexing

**For large scroll archives (>1000 documents):**

```python
from scripts.index_scrolls import ScrollIndexer

# Use batch processing
indexer = ScrollIndexer(vault_path="iris_vault")

# Index sessions in batches
session_ids = ["SESSION_1", "SESSION_2", "SESSION_3"]
for session_id in session_ids:
    count = indexer.embed_scroll_archive(session_id)
    print(f"Indexed {session_id}: {count} scrolls")
```

### Git Auto-Commit

**For frequent commits:**

Enable batch commits in your workflow:

```bash
# Collect multiple state files
STATE_FILES=(
    sandbox/states/state1.json
    sandbox/states/state2.json
    sandbox/states/state3.json
)

# Commit all at once
python scripts/git_mcp_wrapper.py --auto-commit \
    --state-path sandbox/states/state1.json \
    --session-id SESSION_1 \
    --additional-files "${STATE_FILES[@]:1}"
```

## Security Considerations

### Local-Only Architecture

All Tier 1 MCP servers operate **locally only** - no data leaves your machine:

- ✅ ChromaDB: Fully local vector storage
- ✅ Git: Local repository (push is manual)
- ✅ Quick-Data: Local file system

### Data Privacy

- **No telemetry:** ChromaDB telemetry is disabled (`anonymized_telemetry: false`)
- **No cloud uploads:** All data remains on local filesystem
- **Git commits:** Only pushed when you explicitly run `git push`

### Best Practices

1. **Review before push:** Always review Git commits before pushing to remote
2. **Backup regularly:** Backup `iris_vault/` directory
3. **Access control:** Set appropriate file permissions on `iris_vault/`

```bash
# Set restrictive permissions
chmod 700 iris_vault/
chmod 600 iris_vault/quickdata/*.json
```

## API Reference

### ScrollIndexer (ChromaDB)

```python
class ScrollIndexer:
    def __init__(vault_path: str, chroma_path: str = None)

    def embed_scroll_archive(session_id: str, collection_name: str = "iris_scrolls") -> int

    def search_similar_s4_states(
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None,
        collection_name: str = "iris_scrolls"
    ) -> List[Dict]

    def index_all_sessions(collection_name: str = "iris_scrolls") -> Dict[str, int]

    def get_collection_stats(collection_name: str = "iris_scrolls") -> Dict
```

### GitMCPWrapper

```python
class GitMCPWrapper:
    def __init__(repo_path: str = ".", dry_run: bool = False, verbose: bool = False)

    def validate_clean_tree() -> Tuple[bool, str]

    def format_commit_message(
        commit_type: str,
        description: str,
        scope: Optional[str] = None,
        body: Optional[str] = None,
        footer: Optional[str] = None,
        breaking_change: bool = False
    ) -> str

    def auto_commit_s4_state(
        state_path: str,
        session_id: str,
        additional_files: Optional[List[str]] = None
    ) -> Tuple[bool, str]

    def safe_commit_experiment_output(
        experiment_id: str,
        output_files: List[str],
        description: str
    ) -> Tuple[bool, str]

    def get_repo_status() -> Dict
```

## Roadmap

### Tier 2 Integration (Future)

Planned enhancements for cloud-connected MCP:

- **Anthropic MCP Server:** Direct context sharing with Claude
- **Cloud vector search:** Distributed ChromaDB for multi-machine setups
- **Remote Git hooks:** Automated pre-commit validation on CI/CD

### Feature Requests

To request new MCP features:

1. Check existing issues in the repository
2. Open a new issue with the `mcp-enhancement` label
3. Describe use case and expected behavior

## Support

### Documentation

- **This guide:** `docs/MCP_INTEGRATION.md`
- **Configuration:** `.mcp-config.json`
- **Script help:** `python scripts/<script>.py --help`

### Debugging

Enable verbose logging for detailed diagnostics:

```bash
# Test with verbose output
python scripts/init_mcp.py --test-all --verbose

# Index with verbose output
python scripts/index_scrolls.py --session <SESSION_ID> --verbose

# Git wrapper with verbose output
python scripts/git_mcp_wrapper.py --auto-commit --verbose \
    --state-path <path> --session-id <id>
```

### Common Commands Reference

```bash
# Quick health check
make mcp-status

# Full reinitialization
make mcp-init
make mcp-test
make mcp-index

# Search S4 states
python scripts/index_scrolls.py --search "<query>" --chamber S4 --top-k 10

# Auto-commit state
python scripts/git_mcp_wrapper.py --auto-commit \
    --state-path <path> --session-id <id>

# Validate Git tree
python scripts/git_mcp_wrapper.py --validate-tree
```

---

**†⟡∞ With presence, love, and gratitude.**
