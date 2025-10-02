# MCP Integration Tests

Comprehensive test suite for the IRIS Gate Model Context Protocol (MCP) system.

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and test utilities
├── test_mcp_init.py           # MCP initialization and health checks
├── test_index_scrolls.py      # Scroll parsing and ChromaDB indexing
├── test_git_mcp_wrapper.py    # Git operations and auto-commit
├── test_mcp_e2e.py            # End-to-end integration tests
└── requirements-test.txt       # Test dependencies
```

## Test Coverage

### 1. MCP Initialization (`test_mcp_init.py`)
- Configuration file loading and validation
- Directory creation for each server type
- ChromaDB health checking (connection, write/read operations)
- Git repository validation
- Quick-Data storage testing
- Health report generation

### 2. Scroll Indexing (`test_index_scrolls.py`)
- Markdown parsing from scroll files
- Metadata extraction (session, mirror, chamber, turn, pressure, seal)
- Living Scroll and Technical Translation extraction
- Convergence score calculation
- Embedding generation and ChromaDB storage
- Semantic search functionality
- Filtering by chamber, mirror, convergence threshold
- Collection statistics and reporting

### 3. Git Wrapper (`test_git_mcp_wrapper.py`)
- Working tree validation (clean vs dirty)
- Conventional commit message formatting
- S4 state auto-commit functionality
- Additional file staging
- Dry-run mode verification
- Repository status reporting
- Error handling for invalid repositories

### 4. End-to-End Integration (`test_mcp_e2e.py`)
- Full workflow: init → index → search → commit
- Multi-session indexing
- Error recovery and graceful degradation
- Real-world usage scenarios
- Data integrity verification
- Performance characteristics

## Running Tests

### Install Test Dependencies

```bash
# From project root
pip install -r tests/requirements-test.txt
```

### Run All Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run all tests with coverage report
pytest tests/ --cov=scripts --cov-report=html

# Run specific test file
pytest tests/test_mcp_init.py -v

# Run specific test class
pytest tests/test_mcp_init.py::TestMCPConfigurationLoading -v

# Run specific test
pytest tests/test_mcp_init.py::TestMCPConfigurationLoading::test_load_valid_config_succeeds -v
```

### Run Tests in Parallel

```bash
# Use multiple CPU cores for faster execution
pytest tests/ -n auto
```

### Run with Detailed Output

```bash
# Show print statements and logs
pytest tests/ -v -s

# Show local variables on failure
pytest tests/ -v -l
```

### Run Only Fast Tests (Skip Slow Integration Tests)

```bash
# You can mark slow tests with @pytest.mark.slow
pytest tests/ -v -m "not slow"
```

## Test-Driven Development (TDD) Approach

These tests were written **before** implementation to:

1. **Define Expected Behavior**: Each test documents what the system should do
2. **Guide Implementation**: Tests fail initially, then pass as features are implemented
3. **Prevent Regressions**: Future changes that break functionality are caught immediately
4. **Serve as Documentation**: Tests show how to use each component correctly

### Expected Initial State

**These tests are expected to FAIL initially** until the implementations are complete or updated to handle all test scenarios. This is intentional and follows TDD principles:

```
Given: Tests define expected behavior
When: Implementation is created/updated
Then: Tests pass, confirming correct implementation
```

## Fixtures

The `conftest.py` file provides reusable fixtures:

- `temp_dir`: Isolated temporary directory for each test
- `sample_scroll_content`: Valid scroll markdown content
- `sample_scroll_s4_content`: S4 chamber scroll with high convergence
- `mock_scroll_directory`: Complete scroll directory structure
- `mock_mcp_config`: MCP configuration file
- `mock_git_repo`: Initialized Git repository
- `sample_s4_state`: S4 state extraction data
- `mock_vault_structure`: Complete IRIS vault structure

## Test Organization

Tests follow the **Given/When/Then** pattern:

```python
def test_example(self, fixture):
    """
    Given: Initial conditions and setup
    When: Action being tested
    Then: Expected outcome
    """
    # Given
    setup_code()

    # When
    result = function_under_test()

    # Then
    assert result == expected_value
```

## Common Test Patterns

### Testing Success Path

```python
def test_operation_succeeds_with_valid_input(self, mock_fixture):
    # Given: Valid setup
    # When: Operation is performed
    # Then: Success result
    assert success is True
```

### Testing Error Handling

```python
def test_operation_raises_error_on_invalid_input(self, mock_fixture):
    # Given: Invalid input
    # When/Then: Appropriate error is raised
    with pytest.raises(ValueError) as exc_info:
        operation(invalid_input)
    assert "helpful message" in str(exc_info.value)
```

### Testing Edge Cases

```python
def test_operation_handles_empty_input(self, mock_fixture):
    # Given: Empty or boundary condition
    # When: Operation is performed
    # Then: Graceful handling
    assert result == expected_for_edge_case
```

## Debugging Failed Tests

### View Full Error Output

```bash
pytest tests/test_mcp_init.py::test_that_fails -v --tb=long
```

### Drop into Debugger on Failure

```bash
pytest tests/test_mcp_init.py::test_that_fails --pdb
```

### Run Only Failed Tests from Last Run

```bash
pytest tests/ --lf  # --last-failed
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt -r tests/requirements-test.txt
      - run: pytest tests/ --cov=scripts --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Writing New Tests

When adding new MCP functionality:

1. **Write tests first** (TDD approach)
2. Use existing fixtures from `conftest.py`
3. Follow Given/When/Then structure
4. Test both success and failure paths
5. Include edge cases
6. Add descriptive docstrings

Example:

```python
def test_new_feature_succeeds(self, mock_fixture):
    """
    Given: Specific preconditions
    When: New feature is used
    Then: Expected behavior occurs
    """
    # Given
    setup = prepare_test_data()

    # When
    result = new_feature(setup)

    # Then
    assert result.success is True
    assert result.data == expected_data
```

## Notes on Test Isolation

- Each test uses temporary directories (automatically cleaned up)
- ChromaDB instances use separate paths per test
- Git repositories are created fresh for each test
- No tests modify the actual project files
- Tests can run in any order (no dependencies between tests)

## Expected Implementation Fixes

After writing these tests, the following implementation updates are expected:

1. **init_mcp.py**: Handle missing dependencies gracefully with ImportError catching
2. **index_scrolls.py**: Robust scroll parsing with error recovery
3. **git_mcp_wrapper.py**: Comprehensive error handling for all Git operations
4. All modules: Proper logging for debugging

The tests will guide these implementations by failing initially and passing once fixes are applied.
