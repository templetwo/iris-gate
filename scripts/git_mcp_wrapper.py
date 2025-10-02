#!/usr/bin/env python3
"""
Git MCP Wrapper for IRIS Gate

Provides safe Git operations for automated state tracking with:
- Auto-commit S4 state extractions
- Pre-commit validation (clean working tree checks)
- Conventional commit message formatting
- Dry-run mode for testing
- Integration with IRIS workflow

Usage:
    python scripts/git_mcp_wrapper.py --auto-commit --state-path sandbox/states/state.json --session-id BIOELECTRIC_20251001
    python scripts/git_mcp_wrapper.py --validate-tree
    python scripts/git_mcp_wrapper.py --format-message "feat" "Add S4 state extraction for session XYZ"
    python scripts/git_mcp_wrapper.py --auto-commit --dry-run
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import git
    from git.exc import GitCommandError, InvalidGitRepositoryError
except ImportError:
    print("Error: GitPython not installed. Run: pip install GitPython", file=sys.stderr)
    sys.exit(1)


class GitMCPWrapper:
    """
    Safe Git operations wrapper for IRIS Gate automation.

    This wrapper provides automated Git operations with safety checks,
    conventional commit formatting, and integration with IRIS workflows.
    """

    # Conventional commit types
    COMMIT_TYPES = {
        "feat": "New feature or capability",
        "fix": "Bug fix",
        "docs": "Documentation changes",
        "style": "Code style changes (formatting, etc.)",
        "refactor": "Code refactoring",
        "test": "Test additions or modifications",
        "chore": "Build process or auxiliary tool changes",
        "data": "Data file additions (S4 states, outputs)",
        "experiment": "Experiment run or results",
    }

    def __init__(
        self, repo_path: str = ".", dry_run: bool = False, verbose: bool = False
    ):
        """
        Initialize the Git MCP wrapper.

        Args:
            repo_path: Path to the Git repository root
            dry_run: If True, print operations without executing them
            verbose: Enable verbose logging output

        Raises:
            InvalidGitRepositoryError: If the path is not a valid Git repository
        """
        self.repo_path = Path(repo_path).absolute()
        self.dry_run = dry_run
        self.verbose = verbose

        # Set up logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

        # Initialize Git repository
        try:
            self.repo = git.Repo(self.repo_path)
        except InvalidGitRepositoryError:
            raise InvalidGitRepositoryError(
                f"Not a valid Git repository: {self.repo_path}\n"
                "Initialize with: git init"
            )

        if self.dry_run:
            self.logger.info("Running in DRY-RUN mode - no changes will be made")

    def validate_clean_tree(self) -> Tuple[bool, str]:
        """
        Validate that the working tree is clean (no uncommitted changes).

        Returns:
            Tuple of (is_clean: bool, message: str)
            - is_clean: True if working tree is clean, False otherwise
            - message: Description of the validation result
        """
        try:
            # Check for uncommitted changes
            if self.repo.is_dirty(untracked_files=True):
                # Get detailed status
                changed_files = [item.a_path for item in self.repo.index.diff(None)]
                staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
                untracked_files = self.repo.untracked_files

                status_parts = []
                if changed_files:
                    status_parts.append(f"Modified: {', '.join(changed_files[:5])}")
                if staged_files:
                    status_parts.append(f"Staged: {', '.join(staged_files[:5])}")
                if untracked_files:
                    status_parts.append(f"Untracked: {', '.join(untracked_files[:5])}")

                message = "Working tree has uncommitted changes:\n  " + "\n  ".join(
                    status_parts
                )

                if len(changed_files) + len(staged_files) + len(untracked_files) > 5:
                    message += f"\n  ... and {len(changed_files) + len(staged_files) + len(untracked_files) - 5} more"

                return False, message

            return True, "Working tree is clean"

        except Exception as e:
            return False, f"Error validating working tree: {e}"

    def format_commit_message(
        self,
        commit_type: str,
        description: str,
        scope: Optional[str] = None,
        body: Optional[str] = None,
        footer: Optional[str] = None,
        breaking_change: bool = False,
    ) -> str:
        """
        Format a commit message following conventional commits specification.

        Args:
            commit_type: Type of commit (feat, fix, docs, etc.)
            description: Short description of the change (imperative mood)
            scope: Optional scope of the change (e.g., "sandbox", "mcp")
            body: Optional longer description
            footer: Optional footer (e.g., issue references)
            breaking_change: If True, marks as a breaking change

        Returns:
            Formatted commit message string

        Raises:
            ValueError: If commit_type is not recognized
        """
        if commit_type not in self.COMMIT_TYPES:
            raise ValueError(
                f"Invalid commit type: {commit_type}\n"
                f"Valid types: {', '.join(self.COMMIT_TYPES.keys())}"
            )

        # Build header
        header_parts = [commit_type]
        if scope:
            header_parts.append(f"({scope})")

        if breaking_change:
            header_parts.append("!")

        header = "".join(header_parts) + f": {description}"

        # Build full message
        message_parts = [header]

        if body:
            message_parts.append("")  # Blank line
            message_parts.append(body)

        if footer:
            message_parts.append("")  # Blank line
            message_parts.append(footer)

        return "\n".join(message_parts)

    def auto_commit_s4_state(
        self,
        state_path: str,
        session_id: str,
        additional_files: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """
        Auto-commit S4 state extraction files with conventional formatting.

        This function safely commits S4 state files after validation:
        1. Validates the state file exists and is valid JSON
        2. Checks working tree is clean or only contains expected files
        3. Stages the state file and any additional files
        4. Creates a formatted commit message
        5. Commits with proper metadata

        Args:
            state_path: Path to the S4 state JSON file
            session_id: IRIS session ID for the state
            additional_files: Optional list of additional files to commit

        Returns:
            Tuple of (success: bool, message: str)

        Raises:
            FileNotFoundError: If state_path does not exist
            ValueError: If state file is not valid JSON
        """
        state_path = Path(state_path)

        # Validate state file exists
        if not state_path.exists():
            raise FileNotFoundError(f"State file not found: {state_path}")

        # Validate state file is valid JSON
        try:
            with open(state_path) as f:
                state_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in state file: {e}")

        # Extract metadata from state
        mirror_count = len(state_data.get("mirrors", {}))
        timestamp = state_data.get("timestamp", "unknown")

        # Build file list
        files_to_commit = [str(state_path)]
        if additional_files:
            files_to_commit.extend(additional_files)

        # Validate files exist
        for file_path in files_to_commit:
            if not Path(file_path).exists():
                return False, f"File not found: {file_path}"

        # Format commit message
        scope = "s4-extraction"
        description = f"Add S4 state for session {session_id}"
        body = (
            f"Session: {session_id}\n"
            f"Mirrors: {mirror_count}\n"
            f"Timestamp: {timestamp}\n"
            f"State file: {state_path.name}"
        )

        if additional_files:
            body += "\n\nAdditional files:\n" + "\n".join(
                f"- {f}" for f in additional_files
            )

        commit_message = self.format_commit_message(
            commit_type="data", description=description, scope=scope, body=body
        )

        # Execute commit
        if self.dry_run:
            self.logger.info(f"[DRY-RUN] Would stage files: {files_to_commit}")
            self.logger.info(f"[DRY-RUN] Would commit with message:\n{commit_message}")
            return True, f"Dry-run successful for {len(files_to_commit)} files"

        try:
            # Stage files
            self.repo.index.add(files_to_commit)
            self.logger.info(f"Staged {len(files_to_commit)} files")

            # Commit
            commit = self.repo.index.commit(commit_message)
            self.logger.info(f"Created commit: {commit.hexsha[:8]}")

            return (
                True,
                f"Successfully committed {len(files_to_commit)} files (commit: {commit.hexsha[:8]})",
            )

        except GitCommandError as e:
            return False, f"Git command failed: {e}"
        except Exception as e:
            return False, f"Unexpected error during commit: {e}"

    def get_repo_status(self) -> Dict:
        """
        Get current repository status.

        Returns:
            Dictionary containing repository status information
        """
        try:
            status = {
                "repo_path": str(self.repo_path),
                "current_branch": self.repo.active_branch.name,
                "is_dirty": self.repo.is_dirty(),
                "untracked_files": self.repo.untracked_files,
                "modified_files": [item.a_path for item in self.repo.index.diff(None)],
                "staged_files": [item.a_path for item in self.repo.index.diff("HEAD")],
                "last_commit": {
                    "sha": self.repo.head.commit.hexsha[:8],
                    "message": self.repo.head.commit.message.strip(),
                    "author": str(self.repo.head.commit.author),
                    "date": datetime.fromtimestamp(
                        self.repo.head.commit.committed_date
                    ).isoformat(),
                }
                if self.repo.head.is_valid()
                else None,
            }
            return status
        except Exception as e:
            return {"error": str(e)}

    def safe_commit_experiment_output(
        self, experiment_id: str, output_files: List[str], description: str
    ) -> Tuple[bool, str]:
        """
        Safely commit experiment output files with metadata.

        Args:
            experiment_id: Unique identifier for the experiment
            output_files: List of output file paths to commit
            description: Short description of the experiment

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Validate all files exist
        missing_files = [f for f in output_files if not Path(f).exists()]
        if missing_files:
            return False, f"Missing output files: {', '.join(missing_files)}"

        # Format commit message
        commit_message = self.format_commit_message(
            commit_type="experiment",
            description=description,
            scope=experiment_id,
            body="Output files:\n" + "\n".join(f"- {f}" for f in output_files),
        )

        # Execute commit
        if self.dry_run:
            self.logger.info("[DRY-RUN] Would commit experiment output:")
            self.logger.info(f"  Experiment: {experiment_id}")
            self.logger.info(f"  Files: {len(output_files)}")
            self.logger.info(f"  Message:\n{commit_message}")
            return True, f"Dry-run successful for experiment {experiment_id}"

        try:
            self.repo.index.add(output_files)
            commit = self.repo.index.commit(commit_message)
            return (
                True,
                f"Committed experiment {experiment_id} (commit: {commit.hexsha[:8]})",
            )
        except GitCommandError as e:
            return False, f"Git command failed: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"


