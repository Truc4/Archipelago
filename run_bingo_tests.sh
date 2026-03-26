#!/bin/bash
# Bingo Test Runner
# Runs all bingo tests and reports results

set -e

echo "========================================"
echo "  Archipelago Bingo Test Suite"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_file=$1
    local test_name=$2

    echo "----------------------------------------"
    echo "Running: $test_name"
    echo "----------------------------------------"

    if python3 "$test_file"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
    echo ""
}

# Run tests
echo "Starting test run..."
echo ""

# 1. Unit tests (fast)
if [ -f "test_bingo_simple.py" ]; then
    run_test "test_bingo_simple.py" "Unit Tests (Core Logic)"
fi

# 2. Web tracker tests (fast)
if [ -f "test_bingo_webtracker.py" ]; then
    run_test "test_bingo_webtracker.py" "Web Tracker Tests (Co-op Mode)"
fi

# 3. Integration tests (slower - optional with flag)
if [ "${RUN_INTEGRATION}" = "1" ] || [ "$1" = "--full" ]; then
    if [ -f "test_bingo_integration.py" ]; then
        echo -e "${YELLOW}Note: Integration tests may take several minutes...${NC}"
        run_test "test_bingo_integration.py" "Integration Tests (Real Games)"
    fi
else
    echo "----------------------------------------"
    echo "Skipping Integration Tests (use --full to run)"
    echo "  To include: ./run_bingo_tests.sh --full"
    echo "  Or: RUN_INTEGRATION=1 ./run_bingo_tests.sh"
    echo "----------------------------------------"
    echo ""
fi

# Summary
echo "========================================"
echo "  Test Results Summary"
echo "========================================"
echo ""
echo "Total Tests:  $TOTAL_TESTS"
echo -e "${GREEN}Passed:${NC}       $PASSED_TESTS"
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}Failed:${NC}       $FAILED_TESTS"
else
    echo -e "${GREEN}Failed:${NC}       $FAILED_TESTS"
fi
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
