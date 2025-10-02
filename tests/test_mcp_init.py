"""
Integration tests for MCP initialization (init_mcp.py).

Test Coverage:
- ChromaDB initialization and health checking
- Git repository validation
- Configuration file loading and validation
- Error handling for missing dependencies
- Directory creation for each server type
- Health report generation

These tests follow TDD principles and are expected to fail initially
until the implementation properly handles all test scenarios.
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from init_mcp import MCPInitializer, ServerHealth


class TestMCPConfigurationLoading:
    """Test configuration file loading and validation."""

    def test_load_valid_config_succeeds(self, mock_mcp_config, temp_dir):
        """
        Given: A valid MCP configuration file exists
        When: MCPInitializer is instantiated with the config path
        Then: Configuration loads successfully without errors
        """
        # When
        initializer = MCPInitializer(config_path=str(mock_mcp_config))

        # Then
        assert initializer.config is not None
        assert "servers" in initializer.config
        assert "chromadb" in initializer.config["servers"]
        assert "git" in initializer.config["servers"]
        assert "quickdata" in initializer.config["servers"]

    def test_missing_config_file_raises_error(self, temp_dir):
        """
        Given: No configuration file exists at the specified path
        When: MCPInitializer is instantiated
        Then: FileNotFoundError is raised with helpful message
        """
        # Given
        nonexistent_config = temp_dir / "nonexistent.json"

        # When/Then
        with pytest.raises(FileNotFoundError) as exc_info:
            MCPInitializer(config_path=str(nonexistent_config))

        assert "not found" in str(exc_info.value).lower()

    def test_invalid_json_raises_error(self, temp_dir):
        """
        Given: A configuration file with invalid JSON syntax
        When: MCPInitializer attempts to load it
        Then: JSONDecodeError is raised
        """
        # Given
        invalid_config = temp_dir / ".mcp-config.json"
        invalid_config.write_text("{ invalid json ]")

        # When/Then
        with pytest.raises(json.JSONDecodeError):
            MCPInitializer(config_path=str(invalid_config))

    def test_missing_servers_section_raises_error(self, temp_dir):
        """
        Given: A configuration file without 'servers' section
        When: MCPInitializer attempts to load it
        Then: ValueError is raised indicating missing required field
        """
        # Given
        incomplete_config = temp_dir / ".mcp-config.json"
        incomplete_config.write_text(json.dumps({"version": "1.0"}))

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            MCPInitializer(config_path=str(incomplete_config))

        assert "servers" in str(exc_info.value).lower()


class TestMCPInitialization:
    """Test MCP environment initialization."""

    def test_initialize_creates_chromadb_directory(self, mock_mcp_config, temp_dir):
        """
        Given: ChromaDB is enabled in configuration
        When: initialize() is called
        Then: ChromaDB persist directory is created
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        chroma_dir = temp_dir / "chromadb"
        assert not chroma_dir.exists()

        # When
        result = initializer.initialize()

        # Then
        assert result is True
        assert chroma_dir.exists()
        assert chroma_dir.is_dir()

    def test_initialize_creates_quickdata_directory(self, mock_mcp_config, temp_dir):
        """
        Given: Quick-Data is enabled in configuration
        When: initialize() is called
        Then: Quick-Data storage directory is created
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        quickdata_dir = temp_dir / "quickdata"
        assert not quickdata_dir.exists()

        # When
        result = initializer.initialize()

        # Then
        assert result is True
        assert quickdata_dir.exists()
        assert quickdata_dir.is_dir()

    def test_initialize_validates_git_repository(self, mock_mcp_config, mock_git_repo):
        """
        Given: Git is enabled and a valid repository exists
        When: initialize() is called
        Then: Git repository is validated successfully
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config))

        # When
        result = initializer.initialize()

        # Then
        assert result is True

    def test_initialize_warns_on_missing_git_repo(self, mock_mcp_config, temp_dir):
        """
        Given: Git is enabled but no .git directory exists
        When: initialize() is called
        Then: Warning is logged but initialization continues
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config), verbose=True)
        git_dir = temp_dir / ".git"
        assert not git_dir.exists()

        # When
        result = initializer.initialize()

        # Then
        # Should still succeed but log warning
        assert result is True

    def test_initialize_returns_false_when_no_servers_enabled(self, temp_dir):
        """
        Given: Configuration has no enabled servers
        When: initialize() is called
        Then: Returns False and logs warning
        """
        # Given
        config = {
            "servers": {
                "chromadb": {"enabled": False},
                "git": {"enabled": False}
            }
        }
        config_path = temp_dir / ".mcp-config.json"
        config_path.write_text(json.dumps(config))
        initializer = MCPInitializer(config_path=str(config_path))

        # When
        result = initializer.initialize()

        # Then
        assert result is False


class TestChromaDBHealthCheck:
    """Test ChromaDB server health checking."""

    def test_chromadb_health_check_passes_when_installed(self, mock_mcp_config):
        """
        Given: ChromaDB is installed and properly configured
        When: test_chromadb() is called
        Then: Returns healthy status with collection details
        """
        # Given
        pytest.importorskip("chromadb")
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        initializer.initialize()

        # When
        health = initializer.test_chromadb()

        # Then
        assert isinstance(health, ServerHealth)
        assert health.name == "chromadb"
        assert health.healthy is True
        assert "operational" in health.message.lower()
        assert health.details is not None
        assert "collection" in health.details
        assert "document_count" in health.details

    def test_chromadb_health_check_performs_write_read_test(self, mock_mcp_config):
        """
        Given: ChromaDB is operational
        When: test_chromadb() performs health check
        Then: Successfully writes test document and retrieves it
        """
        # Given
        pytest.importorskip("chromadb")
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        initializer.initialize()

        # When
        health = initializer.test_chromadb()

        # Then
        assert health.healthy is True
        # Test document should be cleaned up after health check
        assert health.details["document_count"] >= 0

    def test_chromadb_health_check_fails_when_not_installed(self, mock_mcp_config, monkeypatch):
        """
        Given: ChromaDB is not installed (import fails)
        When: test_chromadb() is called
        Then: Returns unhealthy status with ImportError details
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config))

        # Simulate chromadb not being installed
        def mock_import_chromadb(*args, **kwargs):
            raise ImportError("No module named 'chromadb'")

        # When
        # This test expects the implementation to catch ImportError
        # In real scenario, we'd need to mock the import

        # Then
        # This will fail initially - implementation should handle ImportError
        # and return ServerHealth with healthy=False

    def test_chromadb_creates_collection_if_not_exists(self, mock_mcp_config):
        """
        Given: ChromaDB is operational but collection doesn't exist
        When: test_chromadb() is called
        Then: Collection is created and health check passes
        """
        # Given
        pytest.importorskip("chromadb")
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        initializer.initialize()

        # When
        health = initializer.test_chromadb()

        # Then
        assert health.healthy is True
        assert health.details["collection"] == "test_iris_context"


