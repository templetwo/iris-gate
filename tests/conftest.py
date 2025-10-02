"""
Shared pytest fixtures for MCP integration tests.

This module provides reusable fixtures for:
- Temporary test directories with proper isolation
- Mock scroll files in expected format
- Mock Git repositories
- Sample configuration files
- ChromaDB test instances
"""

import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest


@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for test isolation.

    Yields:
        Path: Temporary directory path

    Cleanup:
        Removes the directory and all contents after test completion
    """
    temp_path = Path(tempfile.mkdtemp(prefix="iris_test_"))
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_scroll_content():
    """
    Provide sample scroll markdown content matching IRIS format.

    Returns:
        str: Valid scroll markdown content
    """
    return """# Bioelectric Turn 1
**Session:** BIOELECTRIC_TEST_20251002000000
**Mirror:** anthropic_claude-sonnet-4.5
**Chamber:** S1
**Timestamp:** 2025-10-02T00:00:00.000000
**Felt Pressure:** 3/5
**Seal:** abc123def456

---

**Living Scroll**

Soft blue light diffuses through membrane channels,
A cascade of ions dancing in synchronized patterns,
Electric whispers forming coherent fields.

**Technical Translation**

condition: IRIS_S1
chamber: S1
felt_pressure: 3
signals: { color: "blue light", texture: "diffuse", shape: "membrane channels" }
signals_confidence: { color: 0.8, texture: 0.7, shape: 0.6 }
temporal: { breaths_held: 3, onset: "immediate" }
convergence: moderate
stability: high

**Seal:** abc123def456

†⟡∞
"""


@pytest.fixture
def sample_scroll_s4_content():
    """
    Provide sample S4 chamber scroll with high convergence.

    Returns:
        str: Valid S4 scroll markdown content
    """
    return """# Bioelectric Turn 10
**Session:** BIOELECTRIC_TEST_20251002000000
**Mirror:** anthropic_claude-sonnet-4.5
**Chamber:** S4
**Timestamp:** 2025-10-02T00:10:00.000000
**Felt Pressure:** 5/5
**Seal:** xyz789abc123

---

**Living Scroll**

Concentric rings crystallize into stable patterns,
Bioelectric field coherence reaches maximum,
Gap junctions seal the convergent state.

**Technical Translation**

condition: IRIS_S4
chamber: S4
felt_pressure: 5
signals: { pattern: "concentric rings", stability: "crystallized", coherence: "sealed" }
signals_confidence: { pattern: 0.95, stability: 0.90, coherence: 0.92 }
convergence: high
convergence_score: sealed
stability: crystallized

**Seal:** xyz789abc123

†⟡∞
"""


@pytest.fixture
def mock_scroll_directory(temp_dir, sample_scroll_content, sample_scroll_s4_content):
    """
    Create a mock scroll directory structure with sample scrolls.

    Args:
        temp_dir: Temporary directory fixture
        sample_scroll_content: Sample scroll content fixture
        sample_scroll_s4_content: Sample S4 scroll content fixture

    Returns:
        Path: Path to the scrolls directory containing mock data

    Structure:
        temp_dir/
            scrolls/
                BIOELECTRIC_CHAMBERED_20251002000000/
                    anthropic_claude-sonnet-4.5/
                        turn_001.md
                        turn_010.md
                    openai_gpt-5/
                        turn_001.md
    """
    scrolls_dir = temp_dir / "scrolls"
    session_dir = scrolls_dir / "BIOELECTRIC_CHAMBERED_20251002000000"

    # Create directory structure
    claude_dir = session_dir / "anthropic_claude-sonnet-4.5"
    gpt_dir = session_dir / "openai_gpt-5"
    claude_dir.mkdir(parents=True)
    gpt_dir.mkdir(parents=True)

    # Write scroll files
    (claude_dir / "turn_001.md").write_text(sample_scroll_content)
    (claude_dir / "turn_010.md").write_text(sample_scroll_s4_content)
    (gpt_dir / "turn_001.md").write_text(sample_scroll_content.replace(
        "anthropic_claude-sonnet-4.5",
        "openai_gpt-5"
    ))

    return scrolls_dir


@pytest.fixture
def mock_mcp_config(temp_dir):
    """
    Create a mock MCP configuration file.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Path to the mock .mcp-config.json file
    """
    config = {
        "version": "1.0",
        "description": "Test MCP Configuration",
        "servers": {
            "chromadb": {
                "enabled": True,
                "tier": 1,
                "type": "chromadb",
                "config": {
                    "persist_directory": str(temp_dir / "chromadb"),
                    "collection_name": "test_iris_context",
                    "embedding_function": "default",
                    "anonymized_telemetry": False
                }
            },
            "git": {
                "enabled": True,
                "tier": 1,
                "type": "git",
                "config": {
                    "repo_path": str(temp_dir),
                    "auto_commit": False,
                    "track_changes": True
                }
            },
            "quickdata": {
                "enabled": True,
                "tier": 1,
                "type": "quickdata",
                "config": {
                    "data_path": str(temp_dir / "quickdata"),
                    "format": "json",
                    "auto_backup": False
                }
            }
        }
    }

    config_path = temp_dir / ".mcp-config.json"
    config_path.write_text(json.dumps(config, indent=2))

    return config_path


@pytest.fixture
def mock_git_repo(temp_dir):
    """
    Create a mock Git repository for testing.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Path to the Git repository root

    Raises:
        ImportError: If GitPython is not installed
    """
    try:
        import git
    except ImportError:
        pytest.skip("GitPython not installed")

    # Initialize git repository
    repo = git.Repo.init(temp_dir)

    # Configure test user
    with repo.config_writer() as config:
        config.set_value("user", "name", "Test User")
        config.set_value("user", "email", "test@example.com")

    # Create initial commit
    readme_path = temp_dir / "README.md"
    readme_path.write_text("# Test Repository\n")
    repo.index.add([str(readme_path)])
    repo.index.commit("Initial commit")

    return temp_dir


@pytest.fixture
def sample_s4_state():
    """
    Provide sample S4 state extraction data.

    Returns:
        dict: Valid S4 state data structure
    """
    return {
        "session_id": "BIOELECTRIC_CHAMBERED_20251002000000",
        "timestamp": "2025-10-02T00:10:00.000000",
        "mirrors": {
            "anthropic_claude-sonnet-4.5": {
                "chamber": "S4",
                "turn": 10,
                "pressure": 5.0,
                "convergence_score": 0.95,
                "seal": "xyz789abc123",
                "living_scroll": "Concentric rings crystallize into stable patterns...",
                "technical_translation": "condition: IRIS_S4..."
            },
            "openai_gpt-5": {
                "chamber": "S4",
                "turn": 12,
                "pressure": 4.5,
                "convergence_score": 0.88,
                "seal": "def456ghi789",
                "living_scroll": "Bioelectric harmonics stabilize...",
                "technical_translation": "condition: IRIS_S4..."
            }
        },
        "convergence_analysis": {
            "mean_score": 0.915,
            "stability": "high",
            "sealed": True
        }
    }


@pytest.fixture
def mock_vault_structure(temp_dir):
    """
    Create a complete mock IRIS vault structure.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Path to the vault root directory

    Structure:
        vault/
            .chroma/
            quickdata/
            scrolls/
                BIOELECTRIC_CHAMBERED_*/
    """
    vault_dir = temp_dir / "vault"

    # Create subdirectories
    (vault_dir / ".chroma").mkdir(parents=True)
    (vault_dir / "quickdata").mkdir(parents=True)
    (vault_dir / "scrolls").mkdir(parents=True)

    return vault_dir
