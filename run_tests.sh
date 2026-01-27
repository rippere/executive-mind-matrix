#!/bin/bash

# Executive Mind Matrix - Test Runner Script
# Provides convenient commands for running different test suites

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Executive Mind Matrix - Test Runner${NC}"
echo ""

# Default action
ACTION=${1:-all}

case "$ACTION" in
    "all")
        echo -e "${GREEN}Running all tests...${NC}"
        pytest -v
        ;;

    "unit")
        echo -e "${GREEN}Running unit tests...${NC}"
        pytest -v -m unit
        ;;

    "integration")
        echo -e "${GREEN}Running integration tests...${NC}"
        pytest -v -m integration
        ;;

    "api")
        echo -e "${GREEN}Running API tests...${NC}"
        pytest -v -m api
        ;;

    "coverage")
        echo -e "${GREEN}Running tests with coverage report...${NC}"
        pytest --cov=app --cov=config --cov=main --cov-report=term-missing --cov-report=html
        echo ""
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;

    "fast")
        echo -e "${GREEN}Running fast tests only (excluding slow tests)...${NC}"
        pytest -v -m "not slow"
        ;;

    "failed")
        echo -e "${GREEN}Re-running failed tests from last run...${NC}"
        pytest --lf -v
        ;;

    "watch")
        echo -e "${GREEN}Running tests in watch mode...${NC}"
        echo "Note: This requires pytest-watch to be installed (pip install pytest-watch)"
        ptw -- -v
        ;;

    "debug")
        echo -e "${GREEN}Running tests with debug output...${NC}"
        pytest -vv --tb=long -s
        ;;

    "parallel")
        echo -e "${GREEN}Running tests in parallel...${NC}"
        echo "Note: This requires pytest-xdist to be installed (pip install pytest-xdist)"
        pytest -v -n auto
        ;;

    "models")
        echo -e "${GREEN}Running model tests...${NC}"
        pytest -v tests/test_models.py
        ;;

    "settings")
        echo -e "${GREEN}Running settings tests...${NC}"
        pytest -v tests/test_settings.py
        ;;

    "diff-logger")
        echo -e "${GREEN}Running diff logger tests...${NC}"
        pytest -v tests/test_diff_logger.py
        ;;

    "agent-router")
        echo -e "${GREEN}Running agent router tests...${NC}"
        pytest -v tests/test_agent_router.py
        ;;

    "notion-poller")
        echo -e "${GREEN}Running notion poller tests...${NC}"
        pytest -v tests/test_notion_poller.py
        ;;

    "help")
        echo "Usage: ./run_tests.sh [command]"
        echo ""
        echo "Available commands:"
        echo "  all              Run all tests (default)"
        echo "  unit             Run unit tests only"
        echo "  integration      Run integration tests only"
        echo "  api              Run API tests only"
        echo "  coverage         Run tests with coverage report"
        echo "  fast             Run fast tests (exclude slow tests)"
        echo "  failed           Re-run only failed tests from last run"
        echo "  watch            Run tests in watch mode (requires pytest-watch)"
        echo "  debug            Run tests with verbose debug output"
        echo "  parallel         Run tests in parallel (requires pytest-xdist)"
        echo "  models           Run model validation tests"
        echo "  settings         Run settings configuration tests"
        echo "  diff-logger      Run diff logger tests"
        echo "  agent-router     Run agent router tests"
        echo "  notion-poller    Run notion poller tests"
        echo "  help             Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                 # Run all tests"
        echo "  ./run_tests.sh unit            # Run unit tests only"
        echo "  ./run_tests.sh coverage        # Generate coverage report"
        echo "  ./run_tests.sh models          # Test models only"
        ;;

    *)
        echo -e "${RED}Unknown command: $ACTION${NC}"
        echo "Run './run_tests.sh help' for available commands"
        exit 1
        ;;
esac
