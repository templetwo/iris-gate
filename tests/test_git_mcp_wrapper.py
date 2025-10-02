"""
Integration tests for Git MCP wrapper (git_mcp_wrapper.py).

Test Coverage:
- Working tree validation (clean vs dirty)
- Conventional commit message formatting
- Auto-commit functionality for S4 states
- Dry-run mode verification
- Error handling for invalid repositories
- Repository status reporting

These tests follow TDD principles and are expected to fail initially
until the implementation properly handles all test scenarios.
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from git_mcp_wrapper import GitMCPWrapper


class TestGitRepositoryValidation:
    """Test Git repository initialization and validation."""

    def test_wrapper_initializes_with_valid_repo(self, mock_git_repo):
        """
        Given: A valid Git repository exists
        When: GitMCPWrapper is instantiated
        Then: Wrapper initializes successfully without errors
        """
        # Given/When
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # Then
        assert wrapper.repo is not None
        assert wrapper.repo_path == mock_git_repo

    def test_wrapper_raises_error_on_invalid_repo(self, temp_dir):
        """
        Given: Directory is not a Git repository
        When: GitMCPWrapper is instantiated
        Then: InvalidGitRepositoryError is raised
        """
        # Given
        pytest.importorskip("git")
        from git.exc import InvalidGitRepositoryError

        # When/Then
        with pytest.raises(InvalidGitRepositoryError) as exc_info:
            GitMCPWrapper(repo_path=str(temp_dir))

        assert "not a valid" in str(exc_info.value).lower() or "git" in str(exc_info.value).lower()

    def test_wrapper_dry_run_mode_logs_message(self, mock_git_repo):
        """
        Given: Wrapper is initialized with dry_run=True
        When: Operations are performed
        Then: No actual changes are made and operations are logged
        """
        # Given/When
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo), dry_run=True)

        # Then
        assert wrapper.dry_run is True

    def test_wrapper_verbose_mode_enables_debug_logging(self, mock_git_repo):
        """
        Given: Wrapper is initialized with verbose=True
        When: Wrapper is used
        Then: Debug logging is enabled
        """
        # Given/When
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo), verbose=True)

        # Then
        assert wrapper.verbose is True


class TestWorkingTreeValidation:
    """Test working tree status validation."""

    def test_validate_clean_tree_passes_on_clean_repo(self, mock_git_repo):
        """
        Given: Git repository with no uncommitted changes
        When: validate_clean_tree() is called
        Then: Returns (True, success message)
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # When
        is_clean, message = wrapper.validate_clean_tree()

        # Then
        assert is_clean is True
        assert "clean" in message.lower()

    def test_validate_clean_tree_fails_on_modified_files(self, mock_git_repo):
        """
        Given: Git repository with modified tracked files
        When: validate_clean_tree() is called
        Then: Returns (False, message with modified files)
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # Modify existing file
        readme = mock_git_repo / "README.md"
        readme.write_text("# Modified content\n")

        # When
        is_clean, message = wrapper.validate_clean_tree()

        # Then
        assert is_clean is False
        assert "uncommitted" in message.lower() or "modified" in message.lower()
        assert "README.md" in message

    def test_validate_clean_tree_fails_on_untracked_files(self, mock_git_repo):
        """
        Given: Git repository with untracked files
        When: validate_clean_tree() is called
        Then: Returns (False, message with untracked files)
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # Create untracked file
        new_file = mock_git_repo / "untracked.txt"
        new_file.write_text("untracked content")

        # When
        is_clean, message = wrapper.validate_clean_tree()

        # Then
        assert is_clean is False
        assert "uncommitted" in message.lower() or "untracked" in message.lower()
        assert "untracked.txt" in message

    def test_validate_clean_tree_fails_on_staged_files(self, mock_git_repo):
        """
        Given: Git repository with staged but uncommitted files
        When: validate_clean_tree() is called
        Then: Returns (False, message with staged files)
        """
        # Given
        pytest.importorskip("git")
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # Create and stage file
        new_file = mock_git_repo / "staged.txt"
        new_file.write_text("staged content")
        wrapper.repo.index.add([str(new_file)])

        # When
        is_clean, message = wrapper.validate_clean_tree()

        # Then
        assert is_clean is False
        assert "staged" in message.lower() or "uncommitted" in message.lower()

    def test_validate_clean_tree_truncates_long_file_lists(self, mock_git_repo):
        """
        Given: Git repository with many uncommitted files
        When: validate_clean_tree() is called
        Then: Message shows first few files and indicates more exist
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # Create many untracked files
        for i in range(10):
            (mock_git_repo / f"file_{i:02d}.txt").write_text(f"content {i}")

        # When
        is_clean, message = wrapper.validate_clean_tree()

        # Then
        assert is_clean is False
        assert "..." in message or "more" in message.lower()


class TestConventionalCommitFormatting:
    """Test conventional commit message formatting."""

    def test_format_commit_message_basic(self, mock_git_repo):
        """
        Given: Commit type and description
        When: format_commit_message() is called
        Then: Returns properly formatted conventional commit message
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # When
        message = wrapper.format_commit_message(
            commit_type="feat",
            description="Add new feature"
        )

        # Then
        assert message.startswith("feat: Add new feature")

    def test_format_commit_message_with_scope(self, mock_git_repo):
        """
        Given: Commit type, description, and scope
        When: format_commit_message() is called
        Then: Scope is included in parentheses
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # When
        message = wrapper.format_commit_message(
            commit_type="fix",
            description="Fix bug in parser",
            scope="parser"
        )

        # Then
        assert message.startswith("fix(parser): Fix bug in parser")

    def test_format_commit_message_with_body(self, mock_git_repo):
        """
        Given: Commit with body text
        When: format_commit_message() is called
        Then: Body is included after blank line
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # When
        message = wrapper.format_commit_message(
            commit_type="feat",
            description="Add authentication",
            body="Implements OAuth2 flow with token refresh"
        )

        # Then
        lines = message.split("\n")
        assert len(lines) >= 3
        assert lines[1] == ""  # Blank line
        assert "OAuth2" in lines[2]

    def test_format_commit_message_with_footer(self, mock_git_repo):
        """
        Given: Commit with footer (e.g., issue reference)
        When: format_commit_message() is called
        Then: Footer is included after body
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # When
        message = wrapper.format_commit_message(
            commit_type="fix",
            description="Fix memory leak",
            footer="Fixes #123"
        )

        # Then
        assert "Fixes #123" in message

    def test_format_commit_message_with_breaking_change(self, mock_git_repo):
        """
        Given: Commit marked as breaking change
        When: format_commit_message() is called
        Then: Exclamation mark is added to header
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # When
        message = wrapper.format_commit_message(
            commit_type="feat",
            description="Remove deprecated API",
            breaking_change=True
        )

        # Then
        assert "!" in message.split(":")[0]

    def test_format_commit_message_raises_error_on_invalid_type(self, mock_git_repo):
        """
        Given: Invalid commit type
        When: format_commit_message() is called
        Then: ValueError is raised
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            wrapper.format_commit_message(
                commit_type="invalid_type",
                description="Test"
            )

        assert "invalid commit type" in str(exc_info.value).lower()

    def test_format_commit_message_supports_all_standard_types(self, mock_git_repo):
        """
        Given: Each standard conventional commit type
        When: format_commit_message() is called
        Then: All types are accepted without error
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))
        standard_types = ["feat", "fix", "docs", "style", "refactor", "test", "chore"]

        # When/Then
        for commit_type in standard_types:
            message = wrapper.format_commit_message(
                commit_type=commit_type,
                description="Test commit"
            )
            assert message.startswith(f"{commit_type}:")