def main():
    """Main entry point for the Git MCP wrapper CLI."""
    parser = argparse.ArgumentParser(
        description="Git MCP wrapper for safe automated Git operations in IRIS Gate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-commit S4 state extraction
  %(prog)s --auto-commit \\
      --state-path sandbox/states/BIOELECTRIC_20251001.json \\
      --session-id BIOELECTRIC_CHAMBERED_20251001054935

  # Validate working tree is clean
  %(prog)s --validate-tree

  # Format a conventional commit message
  %(prog)s --format-message feat "Add new MCP integration" \\
      --scope mcp --body "Detailed description here"

  # Dry-run mode (test without committing)
  %(prog)s --auto-commit --state-path <path> --session-id <id> --dry-run

  # Get repository status
  %(prog)s --status
        """,
    )

    parser.add_argument(
        "--auto-commit",
        action="store_true",
        help="Auto-commit S4 state or experiment files",
    )

    parser.add_argument(
        "--state-path", type=str, help="Path to S4 state JSON file for auto-commit"
    )

    parser.add_argument(
        "--session-id", type=str, help="IRIS session ID for auto-commit"
    )

    parser.add_argument(
        "--additional-files",
        nargs="+",
        help="Additional files to include in auto-commit",
    )

    parser.add_argument(
        "--validate-tree",
        action="store_true",
        help="Validate that working tree is clean",
    )

    parser.add_argument(
        "--format-message",
        nargs=2,
        metavar=("TYPE", "DESCRIPTION"),
        help="Format a conventional commit message (type and description)",
    )

    parser.add_argument("--scope", type=str, help="Scope for commit message formatting")

    parser.add_argument("--body", type=str, help="Body for commit message formatting")

    parser.add_argument(
        "--status", action="store_true", help="Display repository status"
    )

    parser.add_argument(
        "--repo-path",
        type=str,
        default=".",
        help="Path to Git repository (default: current directory)",
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Print operations without executing them"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Require at least one action
    if not (
        args.auto_commit or args.validate_tree or args.format_message or args.status
    ):
        parser.print_help()
        sys.exit(1)

    try:
        # Initialize wrapper
        wrapper = GitMCPWrapper(
            repo_path=args.repo_path, dry_run=args.dry_run, verbose=args.verbose
        )

        # Handle status
        if args.status:
            status = wrapper.get_repo_status()
            print("\n=== Repository Status ===")
            print(json.dumps(status, indent=2))
            sys.exit(0)

        # Handle validate tree
        if args.validate_tree:
            is_clean, message = wrapper.validate_clean_tree()
            print(f"\n{'✓' if is_clean else '✗'} {message}")
            sys.exit(0 if is_clean else 1)

        # Handle format message
        if args.format_message:
            commit_type, description = args.format_message
            message = wrapper.format_commit_message(
                commit_type=commit_type,
                description=description,
                scope=args.scope,
                body=args.body,
            )
            print("\n=== Formatted Commit Message ===")
            print(message)
            sys.exit(0)

        # Handle auto-commit
        if args.auto_commit:
            if not args.state_path or not args.session_id:
                print(
                    "Error: --state-path and --session-id required for auto-commit",
                    file=sys.stderr,
                )
                sys.exit(1)

            success, message = wrapper.auto_commit_s4_state(
                state_path=args.state_path,
                session_id=args.session_id,
                additional_files=args.additional_files,
            )

            print(f"\n{'✓' if success else '✗'} {message}")
            sys.exit(0 if success else 1)

    except InvalidGitRepositoryError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
