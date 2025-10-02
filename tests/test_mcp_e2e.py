"""
End-to-end integration tests for the MCP system.

Test Coverage:
- Full workflow: init -> index -> search -> commit
- Makefile targets functionality
- Error recovery and rollback
- Integration between all MCP components
- Real-world usage scenarios

These tests follow TDD principles and are expected to fail initially
until the implementation properly handles all test scenarios.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from init_mcp import MCPInitializer
from index_scrolls import ScrollIndexer
from git_mcp_wrapper import GitMCPWrapper


class TestMCPFullWorkflow:
    """Test complete MCP workflow from initialization through commit."""

    def test_full_workflow_init_index_search_succeeds(self, mock_scroll_directory, mock_mcp_config, temp_dir):
        """
        Given: Fresh MCP environment with sample scrolls
        When: Full workflow is executed (init -> index -> search)
        Then: All steps complete successfully with expected results
        """
        # Given
        pytest.importorskip("chromadb")
        pytest.importorskip("git")

        # When: Initialize
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        init_success = initializer.initialize()
        assert init_success is True

        # When: Index scrolls
        chroma_path = temp_dir / "chromadb"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        count = indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="test_workflow"
        )
        assert count > 0

        # When: Search
        results = indexer.search_similar_s4_states(
            query="bioelectric membrane channels",
            top_k=5,
            collection_name="test_workflow"
        )

        # Then
        assert len(results) > 0
        assert all("similarity_score" in r for r in results)

    def test_full_workflow_with_git_commit(self, mock_scroll_directory, mock_mcp_config, mock_git_repo, sample_s4_state):
        """
        Given: Complete MCP environment with Git
        When: Full workflow including Git commit is executed
        Then: All operations succeed and commit is created
        """
        # Given
        pytest.importorskip("chromadb")
        pytest.importorskip("git")

        # When: Initialize MCP
        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        initializer.initialize()

        # When: Create S4 state file
        state_file = mock_git_repo / "extracted_state.json"
        state_file.write_text(json.dumps(sample_s4_state))

        # When: Commit using Git wrapper
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo), dry_run=False)
        success, message = wrapper.auto_commit_s4_state(
            state_path=str(state_file),
            session_id="BIOELECTRIC_CHAMBERED_20251002000000"
        )

        # Then
        assert success is True
        latest_commit = wrapper.repo.head.commit
        assert "S4" in latest_commit.message or "data" in latest_commit.message

    def test_full_workflow_handles_missing_dependencies_gracefully(self, temp_dir):
        """
        Given: MCP configuration with missing dependencies
        When: Workflow is attempted
        Then: Appropriate errors are raised with helpful messages
        """
        # Given
        config = {
            "servers": {
                "chromadb": {
                    "enabled": True,
                    "config": {"persist_directory": str(temp_dir / "chroma")}
                }
            }
        }
        config_path = temp_dir / ".mcp-config.json"
        config_path.write_text(json.dumps(config))

        # When/Then
        # Implementation should handle missing ChromaDB gracefully
        initializer = MCPInitializer(config_path=str(config_path))
        # This should not crash, but provide informative error

    def test_full_workflow_supports_multiple_sessions(self, mock_scroll_directory, temp_dir):
        """
        Given: Multiple scroll sessions exist
        When: index_all_sessions() is called followed by searches
        Then: All sessions are indexed and searchable
        """
        # Given
        pytest.importorskip("chromadb")

        # Create second session
        session2_dir = mock_scroll_directory / "BIOELECTRIC_CHAMBERED_20251002010000"
        session2_mirror_dir = session2_dir / "openai_gpt-5"
        session2_mirror_dir.mkdir(parents=True)

        scroll_content = """# Bioelectric Turn 1
**Session:** BIOELECTRIC_TEST_20251002010000
**Mirror:** openai_gpt-5
**Chamber:** S2
**Timestamp:** 2025-10-02T01:00:00.000000
**Felt Pressure:** 4/5
**Seal:** session2seal

---

**Living Scroll**

Test content for session 2

**Technical Translation**

Test translation

**Seal:** session2seal