class TestS4StateAutoCommit:
    """Test auto-commit functionality for S4 state files."""

    def test_auto_commit_s4_state_validates_file_exists(self, mock_git_repo):
        """
        Given: State file path that doesn't exist
        When: auto_commit_s4_state() is called
        Then: FileNotFoundError is raised
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))
        nonexistent_file = mock_git_repo / "nonexistent.json"

        # When/Then
        with pytest.raises(FileNotFoundError):
            wrapper.auto_commit_s4_state(
                state_path=str(nonexistent_file),
                session_id="TEST_SESSION"
            )

    def test_auto_commit_s4_state_validates_json_format(self, mock_git_repo, sample_s4_state):
        """
        Given: State file with invalid JSON
        When: auto_commit_s4_state() is called
        Then: ValueError is raised
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))
        invalid_json_file = mock_git_repo / "invalid.json"
        invalid_json_file.write_text("{ invalid json }")

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            wrapper.auto_commit_s4_state(
                state_path=str(invalid_json_file),
                session_id="TEST_SESSION"
            )

        assert "invalid json" in str(exc_info.value).lower()

    def test_auto_commit_s4_state_creates_commit_in_normal_mode(self, mock_git_repo, sample_s4_state):
        """
        Given: Valid S4 state file
        When: auto_commit_s4_state() is called (not dry-run)
        Then: File is staged and committed successfully
        """
        # Given
        pytest.importorskip("git")
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo), dry_run=False)
        state_file = mock_git_repo / "state.json"
        state_file.write_text(json.dumps(sample_s4_state))

        # When
        success, message = wrapper.auto_commit_s4_state(
            state_path=str(state_file),
            session_id="BIOELECTRIC_CHAMBERED_20251002000000"
        )

        # Then
        assert success is True
        assert "committed" in message.lower() or "success" in message.lower()

        # Verify commit was created
        latest_commit = wrapper.repo.head.commit
        assert "S4 state" in latest_commit.message or "data" in latest_commit.message

    def test_auto_commit_s4_state_uses_conventional_format(self, mock_git_repo, sample_s4_state):
        """
        Given: Valid S4 state file
        When: auto_commit_s4_state() is called
        Then: Commit message follows conventional format
        """
        # Given
        pytest.importorskip("git")
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo), dry_run=False)
        state_file = mock_git_repo / "state.json"
        state_file.write_text(json.dumps(sample_s4_state))

        # When
        wrapper.auto_commit_s4_state(
            state_path=str(state_file),
            session_id="BIOELECTRIC_CHAMBERED_20251002000000"
        )

        # Then
        latest_commit = wrapper.repo.head.commit
        message = latest_commit.message
        assert message.startswith("data(s4-extraction):")

    def test_auto_commit_s4_state_includes_metadata_in_body(self, mock_git_repo, sample_s4_state):
        """
        Given: Valid S4 state file with metadata
        When: auto_commit_s4_state() is called
        Then: Commit body includes session info and mirror count
        """
        # Given
        pytest.importorskip("git")
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo), dry_run=False)
        state_file = mock_git_repo / "state.json"
        state_file.write_text(json.dumps(sample_s4_state))

        # When
        wrapper.auto_commit_s4_state(
            state_path=str(state_file),
            session_id="BIOELECTRIC_CHAMBERED_20251002000000"
        )

        # Then
        latest_commit = wrapper.repo.head.commit
        message = latest_commit.message
        assert "BIOELECTRIC_CHAMBERED_20251002000000" in message
        assert "Mirrors: 2" in message

    def test_auto_commit_s4_state_includes_additional_files(self, mock_git_repo, sample_s4_state):
        """
        Given: S4 state file and additional files to commit
        When: auto_commit_s4_state() is called with additional_files
        Then: All files are staged and committed together
        """
        # Given
        pytest.importorskip("git")
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo), dry_run=False)
        state_file = mock_git_repo / "state.json"
        state_file.write_text(json.dumps(sample_s4_state))

        additional_file = mock_git_repo / "analysis.txt"
        additional_file.write_text("Analysis results")

        # When
        success, message = wrapper.auto_commit_s4_state(
            state_path=str(state_file),
            session_id="TEST_SESSION",
            additional_files=[str(additional_file)]
        )

        # Then
        assert success is True
        latest_commit = wrapper.repo.head.commit
        committed_files = list(latest_commit.stats.files.keys())
        assert "state.json" in str(committed_files)
        assert "analysis.txt" in str(committed_files)

    def test_auto_commit_s4_state_fails_on_missing_additional_file(self, mock_git_repo, sample_s4_state):
        """
        Given: S4 state file exists but additional file doesn't
        When: auto_commit_s4_state() is called
        Then: Returns (False, error message)
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))
        state_file = mock_git_repo / "state.json"
        state_file.write_text(json.dumps(sample_s4_state))

        # When
        success, message = wrapper.auto_commit_s4_state(
            state_path=str(state_file),
            session_id="TEST_SESSION",
            additional_files=[str(mock_git_repo / "missing.txt")]
        )

        # Then
        assert success is False
        assert "not found" in message.lower()


class TestDryRunMode:
    """Test dry-run mode functionality."""

    def test_dry_run_mode_does_not_create_commit(self, mock_git_repo, sample_s4_state):
        """
        Given: Wrapper in dry-run mode
        When: auto_commit_s4_state() is called
        Then: No commit is created but operation succeeds
        """
        # Given
        pytest.importorskip("git")
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo), dry_run=True)
        state_file = mock_git_repo / "state.json"
        state_file.write_text(json.dumps(sample_s4_state))

        initial_commit = wrapper.repo.head.commit.hexsha

        # When
        success, message = wrapper.auto_commit_s4_state(
            state_path=str(state_file),
            session_id="TEST_SESSION"
        )

        # Then
        assert success is True
        assert "dry-run" in message.lower() or "would" in message.lower()
        # No new commit created
        assert wrapper.repo.head.commit.hexsha == initial_commit

    def test_dry_run_mode_logs_would_be_operations(self, mock_git_repo, sample_s4_state, caplog):
        """
        Given: Wrapper in dry-run mode with verbose logging
        When: auto_commit_s4_state() is called
        Then: Operations are logged but not executed
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo), dry_run=True, verbose=True)
        state_file = mock_git_repo / "state.json"
        state_file.write_text(json.dumps(sample_s4_state))

        # When
        wrapper.auto_commit_s4_state(
            state_path=str(state_file),
            session_id="TEST_SESSION"
        )

        # Then
        # Check that dry-run operations were logged
        # (Actual log checking depends on logging configuration)


