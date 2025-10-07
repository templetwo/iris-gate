#!/usr/bin/env bash
#
# CI Gates for IRIS Gate Orchestrator
#
# Pre-merge validation gates run before integrating agent changes.
# All gates must pass for merge to proceed.

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Exit codes
EXIT_SUCCESS=0
EXIT_FAILURE=1

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo "  $1"
}

# Gate: Check working tree is clean
check_clean_tree() {
    echo "=== Gate: Clean Working Tree ==="

    if [[ -n $(git status --porcelain) ]]; then
        print_error "Working tree is not clean"
        git status --short
        return $EXIT_FAILURE
    fi

    print_success "Working tree is clean"
    return $EXIT_SUCCESS
}

# Gate: Run code style check with ruff
check_code_style() {
    echo "=== Gate: Code Style Check ==="

    if ! command -v ruff &> /dev/null; then
        print_warning "ruff not installed, skipping"
        return $EXIT_SUCCESS
    fi

    if ruff check scripts/ tests/ 2>&1; then
        print_success "Code style check passed"
        return $EXIT_SUCCESS
    else
        print_error "Code style issues found"
        return $EXIT_FAILURE
    fi
}

# Gate: Run code formatter check with ruff
check_code_format() {
    echo "=== Gate: Code Format Check ==="

    if ! command -v ruff &> /dev/null; then
        print_warning "ruff not installed, skipping"
        return $EXIT_SUCCESS
    fi

    if ruff format --check scripts/ tests/ 2>&1; then
        print_success "Code format check passed"
        return $EXIT_SUCCESS
    else
        print_error "Code formatting issues found"
        print_info "Run: ruff format scripts/ tests/"
        return $EXIT_FAILURE
    fi
}

# Gate: Run test suite with pytest
run_tests() {
    echo "=== Gate: Test Suite ==="

    if ! command -v pytest &> /dev/null; then
        print_warning "pytest not installed, skipping"
        return $EXIT_SUCCESS
    fi

    # Check if tests directory exists
    if [[ ! -d "tests" ]]; then
        print_warning "No tests directory found, skipping"
        return $EXIT_SUCCESS
    fi

    # Run tests with short traceback
    if pytest tests/ -v --tb=short --maxfail=5 2>&1; then
        print_success "All tests passed"
        return $EXIT_SUCCESS
    else
        print_error "Test failures detected"
        return $EXIT_FAILURE
    fi
}

