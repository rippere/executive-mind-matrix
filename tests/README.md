# Executive Mind Matrix - Testing Documentation

Comprehensive test suite for the Executive Mind Matrix project.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Coverage Requirements](#coverage-requirements)
- [Writing Tests](#writing-tests)
- [Mock Data Examples](#mock-data-examples)
- [Troubleshooting](#troubleshooting)

## Overview

The test suite provides comprehensive coverage of:

- **Unit Tests**: Individual component testing with mocked dependencies
- **Integration Tests**: Multi-component workflow testing
- **API Tests**: FastAPI endpoint testing
- **Model Validation**: Pydantic schema validation testing

### Test Stack

- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Advanced mocking utilities
- **respx**: HTTP mocking (if needed)

## Quick Start

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Run All Tests

```bash
pytest
```

### 3. Run with Coverage

```bash
pytest --cov=app --cov=config --cov=main --cov-report=html
```

### 4. View Coverage Report

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── test_models.py           # Unit tests for app/models.py
├── test_settings.py         # Unit tests for config/settings.py
├── test_diff_logger.py      # Unit tests for app/diff_logger.py
├── test_agent_router.py     # Unit tests for app/agent_router.py
├── test_notion_poller.py    # Unit tests for app/notion_poller.py
├── test_integration.py      # Integration tests for workflows
├── test_api.py              # API endpoint tests
└── README.md                # This file
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_models.py
```

### Run Specific Test Class

```bash
pytest tests/test_models.py::TestScenarioOption
```

### Run Specific Test Function

```bash
pytest tests/test_models.py::TestScenarioOption::test_valid_scenario_option
```

### Run Tests by Marker

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# API tests only
pytest -m api

# Async tests only
pytest -m async

# Slow tests only
pytest -m slow

# Notion API tests
pytest -m notion

# Anthropic API tests
pytest -m anthropic
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests with Debug Output

```bash
pytest -vv --tb=long
```

### Run Failed Tests Only

```bash
# Run tests that failed in the last run
pytest --lf

# Run failed tests first, then remaining
pytest --ff
```

### Run Tests in Parallel

```bash
# Install pytest-xdist first
pip install pytest-xdist

# Run on 4 cores
pytest -n 4
```

## Test Categories

### Unit Tests (`-m unit`)

Test individual components in isolation with mocked dependencies.

**Files:**
- `test_models.py` - Model validation and Pydantic schemas
- `test_settings.py` - Configuration loading and validation
- `test_diff_logger.py` - Diff calculation and training data logging
- `test_agent_router.py` - Intent classification and agent analysis
- `test_notion_poller.py` - Polling logic and intent processing

**Example:**
```bash
pytest -m unit tests/test_models.py
```

### Integration Tests (`-m integration`)

Test multi-component workflows and interactions.

**File:** `test_integration.py`

**Test Scenarios:**
- Full poller cycle (inbox → classification → intent creation)
- Dialectic flow (growth + risk analysis + synthesis)
- Training data capture (diff logging)
- End-to-end workflows

**Example:**
```bash
pytest -m integration
```

### API Tests (`-m api`)

Test FastAPI endpoints, request/response handling, and error cases.

**File:** `test_api.py`

**Endpoints Tested:**
- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /trigger-poll` - Manual poll trigger
- `POST /analyze-intent/{intent_id}` - Manual analysis
- `POST /dialectic/{intent_id}` - Adversarial dialectic
- `GET /metrics/agent/{agent_name}` - Agent performance
- `POST /log-settlement` - Training data logging

**Example:**
```bash
pytest -m api
```

## Coverage Requirements

### Minimum Coverage Targets

- **Overall**: 80% (enforced by pytest.ini)
- **Unit Tests**: 90%+
- **Integration Tests**: 70%+
- **API Tests**: 85%+

### Check Coverage

```bash
# Generate coverage report
pytest --cov=app --cov=config --cov=main --cov-report=term-missing

# Generate HTML report
pytest --cov=app --cov=config --cov=main --cov-report=html

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80
```

### Coverage Reports

Coverage reports are generated in:
- **Terminal**: `--cov-report=term-missing`
- **HTML**: `htmlcov/index.html`
- **XML**: `coverage.xml` (for CI/CD)

## Writing Tests

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Using Fixtures

Fixtures are defined in `conftest.py` and available to all tests.

**Common Fixtures:**

```python
def test_with_notion_client(mock_notion_client):
    """Use mocked Notion client."""
    # mock_notion_client is automatically injected
    assert mock_notion_client is not None

def test_with_anthropic_client(mock_anthropic_client):
    """Use mocked Anthropic client."""
    assert mock_anthropic_client is not None

def test_with_sample_data(sample_notion_intent):
    """Use sample test data."""
    assert sample_notion_intent.id == "intent_123"
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async functions."""
    result = await some_async_function()
    assert result is not None
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("Low", RiskLevel.LOW),
    ("Medium", RiskLevel.MEDIUM),
    ("High", RiskLevel.HIGH),
])
def test_risk_levels(input, expected):
    """Test multiple inputs with parametrize."""
    assert RiskLevel(input) == expected
```

### Mocking External APIs

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mocked_api(mock_anthropic_client):
    """Mock external API calls."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"test": "data"}')]
    mock_anthropic_client.messages.create.return_value = mock_response

    # Test your code
    result = await call_anthropic_api()

    # Verify
    mock_anthropic_client.messages.create.assert_called_once()
```

## Mock Data Examples

### Sample Notion Intent

```python
from app.models import NotionIntent, IntentStatus, RiskLevel, AgentPersona

intent = NotionIntent(
    id="intent_123",
    title="Launch SaaS Product",
    description="Build and launch a project management SaaS",
    status=IntentStatus.PENDING,
    risk_level=RiskLevel.HIGH,
    agent_persona=AgentPersona.ENTREPRENEUR,
    projected_impact=9,
    success_criteria="Get 100 paying customers"
)
```

### Sample Agent Analysis

```python
from app.models import AgentAnalysis, ScenarioOption

analysis = AgentAnalysis(
    scenario_options=[
        ScenarioOption(
            option="A",
            description="Move fast with MVP",
            pros=["Quick to market", "Low cost"],
            cons=["Technical debt"],
            risk=2,
            impact=8
        )
    ],
    recommended_option="A",
    recommendation_rationale="Speed to market is critical",
    risk_assessment="Low technical risk",
    required_resources={
        "time": "4 weeks",
        "money": "$5000",
        "tools": ["AWS", "Stripe"],
        "people": ["Developer"]
    },
    task_generation_template=[
        "Set up infrastructure",
        "Build MVP",
        "Launch"
    ]
)
```

### Sample Dialectic Output

```python
from app.models import DialecticOutput

dialectic = DialecticOutput(
    intent_id="intent_123",
    growth_perspective=growth_analysis,  # AgentAnalysis
    risk_perspective=risk_analysis,       # AgentAnalysis
    synthesis="Balance speed with quality",
    recommended_path="Launch MVP in 60 days with core features",
    conflict_points=[
        "Speed vs Quality",
        "Cost vs Features",
        "Risk tolerance"
    ]
)
```

### Sample Settlement Diff

```python
from app.models import SettlementDiff
from datetime import datetime

diff = SettlementDiff(
    intent_id="intent_123",
    timestamp=datetime.utcnow(),
    original_plan={
        "option": "A",
        "tasks": ["Task 1", "Task 2"],
        "budget": 5000
    },
    final_plan={
        "option": "B",
        "tasks": ["Task 1", "Task 3"],
        "budget": 7500
    },
    diff_summary={
        "values_changed": {
            "option": {"old": "A", "new": "B"},
            "budget": {"old": 5000, "new": 7500}
        }
    },
    user_modifications=[
        "Changed option from A to B",
        "Modified task list",
        "Increased budget by $2500"
    ],
    acceptance_rate=0.67
)
```

## Troubleshooting

### Tests Failing Due to Missing Environment Variables

**Problem:** Tests fail with "ValidationError" for missing environment variables.

**Solution:** Environment variables are set in `pytest.ini`. If you need different values:

```bash
# Set environment variables before running tests
export NOTION_API_KEY=test_key
export ANTHROPIC_API_KEY=test_key
pytest
```

### Async Tests Not Running

**Problem:** Async tests are skipped or fail with "coroutine was never awaited".

**Solution:** Ensure `pytest-asyncio` is installed and use `@pytest.mark.asyncio`:

```bash
pip install pytest-asyncio
```

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result
```

### Import Errors

**Problem:** Tests fail with "ModuleNotFoundError".

**Solution:** Ensure you're running tests from the project root:

```bash
cd /home/rippere/Projects/executive-mind-matrix
pytest
```

### Coverage Not Working

**Problem:** Coverage report shows 0% or missing files.

**Solution:** Ensure `pytest-cov` is installed and paths are correct:

```bash
pip install pytest-cov
pytest --cov=app --cov=config --cov=main
```

### Mock Not Working

**Problem:** Real API calls are being made instead of using mocks.

**Solution:** Ensure you're using the fixtures or patching correctly:

```python
# Use fixture
def test_with_fixture(mock_notion_client):
    # mock_notion_client is already patched
    pass

# Or patch manually
@patch('app.agent_router.AsyncAnthropic')
def test_with_patch(mock_anthropic):
    pass
```

### Tests Running Slowly

**Problem:** Tests take too long to run.

**Solution:**

1. Run specific test files: `pytest tests/test_models.py`
2. Run tests in parallel: `pytest -n 4`
3. Skip slow tests: `pytest -m "not slow"`

### Database Connection Errors

**Problem:** Tests fail trying to connect to real databases.

**Solution:** All database calls should be mocked. Check that:

1. Fixtures are being used correctly
2. Patches are applied in the right scope
3. Mock responses are properly configured

### Coverage Threshold Failing

**Problem:** Tests pass but coverage check fails.

**Solution:**

1. Check which files/lines are missing coverage:
   ```bash
   pytest --cov=app --cov-report=term-missing
   ```

2. Add tests for uncovered lines

3. Adjust threshold temporarily if needed:
   ```bash
   pytest --cov-fail-under=70  # Lower threshold
   ```

## Best Practices

### 1. Test Isolation

Each test should be independent and not rely on other tests.

```python
# Good: Self-contained test
def test_create_intent():
    intent = NotionIntent(id="123", title="Test", ...)
    assert intent.id == "123"

# Bad: Relies on global state
intent = None
def test_create_intent():
    global intent
    intent = NotionIntent(...)

def test_use_intent():
    assert intent is not None  # Fails if previous test skipped
```

### 2. Use Descriptive Test Names

```python
# Good: Clear what's being tested
def test_acceptance_rate_with_no_changes_returns_100_percent():
    pass

# Bad: Unclear
def test_acceptance():
    pass
```

### 3. Follow AAA Pattern

Arrange, Act, Assert:

```python
def test_calculate_diff():
    # Arrange
    original = {"key": "value1"}
    final = {"key": "value2"}

    # Act
    diff = calculate_diff(original, final)

    # Assert
    assert diff.acceptance_rate < 1.0
```

### 4. Test Edge Cases

```python
def test_empty_input():
    """Test with empty input."""

def test_null_input():
    """Test with None input."""

def test_invalid_input():
    """Test with invalid input."""

def test_boundary_values():
    """Test min/max values."""
```

### 5. Keep Tests Fast

- Mock external API calls
- Use in-memory databases if needed
- Avoid unnecessary sleeps
- Run heavy tests separately with markers

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt

    - name: Run tests with coverage
      run: |
        pytest --cov=app --cov=config --cov=main --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)

## Support

For questions or issues with the test suite:

1. Check this documentation
2. Review test examples in the codebase
3. Check pytest documentation
4. Create an issue in the project repository