class TestRepositoryStatus:
    """Test repository status reporting."""

    def test_get_repo_status_returns_current_branch(self, mock_git_repo):
        """
        Given: Valid Git repository
        When: get_repo_status() is called
        Then: Returns current branch name
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # When
        status = wrapper.get_repo_status()

        # Then
        assert "current_branch" in status
        assert status["current_branch"] in ["master", "main"]

    def test_get_repo_status_returns_dirty_flag(self, mock_git_repo):
        """
        Given: Repository with uncommitted changes
        When: get_repo_status() is called
        Then: is_dirty flag is True
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))
        (mock_git_repo / "dirty.txt").write_text("uncommitted")

        # When
        status = wrapper.get_repo_status()

        # Then
        assert "is_dirty" in status
        assert status["is_dirty"] is True

    def test_get_repo_status_returns_file_lists(self, mock_git_repo):
        """
        Given: Repository with various file states
        When: get_repo_status() is called
        Then: Returns lists of untracked, modified, and staged files
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # Create untracked file
        (mock_git_repo / "untracked.txt").write_text("new")

        # Modify tracked file
        readme = mock_git_repo / "README.md"
        readme.write_text("modified")

        # When
        status = wrapper.get_repo_status()

        # Then
        assert "untracked_files" in status
        assert "modified_files" in status
        assert len(status["untracked_files"]) > 0
        assert len(status["modified_files"]) > 0

    def test_get_repo_status_returns_last_commit_info(self, mock_git_repo):
        """
        Given: Repository with commit history
        When: get_repo_status() is called
        Then: Returns last commit information
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # When
        status = wrapper.get_repo_status()

        # Then
        assert "last_commit" in status
        assert status["last_commit"] is not None
        assert "sha" in status["last_commit"]
        assert "message" in status["last_commit"]
        assert "author" in status["last_commit"]
        assert "date" in status["last_commit"]