# Gate: Check no uncommitted large files
check_file_sizes() {
    echo "=== Gate: File Size Check ==="

    # Maximum file size in bytes (10MB)
    MAX_SIZE=$((10 * 1024 * 1024))

    # Get list of staged files
    STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR)

    if [[ -z "$STAGED_FILES" ]]; then
        print_success "No staged files to check"
        return $EXIT_SUCCESS
    fi

    LARGE_FILES=()

    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            SIZE=$(wc -c < "$file")
            if [[ $SIZE -gt $MAX_SIZE ]]; then
                LARGE_FILES+=("$file ($(numfmt --to=iec-i --suffix=B $SIZE))")
            fi
        fi
    done <<< "$STAGED_FILES"

    if [[ ${#LARGE_FILES[@]} -gt 0 ]]; then
        print_error "Large files detected (>10MB):"
        for file in "${LARGE_FILES[@]}"; do
            print_info "$file"
        done
        print_info "Consider using Git LFS for large files"
        return $EXIT_FAILURE
    fi

    print_success "No large files detected"
    return $EXIT_SUCCESS
}

# Gate: Check for common security issues
check_security() {
    echo "=== Gate: Security Check ==="

    # Check for potential secrets in staged files
    STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR)

    if [[ -z "$STAGED_FILES" ]]; then
        print_success "No staged files to check"
        return $EXIT_SUCCESS
    fi

    # Patterns to detect (API keys, passwords, tokens)
    SECURITY_PATTERNS=(
        "password\\s*=\\s*['\"][^'\"]{8,}"
        "api_key\\s*=\\s*['\"][^'\"]{16,}"
        "secret\\s*=\\s*['\"][^'\"]{16,}"
        "token\\s*=\\s*['\"][^'\"]{16,}"
        "AKIA[0-9A-Z]{16}"  # AWS access key
        "sk_live_[0-9a-zA-Z]{24}"  # Stripe key
    )

    ISSUES_FOUND=0

    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            for pattern in "${SECURITY_PATTERNS[@]}"; do
                if grep -iEq "$pattern" "$file"; then
                    print_warning "Potential secret detected in: $file"
                    ISSUES_FOUND=$((ISSUES_FOUND + 1))
                fi
            done
        fi
    done <<< "$STAGED_FILES"

    if [[ $ISSUES_FOUND -gt 0 ]]; then
        print_error "Security issues detected ($ISSUES_FOUND potential secrets)"
        print_info "Review files for hardcoded credentials"
        return $EXIT_FAILURE
    fi

    print_success "No security issues detected"
    return $EXIT_SUCCESS
}

# Gate: Check Python imports are valid
check_python_imports() {
    echo "=== Gate: Python Import Check ==="

    if ! command -v python3 &> /dev/null; then
        print_warning "python3 not found, skipping"
        return $EXIT_SUCCESS
    fi

    # Find all Python files
    PYTHON_FILES=$(find scripts tests -name "*.py" 2>/dev/null || true)

    if [[ -z "$PYTHON_FILES" ]]; then
        print_success "No Python files to check"
        return $EXIT_SUCCESS
    fi

    FAILED_FILES=()

    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            # Try to compile the file (syntax check)
            if ! python3 -m py_compile "$file" 2>/dev/null; then
                FAILED_FILES+=("$file")
            fi
        fi
    done <<< "$PYTHON_FILES"

    if [[ ${#FAILED_FILES[@]} -gt 0 ]]; then
        print_error "Python syntax errors detected:"
        for file in "${FAILED_FILES[@]}"; do
            print_info "$file"
        done
        return $EXIT_FAILURE
    fi

    print_success "All Python files have valid syntax"
    return $EXIT_SUCCESS
}

# Gate: Check for TODO/FIXME markers
check_todos() {
    echo "=== Gate: TODO/FIXME Check ==="

    # Get staged files
    STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR)

    if [[ -z "$STAGED_FILES" ]]; then
        print_success "No staged files to check"
        return $EXIT_SUCCESS
    fi

    TODO_COUNT=0

    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            COUNT=$(grep -ic "TODO\|FIXME" "$file" 2>/dev/null || true)
            TODO_COUNT=$((TODO_COUNT + COUNT))
        fi
    done <<< "$STAGED_FILES"

    if [[ $TODO_COUNT -gt 0 ]]; then
        print_warning "$TODO_COUNT TODO/FIXME markers found in staged files"
        print_info "Consider resolving before merge"
        # Don't fail, just warn
    else
        print_success "No TODO/FIXME markers in staged files"
    fi

    return $EXIT_SUCCESS
}

# Main gate runner
run_all_gates() {
    echo ""
    echo "========================================"
    echo "  IRIS Gate CI Validation"
    echo "========================================"
    echo ""

    FAILED_GATES=()

    # Run each gate
    if ! check_python_imports; then
        FAILED_GATES+=("python_imports")
    fi
    echo ""

    if ! check_code_style; then
        FAILED_GATES+=("code_style")
    fi
    echo ""

    if ! check_code_format; then
        FAILED_GATES+=("code_format")
    fi
    echo ""

    if ! run_tests; then
        FAILED_GATES+=("tests")
    fi
    echo ""

    if ! check_file_sizes; then
        FAILED_GATES+=("file_sizes")
    fi
    echo ""

    if ! check_security; then
        FAILED_GATES+=("security")
    fi
    echo ""

    if ! check_todos; then
        FAILED_GATES+=("todos")
    fi
    echo ""

    # Summary
    echo "========================================"
    if [[ ${#FAILED_GATES[@]} -eq 0 ]]; then
        print_success "All gates passed!"
        echo "========================================"
        return $EXIT_SUCCESS
    else
        print_error "Gates failed: ${FAILED_GATES[*]}"
        echo "========================================"
        return $EXIT_FAILURE
    fi
}

# CLI entry point
main() {
    # Parse command line arguments
    if [[ $# -eq 0 ]]; then
        # No arguments, run all gates
        run_all_gates
        exit $?
    fi

    # Run specific gate
    case "$1" in
        check_clean_tree)
            check_clean_tree
            exit $?
            ;;
        check_code_style)
            check_code_style
            exit $?
            ;;
        check_code_format)
            check_code_format
            exit $?
            ;;
        run_tests)
            run_tests
            exit $?
            ;;
        check_file_sizes)
            check_file_sizes
            exit $?
            ;;
        check_security)
            check_security
            exit $?
            ;;
        check_python_imports)
            check_python_imports
            exit $?
            ;;
        check_todos)
            check_todos
            exit $?
            ;;
        all)
            run_all_gates
            exit $?
            ;;
        --help|-h)
            echo "Usage: $0 [GATE]"
            echo ""
            echo "Available gates:"
            echo "  check_clean_tree      - Verify working tree is clean"
            echo "  check_code_style      - Run ruff style check"
            echo "  check_code_format     - Check code formatting"
            echo "  run_tests             - Run pytest test suite"
            echo "  check_file_sizes      - Check for large files"
            echo "  check_security        - Scan for hardcoded secrets"
            echo "  check_python_imports  - Validate Python syntax"
            echo "  check_todos           - Count TODO/FIXME markers"
            echo "  all                   - Run all gates (default)"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all gates"
            echo "  $0 run_tests          # Run only tests"
            echo "  $0 check_security     # Run only security check"
            exit 0
            ;;
        *)
            print_error "Unknown gate: $1"
            echo "Run '$0 --help' for usage"
            exit $EXIT_FAILURE
            ;;
    esac
}

# Run main
main "$@"
