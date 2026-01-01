# Contributing to ClaudeBox

Thank you for your interest in contributing to ClaudeBox! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Ways to Contribute

There are many ways to contribute to ClaudeBox:

- **Code**: Fix bugs, add features, improve performance
- **Documentation**: Improve docs, write tutorials, fix typos
- **Examples**: Create new example files demonstrating features
- **Issues**: Report bugs, suggest features, ask questions
- **Reviews**: Review pull requests, provide feedback
- **Skills**: Contribute new built-in skills
- **Testing**: Write tests, improve test coverage

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Docker installed and running
- BoxLite micro-VM runtime
- Git

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/boxlite-labs/claudebox.git
cd claudebox

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### Authentication Setup

```bash
# Set your Claude Code OAuth token
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/claudebox --cov-report=html

# Run specific test file
pytest tests/test_skills.py -v

# Skip real integration tests (faster)
pytest tests/ -v -m "not real"
```

### Code Quality

```bash
# Run linter (ruff)
ruff check src/ tests/

# Auto-fix linting issues
ruff check --fix src/ tests/

# Run type checker (mypy)
mypy src/claudebox/

# Format code
ruff format src/ tests/
```

## Pull Request Process

### 1. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write clean, readable code
- Add type hints to all functions
- Include docstrings for public API
- Write tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Ensure all tests pass
pytest tests/ -v

# Check code quality
ruff check src/ tests/
mypy src/claudebox/

# Verify examples still work
python examples/01_basic_usage.py
```

### 4. Commit Your Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Good commit messages
git commit -m "feat: Add support for custom templates"
git commit -m "fix: Resolve session cleanup race condition"
git commit -m "docs: Add RL training tutorial"
git commit -m "test: Add integration tests for skills"

# Commit types
# feat:     New feature
# fix:      Bug fix
# docs:     Documentation only
# test:     Adding or updating tests
# refactor: Code change that neither fixes a bug nor adds a feature
# perf:     Performance improvement
# chore:    Changes to build process or auxiliary tools
```

### 5. Push and Create PR

```bash
# Push your branch
git push origin feature/your-feature-name

# Go to GitHub and create a Pull Request
# Fill out the PR template with:
# - Description of changes
# - Related issue number (if applicable)
# - Testing performed
# - Screenshots (if UI changes)
```

### 6. Code Review

- Respond to review feedback promptly
- Make requested changes in new commits
- Don't force-push after review has started
- Mark conversations as resolved when addressed

### 7. Merge

Once approved and CI passes:
- Maintainer will merge your PR
- Your contribution will be in the next release!

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use `ruff` for linting (configured in `pyproject.toml`)
- Use `mypy` for type checking
- Maximum line length: 100 characters

### Type Hints

All public functions must have type hints:

```python
# Good
def create_session(session_id: str, workspace_dir: str | None = None) -> SessionWorkspace:
    """Create a new session workspace."""
    ...

# Bad
def create_session(session_id, workspace_dir=None):
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def code(self, prompt: str, timeout: int = 120) -> CodeResult:
    """
    Execute Claude Code CLI with the given prompt.

    Args:
        prompt: Natural language instruction for Claude Code
        timeout: Maximum execution time in seconds

    Returns:
        CodeResult containing response, success status, and metadata

    Raises:
        TimeoutError: If execution exceeds timeout
        RuntimeError: If box is not initialized

    Example:
        >>> async with ClaudeBox() as box:
        ...     result = await box.code("Create a hello world script")
        ...     print(result.response)
    """
```

### Imports

- Group imports: stdlib, third-party, local
- Use `from __future__ import annotations` for forward references
- Import `Callable` from `collections.abc`, not `typing`
- Sort imports with `ruff`

```python
from __future__ import annotations

import os
import uuid
from collections.abc import Callable

from boxlite import Boxlite, BoxOptions

from claudebox.results import CodeResult
from claudebox.session import SessionManager
```

## Testing Requirements

### Test Coverage