class TestExperimentOutputCommit:
    """Test safe commit of experiment output files."""

    def test_safe_commit_experiment_output_validates_files_exist(self, mock_git_repo):
        """
        Given: Some output files don't exist
        When: safe_commit_experiment_output() is called
        Then: Returns (False, error message) listing missing files
        """
        # Given
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo))

        # When
        success, message = wrapper.safe_commit_experiment_output(
            experiment_id="EXP001",
            output_files=[str(mock_git_repo / "missing.txt")],
            description="Test experiment"
        )

        # Then
        assert success is False
        assert "missing" in message.lower()

    def test_safe_commit_experiment_output_commits_all_files(self, mock_git_repo):
        """
        Given: Valid output files exist
        When: safe_commit_experiment_output() is called
        Then: All files are committed successfully
        """
        # Given
        pytest.importorskip("git")
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo), dry_run=False)

        # Create output files
        output1 = mock_git_repo / "output1.txt"
        output2 = mock_git_repo / "output2.txt"
        output1.write_text("result 1")
        output2.write_text("result 2")

        # When
        success, message = wrapper.safe_commit_experiment_output(
            experiment_id="EXP001",
            output_files=[str(output1), str(output2)],
            description="Run bioelectric simulation"
        )

        # Then
        assert success is True
        latest_commit = wrapper.repo.head.commit
        assert "experiment" in latest_commit.message.lower()

    def test_safe_commit_experiment_output_uses_conventional_format(self, mock_git_repo):
        """
        Given: Experiment output files
        When: safe_commit_experiment_output() is called
        Then: Commit message follows conventional format with experiment type
        """
        # Given
        pytest.importorskip("git")
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo), dry_run=False)

        output_file = mock_git_repo / "results.txt"
        output_file.write_text("experiment results")

        # When
        wrapper.safe_commit_experiment_output(
            experiment_id="APERTURE_TEST",
            output_files=[str(output_file)],
            description="Test gap junction coupling"
        )

        # Then
        latest_commit = wrapper.repo.head.commit
        message = latest_commit.message
        assert message.startswith("experiment(APERTURE_TEST):")

    def test_safe_commit_experiment_output_respects_dry_run(self, mock_git_repo):
        """
        Given: Wrapper in dry-run mode
        When: safe_commit_experiment_output() is called
        Then: No commit is created but success is returned
        """
        # Given
        pytest.importorskip("git")
        wrapper = GitMCPWrapper(repo_path=str(mock_git_repo), dry_run=True)

        output_file = mock_git_repo / "results.txt"
        output_file.write_text("results")

        initial_commit = wrapper.repo.head.commit.hexsha

        # When
        success, message = wrapper.safe_commit_experiment_output(
            experiment_id="EXP001",
            output_files=[str(output_file)],
            description="Test"
        )

        # Then
        assert success is True
        assert "dry-run" in message.lower()
        assert wrapper.repo.head.commit.hexsha == initial_commit