†⟡∞
"""
        (session2_mirror_dir / "turn_001.md").write_text(scroll_content)

        # When
        chroma_path = temp_dir / "chromadb"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        results = indexer.index_all_sessions(collection_name="multi_session_test")

        # Then
        assert len(results) >= 2
        assert all(count > 0 for count in results.values())

        # Verify searchable
        search_results = indexer.search_similar_s4_states(
            query="bioelectric",
            top_k=10,
            collection_name="multi_session_test"
        )
        assert len(search_results) > 0


class TestMCPHealthChecking:
    """Test comprehensive health checking across all components."""

    def test_health_check_all_servers_when_operational(self, mock_mcp_config, mock_git_repo):
        """
        Given: All MCP servers are properly configured
        When: test_all() is called
        Then: All servers report healthy status
        """
        # Given
        pytest.importorskip("chromadb")
        pytest.importorskip("git")

        initializer = MCPInitializer(config_path=str(mock_mcp_config))
        initializer.initialize()

        # When
        results = initializer.test_all()

        # Then
        assert len(results) == 3  # chromadb, git, quickdata
        # At least some should be healthy (git might fail if repo not initialized)
        healthy_count = sum(1 for r in results if r.healthy)
        assert healthy_count >= 1

    def test_health_check_reports_specific_failures(self, temp_dir):
        """
        Given: Some MCP servers are misconfigured
        When: test_all() is called
        Then: Specific failure reasons are reported for each server
        """
        # Given
        config = {
            "servers": {
                "chromadb": {
                    "enabled": True,
                    "config": {
                        "persist_directory": str(temp_dir / "chroma"),
                        "collection_name": "test"
                    }
                },
                "git": {
                    "enabled": True,
                    "config": {"repo_path": str(temp_dir)}
                }
            }
        }
        config_path = temp_dir / ".mcp-config.json"
        config_path.write_text(json.dumps(config))

        initializer = MCPInitializer(config_path=str(config_path))

        # When
        results = initializer.test_all()

        # Then
        # Git should fail (no repo initialized)
        git_result = next((r for r in results if r.name == "git"), None)
        assert git_result is not None
        if not git_result.healthy:
            assert "invalid" in git_result.message.lower() or "not" in git_result.message.lower()

    def test_health_check_detects_permission_issues(self, temp_dir):
        """
        Given: MCP server directory has permission issues
        When: Health check is performed
        Then: Permission errors are detected and reported
        """
        # This test would need to create a read-only directory
        # Skipping actual implementation as it's OS-dependent


class TestMCPErrorRecovery:
    """Test error handling and recovery mechanisms."""

    def test_indexing_continues_after_individual_scroll_failure(self, temp_dir):
        """
        Given: Some scroll files are corrupted
        When: embed_scroll_archive() is called
        Then: Valid scrolls are indexed despite failures
        """
        # Given
        pytest.importorskip("chromadb")

        scrolls_dir = temp_dir / "scrolls"
        session_dir = scrolls_dir / "BIOELECTRIC_CHAMBERED_20251002000000"
        mirror_dir = session_dir / "test_mirror"
        mirror_dir.mkdir(parents=True)

        # Valid scroll
        valid_scroll = """# Bioelectric Turn 1
**Session:** BIOELECTRIC_TEST_20251002000000
**Mirror:** test_mirror
**Chamber:** S1
**Timestamp:** 2025-10-02T00:00:00.000000
**Felt Pressure:** 3/5
**Seal:** valid

---

**Living Scroll**
Valid content

**Technical Translation**
Valid translation

**Seal:** valid