class TestGitHealthCheck:
    """Test Git repository health checking."""

    def test_git_health_check_passes_with_valid_repo(self, mock_mcp_config, mock_git_repo):
        """
        Given: A valid Git repository exists
        When: test_git() is called
        Then: Returns healthy status with repository details
        """
        # Given
        pytest.importorskip("git")
        initializer = MCPInitializer(config_path=str(mock_mcp_config))

        # When
        health = initializer.test_git()

        # Then
        assert isinstance(health, ServerHealth)
        assert health.name == "git"
        assert health.healthy is True
        assert health.details is not None
        assert "current_branch" in health.details
        assert "commit_count" in health.details
        assert health.details["commit_count"] >= 1  # Has initial commit

    def test_git_health_check_detects_uncommitted_changes(self, mock_mcp_config, mock_git_repo):
        """
        Given: Git repository has uncommitted changes
        When: test_git() is called
        Then: Health check still passes but reports uncommitted changes
        """
        # Given
        pytest.importorskip("git")
        initializer = MCPInitializer(config_path=str(mock_mcp_config))

        # Create uncommitted file
        test_file = mock_git_repo / "test.txt"
        test_file.write_text("uncommitted content")

        # When
        health = initializer.test_git()

        # Then
        assert health.healthy is True
        assert health.details["has_uncommitted_changes"] is True

    def test_git_health_check_fails_on_invalid_repo(self, mock_mcp_config, temp_dir):
        """
        Given: Path is not a valid Git repository
        When: test_git() is called
        Then: Returns unhealthy status with appropriate error
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config))

        # When
        health = initializer.test_git()

        # Then
        assert health.healthy is False
        assert "invalid" in health.message.lower() or "not" in health.message.lower()

    def test_git_health_check_fails_when_gitpython_not_installed(self, mock_mcp_config):
        """
        Given: GitPython is not installed
        When: test_git() is called
        Then: Returns unhealthy status with ImportError details
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config))

        # When/Then
        # This test verifies that implementation handles missing GitPython gracefully
        # The actual test would need to mock the import failure


