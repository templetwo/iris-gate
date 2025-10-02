#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Initialization and Testing Utilities

This script initializes the MCP environment for IRIS Gate and provides
connectivity testing for all configured Tier 1 MCP servers:
- ChromaDB: Local vector database
- Git: Version control integration
- Quick-Data: Fast key-value storage

Usage:
    python scripts/init_mcp.py --test-all           # Test all servers
    python scripts/init_mcp.py --test chromadb      # Test specific server
    python scripts/init_mcp.py --init               # Initialize only
    python scripts/init_mcp.py --verbose            # Verbose output
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


# Suppress tokenizer parallelism warnings from ChromaDB embedding functions
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv


@dataclass
class ServerHealth:
    """Health status for an MCP server."""

    name: str
    healthy: bool
    message: str
    details: Optional[Dict] = None


class MCPInitializer:
    """
    Handles initialization and health checking of MCP servers.

    This class manages the setup of local MCP servers and provides
    comprehensive health checking to ensure all components are properly
    configured and operational.
    """

    def __init__(self, config_path: str = ".mcp-config.json", verbose: bool = False):
        """
        Initialize the MCP environment manager.

        Args:
            config_path: Path to the MCP configuration file
            verbose: Enable verbose logging output

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the configuration file is invalid JSON
        """
        self.config_path = Path(config_path)
        self.verbose = verbose
        self.project_root = self.config_path.parent

        # Set up logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

        # Load environment variables
        load_dotenv()

        # Load configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """
        Load and validate the MCP configuration file.

        Returns:
            Parsed configuration dictionary

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            json.JSONDecodeError: If configuration is invalid JSON
            ValueError: If configuration is missing required fields
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"MCP configuration file not found: {self.config_path}\n"
                f"Expected location: {self.config_path.absolute()}\n"
                "Run from the project root directory or specify --config-path"
            )

        try:
            with open(self.config_path) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in MCP configuration file: {e.msg}", e.doc, e.pos
            )

        # Validate required fields
        if "servers" not in config:
            raise ValueError(
                "MCP configuration must include 'servers' section.\n"
                f"Check {self.config_path} for proper structure."
            )

        self.logger.info(f"Loaded MCP configuration from {self.config_path}")
        return config

    def _ensure_directory(self, path: Path) -> None:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            path: Directory path to ensure exists
        """
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created directory: {path}")
        else:
            self.logger.debug(f"Directory exists: {path}")

    def initialize(self) -> bool:
        """
        Initialize all MCP server directories and dependencies.

        Creates required directories for each enabled server and validates
        that all prerequisites are met.

        Returns:
            True if initialization succeeded, False otherwise
        """
        self.logger.info("Initializing MCP environment...")

        try:
            servers = self.config.get("servers", {})
            enabled_servers = [
                name for name, cfg in servers.items() if cfg.get("enabled", False)
            ]

            if not enabled_servers:
                self.logger.warning("No servers enabled in configuration")
                return False

            self.logger.info(f"Enabled servers: {', '.join(enabled_servers)}")

            # Initialize each server's storage
            for server_name in enabled_servers:
                server_config = servers[server_name]["config"]

                if server_name == "chromadb":
                    persist_dir = Path(server_config["persist_directory"])
                    self._ensure_directory(persist_dir)
                    self.logger.info(f"ChromaDB storage ready: {persist_dir}")

                elif server_name == "git":
                    repo_path = Path(server_config["repo_path"])
                    git_dir = repo_path / ".git"
                    if not git_dir.exists():
                        self.logger.warning(
                            f"Git repository not initialized at {repo_path}\n"
                            "Run 'git init' if this is a new repository"
                        )
                    else:
                        self.logger.info(f"Git repository found: {repo_path}")

                elif server_name == "quickdata":
                    data_path = Path(server_config["data_path"])
                    self._ensure_directory(data_path)
                    self.logger.info(f"Quick-Data storage ready: {data_path}")

            self.logger.info("MCP initialization complete")
            return True

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}", exc_info=self.verbose)
            return False

    def test_chromadb(self) -> ServerHealth:
        """
        Test ChromaDB server connectivity and basic operations.

        Returns:
            ServerHealth object with test results
        """
        try:
            import chromadb
            from chromadb.config import Settings

            server_config = self.config["servers"]["chromadb"]["config"]
            persist_dir = str(Path(server_config["persist_directory"]).absolute())

            # Create client
            client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(
                    anonymized_telemetry=server_config.get(
                        "anonymized_telemetry", False
                    )
                ),
            )

            # Test basic operations
            collection_name = server_config.get("collection_name", "iris_context")

            # Get or create collection
            collection = client.get_or_create_collection(name=collection_name)

            # Test add and query
            test_id = "_mcp_health_check"
            collection.upsert(
                ids=[test_id],
                documents=["MCP health check test"],
                metadatas=[{"type": "health_check"}],
            )

            # Verify
            results = collection.get(ids=[test_id])

            # Clean up
            collection.delete(ids=[test_id])

            collection_count = collection.count()

            return ServerHealth(
                name="chromadb",
                healthy=True,
                message=f"ChromaDB operational at {persist_dir}",
                details={
                    "collection": collection_name,
                    "document_count": collection_count,
                    "persist_directory": persist_dir,
                },
            )

        except ImportError as e:
            return ServerHealth(
                name="chromadb",
                healthy=False,
                message=f"ChromaDB not installed: {e}\nRun: pip install chromadb",
                details={"error_type": "ImportError"},
            )
        except Exception as e:
            return ServerHealth(
                name="chromadb",
                healthy=False,
                message=f"ChromaDB test failed: {e}",
                details={"error_type": type(e).__name__},
            )

    def test_git(self) -> ServerHealth:
        """
        Test Git server connectivity and repository access.

        Returns:
            ServerHealth object with test results
        """
        try:
            import git

            server_config = self.config["servers"]["git"]["config"]
            repo_path = Path(server_config["repo_path"]).absolute()

            # Open repository
            repo = git.Repo(repo_path)

            # Get repository information
            is_bare = repo.bare
            current_branch = repo.active_branch.name if not is_bare else "N/A"
            commit_count = sum(1 for _ in repo.iter_commits())
            has_uncommitted = repo.is_dirty()

            return ServerHealth(
                name="git",
                healthy=True,
                message=f"Git repository operational at {repo_path}",
                details={
                    "repo_path": str(repo_path),
                    "current_branch": current_branch,
                    "commit_count": commit_count,
                    "has_uncommitted_changes": has_uncommitted,
                    "is_bare": is_bare,
                },
            )

        except ImportError as e:
            return ServerHealth(
                name="git",
                healthy=False,
                message=f"GitPython not installed: {e}\nRun: pip install GitPython",
                details={"error_type": "ImportError"},
            )
        except git.exc.InvalidGitRepositoryError:
            return ServerHealth(
                name="git",
                healthy=False,
                message=f"Invalid Git repository at {repo_path}\nRun 'git init' to initialize",
                details={"error_type": "InvalidGitRepositoryError"},
            )
        except Exception as e:
            return ServerHealth(
                name="git",
                healthy=False,
                message=f"Git test failed: {e}",
                details={"error_type": type(e).__name__},
            )

    def test_quickdata(self) -> ServerHealth:
        """
        Test Quick-Data server connectivity and file operations.

        Returns:
            ServerHealth object with test results
        """
        try:
            server_config = self.config["servers"]["quickdata"]["config"]
            data_path = Path(server_config["data_path"]).absolute()

            # Ensure directory exists
            data_path.mkdir(parents=True, exist_ok=True)

            # Test file operations
            test_file = data_path / "_mcp_health_check.json"
            test_data = {
                "type": "health_check",
                "status": "testing",
                "timestamp": str(Path(__file__).stat().st_mtime),
            }

            # Write test
            with open(test_file, "w") as f:
                json.dump(test_data, f)

            # Read test
            with open(test_file) as f:
                read_data = json.load(f)

            # Verify
            if read_data != test_data:
                raise ValueError("Data mismatch in read/write test")

            # Clean up
            test_file.unlink()

            # Count existing files
            file_count = len(list(data_path.glob("*.json")))

            return ServerHealth(
                name="quickdata",
                healthy=True,
                message=f"Quick-Data operational at {data_path}",
                details={
                    "data_path": str(data_path),
                    "file_count": file_count,
                    "format": server_config.get("format", "json"),
                    "writable": True,
                },
            )

        except PermissionError:
            return ServerHealth(
                name="quickdata",
                healthy=False,
                message=f"Permission denied for Quick-Data path: {data_path}",
                details={"error_type": "PermissionError"},
            )
        except Exception as e:
            return ServerHealth(
                name="quickdata",
                healthy=False,
                message=f"Quick-Data test failed: {e}",
                details={"error_type": type(e).__name__},
            )

    def test_server(self, server_name: str) -> ServerHealth:
        """
        Test a specific MCP server.

        Args:
            server_name: Name of the server to test (chromadb, git, quickdata)

        Returns:
            ServerHealth object with test results

        Raises:
            ValueError: If server_name is not recognized
        """
        if server_name not in self.config.get("servers", {}):
            raise ValueError(
                f"Unknown server: {server_name}\n"
                f"Available servers: {', '.join(self.config.get('servers', {}).keys())}"
            )

        if not self.config["servers"][server_name].get("enabled", False):
            return ServerHealth(
                name=server_name,
                healthy=False,
                message=f"Server '{server_name}' is disabled in configuration",
            )

        self.logger.info(f"Testing {server_name}...")

        if server_name == "chromadb":
            return self.test_chromadb()
        elif server_name == "git":
            return self.test_git()
        elif server_name == "quickdata":
            return self.test_quickdata()
        else:
            return ServerHealth(
                name=server_name,
                healthy=False,
                message=f"No test implementation for server: {server_name}",
            )

    def test_all(self) -> List[ServerHealth]:
        """
        Test all enabled MCP servers.

        Returns:
            List of ServerHealth objects for all enabled servers
        """
        results = []

        servers = self.config.get("servers", {})
        enabled_servers = [
            name for name, cfg in servers.items() if cfg.get("enabled", False)
        ]

        self.logger.info(f"Testing {len(enabled_servers)} enabled servers...")

        for server_name in enabled_servers:
            result = self.test_server(server_name)
            results.append(result)

        return results

    def print_health_report(self, results: List[ServerHealth]) -> bool:
        """
        Print a formatted health report for tested servers.

        Args:
            results: List of ServerHealth objects

        Returns:
            True if all servers are healthy, False otherwise
        """
        print("\n" + "=" * 70)
        print("MCP SERVER HEALTH REPORT")
        print("=" * 70)

        all_healthy = True

        for result in results:
            status_symbol = "✓" if result.healthy else "✗"
            status_text = "HEALTHY" if result.healthy else "FAILED"

            print(f"\n{status_symbol} {result.name.upper()}: {status_text}")
            print(f"  Message: {result.message}")

            if result.details and self.verbose:
                print("  Details:")
                for key, value in result.details.items():
                    print(f"    - {key}: {value}")

            if not result.healthy:
                all_healthy = False

        print("\n" + "=" * 70)

        if all_healthy:
            print("STATUS: All MCP servers are operational")
        else:
            print("STATUS: Some MCP servers have issues - see details above")

        print("=" * 70 + "\n")

        return all_healthy


def main():
    """Main entry point for the MCP initialization script."""
    parser = argparse.ArgumentParser(
        description="Initialize and test MCP environment for IRIS Gate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --test-all              Test all enabled servers
  %(prog)s --test chromadb         Test ChromaDB only
  %(prog)s --init                  Initialize environment only
  %(prog)s --test-all --verbose    Test with detailed output
        """,
    )

    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize MCP environment (create directories, etc.)",
    )

    parser.add_argument(
        "--test",
        type=str,
        metavar="SERVER",
        help="Test a specific server (chromadb, git, quickdata)",
    )

    parser.add_argument(
        "--test-all", action="store_true", help="Test all enabled MCP servers"
    )

    parser.add_argument(
        "--config-path",
        type=str,
        default=".mcp-config.json",
        help="Path to MCP configuration file (default: .mcp-config.json)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Require at least one action
    if not (args.init or args.test or args.test_all):
        parser.print_help()
        sys.exit(1)

    try:
        # Initialize MCP manager
        mcp = MCPInitializer(config_path=args.config_path, verbose=args.verbose)

        # Run initialization if requested
        if args.init:
            if not mcp.initialize():
                print("Initialization failed", file=sys.stderr)
                sys.exit(1)
            print("MCP environment initialized successfully")

        # Run tests if requested
        if args.test:
            result = mcp.test_server(args.test)
            mcp.print_health_report([result])
            sys.exit(0 if result.healthy else 1)

        if args.test_all:
            results = mcp.test_all()
            all_healthy = mcp.print_health_report(results)
            sys.exit(0 if all_healthy else 1)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}", file=sys.stderr)
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
