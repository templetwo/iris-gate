"""
IRIS Gate MCP Integration Tests

This package contains comprehensive integration tests for the Model Context Protocol
(MCP) system, following test-driven development (TDD) principles.

Test Modules:
- test_mcp_init: MCP initialization and health checking
- test_index_scrolls: Scroll parsing and ChromaDB indexing
- test_git_mcp_wrapper: Git operations and auto-commit
- test_mcp_e2e: End-to-end integration tests

Run all tests:
    pytest tests/ -v

Run specific test file:
    pytest tests/test_mcp_init.py -v

See tests/README.md for detailed documentation.
"""

__version__ = "1.0.0"
