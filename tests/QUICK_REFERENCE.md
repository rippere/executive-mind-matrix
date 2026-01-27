# Testing Quick Reference

## Installation

```bash
pip install -r requirements-test.txt
```

## Common Commands

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov=config --cov=main --cov-report=html

# Specific file
pytest tests/test_models.py

# Specific test
pytest tests/test_models.py::TestScenarioOption::test_valid_scenario_option

# By marker
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m api           # API tests
pytest -m "not slow"    # Exclude slow tests
```

### Using Test Runner Script

```bash
./run_tests.sh              # All tests
./run_tests.sh unit         # Unit tests
./run_tests.sh coverage     # With coverage report
./run_tests.sh help         # Show all commands
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_models.py           # Model validation
├── test_settings.py         # Configuration
├── test_diff_logger.py      # Diff calculation
├── test_agent_router.py     # Agent logic
├── test_notion_poller.py    # Polling logic
├── test_integration.py      # End-to-end workflows
└── test_api.py              # API endpoints
```

## Common Fixtures

```python
# From conftest.py
def test_example(
    mock_notion_client,          # Mocked Notion API
    mock_anthropic_client,       # Mocked Anthropic API
    sample_notion_intent,        # Sample intent data
    sample_agent_analysis,       # Sample analysis
    sample_dialectic_output      # Sample dialectic result
):
    pass
```

## Async Tests

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result is not None
```

## Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("Low", RiskLevel.LOW),
    ("High", RiskLevel.HIGH),
])
def test_risk_levels(input, expected):
    assert RiskLevel(input) == expected
```

## Mocking Examples

### Mock Notion Response

```python
mock_notion_client.databases.query.return_value = {
    "results": [{"id": "page_123", "properties": {}}]
}
```

### Mock Anthropic Response

```python
mock_response = MagicMock()
mock_response.content = [MagicMock(text='{"test": "data"}')]
mock_anthropic_client.messages.create.return_value = mock_response
```

## Coverage Goals

- **Overall**: 80%+
- **Unit Tests**: 90%+
- **Integration Tests**: 70%+
- **API Tests**: 85%+

## Test Markers

```python
@pytest.mark.unit           # Unit test
@pytest.mark.integration    # Integration test
@pytest.mark.api            # API test
@pytest.mark.slow           # Slow running test
@pytest.mark.asyncio        # Async test
```

## Debugging

```bash
# Verbose output
pytest -v

# Very verbose
pytest -vv

# Show print statements
pytest -s

# Debug failing test
pytest --pdb

# Re-run last failures
pytest --lf
```

## CI/CD Integration

```yaml
# .github/workflows/tests.yml
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v2
```

## Troubleshooting

### ImportError
```bash
# Ensure running from project root
cd /home/rippere/Projects/executive-mind-matrix
pytest
```

### ValidationError for env vars
```bash
# Set test environment variables
export NOTION_API_KEY=test_key
export ANTHROPIC_API_KEY=test_key
pytest
```

### Async tests not running
```bash
pip install pytest-asyncio
```

## Resources

- Full docs: `tests/README.md`
- Test runner: `./run_tests.sh help`
- Coverage report: `htmlcov/index.html`
