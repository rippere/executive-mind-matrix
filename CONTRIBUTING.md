# Contributing to Executive Mind Matrix

Thank you for your interest in contributing to Executive Mind Matrix! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Docker (optional, for containerized development)
- Railway CLI (optional, for deployment)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/executive-mind-matrix.git
   cd executive-mind-matrix
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/rippere/executive-mind-matrix.git
   ```

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
```

### 3. Set Up Pre-commit Hooks

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys and configuration
# IMPORTANT: Never commit .env file to the repository
```

### 5. Verify Setup

```bash
# Run tests
pytest

# Run linters
ruff check .
black --check .
mypy app/ config/ main.py

# Start the application
python main.py
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications
- `chore/` - Maintenance tasks

### 2. Make Your Changes

- Write clean, maintainable code
- Follow the code style guidelines
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=config

# Run specific tests
pytest tests/test_specific.py

# Run linting
ruff check .
black --check .
isort --check-only .

# Run type checking
mypy app/ config/ main.py
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature"
```

See [Commit Message Guidelines](#commit-message-guidelines) below.

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style Guidelines

### Python Style

We follow PEP 8 with some modifications configured in `pyproject.toml`:

- Line length: 100 characters
- Use double quotes for strings
- Use type hints where possible
- Write docstrings for all public functions and classes

### Code Formatting Tools

- **Black**: Code formatting
- **isort**: Import sorting
- **Ruff**: Linting and code quality

These tools are automatically run by pre-commit hooks.

### Code Quality Standards

```python
# Good example
from typing import Optional

def process_intent(
    intent_id: str,
    context: Optional[dict] = None
) -> dict:
    """
    Process an intent and return the result.

    Args:
        intent_id: The unique identifier for the intent
        context: Optional context information

    Returns:
        Dictionary containing the processed result

    Raises:
        ValueError: If intent_id is invalid
    """
    if not intent_id:
        raise ValueError("Intent ID cannot be empty")

    result = {"intent_id": intent_id, "status": "processed"}
    if context:
        result["context"] = context

    return result
```

### Import Ordering

```python
# Standard library imports
import asyncio
import sys
from typing import Optional

# Third-party imports
from fastapi import FastAPI
from pydantic import BaseModel

# Local imports
from app.notion_poller import NotionPoller
from config.settings import settings
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
├── fixtures/      # Test fixtures and data
└── conftest.py    # Pytest configuration
```

### Writing Tests

```python
import pytest
from app.agent_router import AgentRouter


class TestAgentRouter:
    """Test suite for AgentRouter."""

    @pytest.fixture
    def router(self):
        """Create a test router instance."""
        return AgentRouter()

    def test_classify_intent(self, router):
        """Test intent classification."""
        result = router.classify_intent("Should I invest in stocks?")
        assert result in ["Strategic", "Operational", "Reference"]

    @pytest.mark.asyncio
    async def test_async_analysis(self, router):
        """Test asynchronous analysis."""
        result = await router.analyze("test_intent_id")
        assert result is not None
```

### Test Requirements

- All new features must include tests
- Maintain or improve code coverage (target: 80%+)
- Tests should be fast and independent
- Use fixtures for common test data
- Mock external API calls

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```bash
# Feature
git commit -m "feat(agent): add new quant analysis persona"

# Bug fix
git commit -m "fix(poller): handle connection timeouts properly"

# Documentation
git commit -m "docs: update installation instructions"

# Multiple changes
git commit -m "feat(api): add new endpoint for metrics

- Add /metrics/summary endpoint
- Update API documentation
- Add tests for new endpoint

Closes #123"
```

## Pull Request Process

### Before Submitting

1. Update your branch with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Ensure all tests pass:
   ```bash
   pytest
   ```

3. Ensure code quality checks pass:
   ```bash
   ruff check .
   black --check .
   mypy app/ config/ main.py
   ```

4. Update documentation if needed

### Pull Request Template

When creating a PR, include:

- Clear description of the changes
- Related issue numbers (if applicable)
- Testing performed
- Screenshots (for UI changes)
- Breaking changes (if any)

### Review Process

1. At least one maintainer review is required
2. All CI checks must pass
3. Code coverage should not decrease
4. Address review feedback promptly
5. Keep the PR focused and small when possible

### After Approval

- Maintainers will merge your PR
- Delete your feature branch after merge

## Issue Reporting

### Bug Reports

Include:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and logs
- Screenshots if applicable

### Feature Requests

Include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)
- Alternatives considered

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `question`: Further information requested

## Development Best Practices

### 1. Keep PRs Small

- Focus on one feature or fix per PR
- Break large changes into multiple PRs
- Makes review process faster and easier

### 2. Write Descriptive Comments

```python
# Good
# Calculate risk-adjusted return using Sharpe ratio
sharpe_ratio = (returns - risk_free_rate) / std_dev

# Bad
# Calculate something
result = (a - b) / c
```

### 3. Handle Errors Properly

```python
from loguru import logger

try:
    result = await api_call()
except APIError as e:
    logger.error(f"API call failed: {e}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
```

### 4. Use Type Hints

```python
from typing import Optional, List, Dict

async def fetch_intents(
    status: str,
    limit: Optional[int] = None
) -> List[Dict[str, str]]:
    """Fetch intents with given status."""
    ...
```

### 5. Document Complex Logic

```python
def dialectic_synthesis(
    growth_view: dict,
    risk_view: dict
) -> dict:
    """
    Synthesize growth and risk perspectives into unified recommendation.

    The synthesis algorithm:
    1. Identifies conflict points between perspectives
    2. Weighs each perspective based on intent context
    3. Generates balanced recommendation
    4. Provides reasoning for the synthesis

    Args:
        growth_view: Output from growth-oriented agent
        risk_view: Output from risk-averse agent

    Returns:
        Synthesized recommendation with reasoning
    """
    ...
```

## Questions?

- Check existing issues and discussions
- Ask in GitHub Discussions
- Email the maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Executive Mind Matrix!