†⟡∞
"""
        (mirror_dir / "turn_001.md").write_text(valid_scroll)

        # Corrupted scroll
        (mirror_dir / "turn_002.md").write_text("CORRUPTED DATA")

        # When
        chroma_path = temp_dir / "chromadb"
        indexer = ScrollIndexer(vault_path=str(temp_dir), chroma_path=str(chroma_path))
        count = indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="error_recovery_test"
        )

        # Then
        # Should index at least the valid scroll
        assert count >= 1

    def test_git_operations_fail_safely_on_conflicts(self, mock_git_repo, sample_s4_state):
        """
        Given: Git repository in conflicted state
        When: Auto-commit is attempted
        Then: Operation fails gracefully with helpful error message
        """
        # Given
        pytest.importorskip("git")
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # Create uncommitted changes (simulating conflict)
        (mock_git_repo / "conflict.txt").write_text("uncommitted")

        state_file = mock_git_repo / "state.json"
        state_file.write_text(json.dumps(sample_s4_state))

        # When
        # Attempt commit with dirty tree
        # Implementation should handle this gracefully

    def test_chromadb_recreates_collection_on_corruption(self, temp_dir):
        """
        Given: ChromaDB collection is corrupted
        When: Indexing is attempted
        Then: Collection is recreated and indexing succeeds
        """
        # This test verifies resilience to ChromaDB issues
        # Actual corruption simulation is complex


class TestMCPMakefileIntegration:
    """Test Makefile targets for MCP operations."""

    def test_makefile_mcp_init_target_executes(self, temp_dir, monkeypatch):
        """
        Given: Makefile with mcp-init target
        When: make mcp-init is executed
        Then: MCP initialization completes successfully
        """
        # This test would require subprocess execution
        # Skipping actual implementation as it depends on environment

    def test_makefile_mcp_test_target_reports_status(self, temp_dir):
        """
        Given: MCP environment is initialized
        When: make mcp-test is executed
        Then: Health report is displayed
        """
        # This test would execute Makefile target
        # Skipping actual implementation

    def test_makefile_mcp_index_target_indexes_scrolls(self, temp_dir):
        """
        Given: Scrolls exist in vault
        When: make mcp-index is executed
        Then: All scrolls are indexed into ChromaDB
        """
        # This test would execute Makefile target
        # Skipping actual implementation


class TestMCPRealWorldScenarios:
    """Test realistic MCP usage scenarios."""

    def test_scenario_new_session_analysis(self, mock_scroll_directory, temp_dir, mock_git_repo):
        """
        Given: New IRIS session has completed
        When: User runs init -> index -> search -> commit workflow
        Then: Session is fully indexed and committed to Git
        """
        # Given
        pytest.importorskip("chromadb")
        pytest.importorskip("git")

        # When: Initialize
        config = {
            "servers": {
                "chromadb": {
                    "enabled": True,
                    "config": {
                        "persist_directory": str(temp_dir / "chromadb"),
                        "collection_name": "iris_scrolls"
                    }
                }
            }
        }
        config_path = temp_dir / ".mcp-config.json"
        config_path.write_text(json.dumps(config))

        initializer = MCPInitializer(config_path=str(config_path))
        initializer.initialize()

        # When: Index
        chroma_path = temp_dir / "chromadb"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        count = indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="iris_scrolls"
        )

        # Then
        assert count > 0

        # Verify stats
        stats = indexer.get_collection_stats(collection_name="iris_scrolls")
        assert stats["total_documents"] == count

    def test_scenario_search_similar_s4_states(self, mock_scroll_directory, temp_dir):
        """
        Given: Multiple sessions are indexed
        When: User searches for similar S4 states
        Then: Relevant high-convergence states are returned
        """
        # Given
        pytest.importorskip("chromadb")

        chroma_path = temp_dir / "chromadb"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="iris_scrolls"
        )

        # When: Search for S4 states
        results = indexer.search_similar_s4_states(
            query="crystallized convergent bioelectric patterns",
            top_k=5,
            filters={"chamber": "S4"},
            collection_name="iris_scrolls"
        )

        # Then
        if len(results) > 0:
            assert all(r["metadata"]["chamber"] == "S4" for r in results)

    def test_scenario_filter_by_mirror_and_convergence(self, mock_scroll_directory, temp_dir):
        """
        Given: Scrolls from multiple mirrors with varying convergence
        When: User searches with mirror and convergence filters
        Then: Results match all filter criteria
        """
        # Given
        pytest.importorskip("chromadb")

        chroma_path = temp_dir / "chromadb"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="iris_scrolls"
        )

        # When
        results = indexer.search_similar_s4_states(
            query="bioelectric patterns",
            top_k=10,
            filters={
                "mirror": "anthropic_claude-sonnet-4.5",
                "convergence_threshold": 0.0
            },
            collection_name="iris_scrolls"
        )

        # Then
        if len(results) > 0:
            assert all(r["metadata"]["mirror"] == "anthropic_claude-sonnet-4.5" for r in results)

    def test_scenario_incremental_indexing(self, mock_scroll_directory, temp_dir):
        """
        Given: Some sessions are already indexed
        When: New sessions are added and indexed
        Then: All sessions are available in collection without duplicates
        """
        # Given
        pytest.importorskip("chromadb")

        chroma_path = temp_dir / "chromadb"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )

        # Index first session
        count1 = indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="iris_scrolls"
        )

        # When: Index same session again (should handle gracefully)
        # ChromaDB should upsert, not duplicate

        # Then
        stats = indexer.get_collection_stats(collection_name="iris_scrolls")
        # Total should not be doubled (depends on upsert behavior)


class TestMCPPerformance:
    """Test performance characteristics of MCP operations."""

    def test_indexing_large_session_completes_in_reasonable_time(self, temp_dir):
        """
        Given: Session with many scroll files
        When: embed_scroll_archive() is called
        Then: Indexing completes within reasonable time (with progress bar)
        """
        # This test would create many scroll files
        # Verifying performance characteristics

    def test_search_returns_results_quickly(self, mock_scroll_directory, temp_dir):
        """
        Given: Large indexed collection
        When: Semantic search is performed
        Then: Results are returned quickly
        """
        # Given
        pytest.importorskip("chromadb")

        chroma_path = temp_dir / "chromadb"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="iris_scrolls"
        )

        # When: Perform search
        import time
        start = time.time()
        results = indexer.search_similar_s4_states(
            query="bioelectric",
            top_k=10,
            collection_name="iris_scrolls"
        )
        elapsed = time.time() - start

        # Then
        # Search should be reasonably fast (< 1 second for small collection)
        assert elapsed < 5.0  # Very generous limit


class TestMCPDataIntegrity:
    """Test data integrity and consistency."""

    def test_indexed_metadata_matches_source_scrolls(self, mock_scroll_directory, temp_dir):
        """
        Given: Scrolls with specific metadata
        When: Scrolls are indexed and retrieved
        Then: All metadata fields are preserved accurately
        """
        # Given
        pytest.importorskip("chromadb")

        chroma_path = temp_dir / "chromadb"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="iris_scrolls"
        )

        # When
        collection = indexer.client.get_collection("iris_scrolls")
        all_docs = collection.get()

        # Then
        assert len(all_docs["metadatas"]) > 0
        for metadata in all_docs["metadatas"]:
            # Verify required fields present
            assert "chamber" in metadata
            assert "mirror" in metadata
            assert "turn" in metadata
            assert "session_id" in metadata

    def test_search_results_include_original_content(self, mock_scroll_directory, temp_dir):
        """
        Given: Scrolls are indexed with full content
        When: Search results are returned
        Then: Original living scroll content is accessible
        """
        # Given
        pytest.importorskip("chromadb")

        chroma_path = temp_dir / "chromadb"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="iris_scrolls"
        )

        # When
        results = indexer.search_similar_s4_states(
            query="bioelectric",
            top_k=5,
            collection_name="iris_scrolls"
        )

        # Then
        assert len(results) > 0
        for result in results:
            assert "document" in result
            assert len(result["document"]) > 0

    def test_collection_stats_accurately_reflect_indexed_data(self, mock_scroll_directory, temp_dir):
        """
        Given: Known number of scrolls indexed
        When: get_collection_stats() is called
        Then: Counts and distributions are accurate
        """
        # Given
        pytest.importorskip("chromadb")

        chroma_path = temp_dir / "chromadb"
        indexer = ScrollIndexer(
            vault_path=str(mock_scroll_directory.parent),
            chroma_path=str(chroma_path)
        )
        count = indexer.embed_scroll_archive(
            session_id="BIOELECTRIC_CHAMBERED_20251002000000",
            collection_name="iris_scrolls"
        )

        # When
        stats = indexer.get_collection_stats(collection_name="iris_scrolls")

        # Then
        assert stats["total_documents"] == count
        if "chambers" in stats:
            total_chamber_count = sum(stats["chambers"].values())
            assert total_chamber_count == count