- Maintain >80% code coverage
- Write unit tests for new functions
- Write integration tests for new features
- Add examples demonstrating new features

### Test Structure

```python
import pytest

from claudebox import ClaudeBox, Skill

def test_feature_basic():
    """Test basic functionality."""
    # Arrange
    skill = Skill(name="test", description="Test skill")

    # Act
    result = skill.validate()

    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_feature_async():
    """Test async functionality."""
    async with ClaudeBox() as box:
        result = await box.code("test")
        assert result.success
```

### Running Specific Tests

```bash
# Run tests for a specific module
pytest tests/test_skills.py -v

# Run a specific test
pytest tests/test_skills.py::test_skill_creation -v

# Run tests matching a pattern
pytest tests/ -k "skill" -v
```

## Documentation Guidelines

### Writing Documentation

- **Be clear and concise** - Get to the point quickly
- **Show examples** - Include runnable code examples
- **Link related docs** - Help users discover related features
- **Keep it updated** - Update docs when code changes

### Documentation Structure

- Guides: Explain how to do something (imperative)
- API Reference: Describe what something does (descriptive)
- Architecture: Explain why/how things work internally

### Example Documentation

````markdown
# Sessions Guide

Learn how to use persistent and ephemeral sessions in ClaudeBox.

## Ephemeral Sessions

Ephemeral sessions auto-cleanup after use:

```python
async with ClaudeBox() as box:
    result = await box.code("Create hello.txt")
# Session is automatically cleaned up
```

## Persistent Sessions

Persistent sessions survive across multiple runs:

```python
# Create session
async with ClaudeBox(session_id="my-project") as box:
    await box.code("npm install")

# Reconnect later
async with ClaudeBox.reconnect("my-project") as box:
    await box.code("npm test")
```
````

## Contributing Skills

Skills extend ClaudeBox capabilities. To contribute a new skill:

### 1. Create the Skill

```python
from claudebox import Skill

NOTIFICATION_SKILL = Skill(
    name="notification",
    description="Send notifications via Slack, Discord, email",
    install_cmd="pip3 install slack-sdk discord-webhook",
    requirements=["slack-sdk", "discord-webhook"],
    env_vars={
        "SLACK_TOKEN": "",
        "DISCORD_WEBHOOK_URL": "",
    },
)
```

### 2. Test the Skill

```python
import pytest
from claudebox import ClaudeBox, NOTIFICATION_SKILL

@pytest.mark.asyncio
async def test_notification_skill():
    async with ClaudeBox(skills=[NOTIFICATION_SKILL]) as box:
        result = await box.code("Send test notification to Slack")
        assert result.success
```

### 3. Add Documentation

Create `docs/skills/notification.md`:

````markdown
# Notification Skill

Send notifications to Slack, Discord, or email.

## Usage

```python
from claudebox import ClaudeBox, NOTIFICATION_SKILL

async with ClaudeBox(skills=[NOTIFICATION_SKILL]) as box:
    await box.code("Send 'Build completed' to #engineering on Slack")
```

## Environment Variables

- `SLACK_TOKEN` - Slack API token
- `DISCORD_WEBHOOK_URL` - Discord webhook URL
````

### 4. Create a PR

Submit your skill as a PR with:
- Skill definition in `src/claudebox/skills.py`
- Test in `tests/test_real_skills.py`
- Documentation in `docs/skills/`
- Example in `examples/02_skills.py`

## Release Process

(For maintainers)

### Version Bumping

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md

# Commit
git add pyproject.toml CHANGELOG.md
git commit -m "chore: Bump version to X.Y.Z"

# Tag
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push origin main --tags
```

### Publishing

GitHub Actions automatically publishes to PyPI when a new tag is pushed.

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions, share ideas
- **Documentation**: Check the [docs/](docs/) directory
- **Examples**: Browse [examples/](examples/) for code samples

## Recognition

Contributors are recognized in:
- Git commit history
- CHANGELOG.md release notes
- GitHub contributors page

Thank you for contributing to ClaudeBox! 🎉