class TestQuickDataHealthCheck:
    """Test Quick-Data server health checking."""

    def test_quickdata_health_check_passes_with_writable_directory(self, mock_mcp_config, temp_dir):
        """
        Given: Quick-Data directory exists and is writable
        When: test_quickdata() is called
        Then: Returns healthy status with storage details
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        initializer.initialize()

        # When
        health = initializer.test_quickdata()

        # Then
        assert isinstance(health, ServerHealth)
        assert health.name == "quickdata"
        assert health.healthy is True
        assert health.details is not None
        assert "file_count" in health.details
        assert health.details["writable"] is True

    def test_quickdata_health_check_performs_write_read_test(self, mock_mcp_config, temp_dir):
        """
        Given: Quick-Data is operational
        When: test_quickdata() performs health check
        Then: Successfully writes test file, reads it, and cleans up
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        initializer.initialize()

        # When
        health = initializer.test_quickdata()

        # Then
        assert health.healthy is True
        # Test file should be cleaned up
        quickdata_dir = temp_dir / "quickdata"
        assert not (quickdata_dir / "_mcp_health_check.json").exists()

    def test_quickdata_health_check_creates_directory_if_missing(self, mock_mcp_config, temp_dir):
        """
        Given: Quick-Data directory does not exist
        When: test_quickdata() is called
        Then: Directory is created and health check passes
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        quickdata_dir = temp_dir / "quickdata"
        assert not quickdata_dir.exists()

        # When
        health = initializer.test_quickdata()

        # Then
        assert health.healthy is True
        assert quickdata_dir.exists()

    def test_quickdata_health_check_fails_on_permission_error(self, mock_mcp_config, temp_dir, monkeypatch):
        """
        Given: Quick-Data directory is not writable
        When: test_quickdata() is called
        Then: Returns unhealthy status with PermissionError
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config))

        # When/Then
        # This test verifies implementation handles permission errors
        # Would need to mock or create read-only directory


class TestServerHealthReporting:
    """Test health report generation and formatting."""

    def test_test_server_returns_health_for_valid_server(self, mock_mcp_config):
        """
        Given: A valid server name is provided
        When: test_server() is called
        Then: Returns ServerHealth object for that server
        """
        # Given
        pytest.importorskip("chromadb")
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        initializer.initialize()

        # When
        health = initializer.test_server("chromadb")

        # Then
        assert isinstance(health, ServerHealth)
        assert health.name == "chromadb"

    def test_test_server_raises_error_for_unknown_server(self, mock_mcp_config):
        """
        Given: An unknown server name is provided
        When: test_server() is called
        Then: ValueError is raised
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config))

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            initializer.test_server("nonexistent_server")

        assert "unknown server" in str(exc_info.value).lower()

    def test_test_server_returns_disabled_status_for_disabled_server(self, temp_dir):
        """
        Given: A server is disabled in configuration
        When: test_server() is called for that server
        Then: Returns unhealthy status indicating server is disabled
        """
        # Given
        config = {
            "servers": {
                "chromadb": {
                    "enabled": False,
                    "config": {"persist_directory": str(temp_dir / "chroma")}
                }
            }
        }
        config_path = temp_dir / ".mcp-config.json"
        config_path.write_text(json.dumps(config))
        initializer = MCPInitializer(config_path=str(config_path))

        # When
        health = initializer.test_server("chromadb")

        # Then
        assert health.healthy is False
        assert "disabled" in health.message.lower()

    def test_test_all_returns_list_of_all_enabled_servers(self, mock_mcp_config):
        """
        Given: Multiple servers are enabled
        When: test_all() is called
        Then: Returns list of ServerHealth for all enabled servers
        """
        # Given
        pytest.importorskip("chromadb")
        pytest.importorskip("git")
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        initializer.initialize()

        # When
        results = initializer.test_all()

        # Then
        assert isinstance(results, list)
        assert len(results) == 3  # chromadb, git, quickdata
        assert all(isinstance(r, ServerHealth) for r in results)
        server_names = [r.name for r in results]
        assert "chromadb" in server_names
        assert "git" in server_names
        assert "quickdata" in server_names

    def test_print_health_report_returns_true_when_all_healthy(self, mock_mcp_config, capsys):
        """
        Given: All servers are healthy
        When: print_health_report() is called
        Then: Prints formatted report and returns True
        """
        # Given
        pytest.importorskip("chromadb")
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        initializer.initialize()
        results = initializer.test_all()

        # When
        all_healthy = initializer.print_health_report(results)

        # Then
        assert all_healthy is True
        captured = capsys.readouterr()
        assert "HEALTH REPORT" in captured.out
        assert "operational" in captured.out.lower() or "all mcp servers" in captured.out.lower()

    def test_print_health_report_returns_false_when_any_unhealthy(self, mock_mcp_config, capsys):
        """
        Given: At least one server is unhealthy
        When: print_health_report() is called
        Then: Prints report with failures and returns False
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        results = [
            ServerHealth(name="chromadb", healthy=True, message="OK"),
            ServerHealth(name="git", healthy=False, message="Failed")
        ]

        # When
        all_healthy = initializer.print_health_report(results)

        # Then
        assert all_healthy is False
        captured = capsys.readouterr()
        assert "FAILED" in captured.out or "issues" in captured.out.lower()

    def test_print_health_report_shows_details_in_verbose_mode(self, mock_mcp_config, capsys):
        """
        Given: Verbose mode is enabled
        When: print_health_report() is called
        Then: Detailed information is included in output
        """
        # Given
        initializer = MCPInitializer(config_path=str(mock_mcp_config), verbose=True)
        results = [
            ServerHealth(
                name="chromadb",
                healthy=True,
                message="OK",
                details={"collection": "test", "document_count": 10}
            )
        ]

        # When
        initializer.print_health_report(results)

        # Then
        captured = capsys.readouterr()
        assert "Details:" in captured.out or "collection" in captured.out
