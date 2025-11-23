# Contributing to ScrapeDrive Python SDK

Thank you for your interest in contributing to the ScrapeDrive Python SDK! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/yourusername/scrapedrive-py.git
   cd scrapedrive-py
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev,async]"
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scrapedrive --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::TestScrapeDriveInit::test_init_with_api_key
```

### Code Quality

```bash
# Format code with black
black scrapedrive tests examples

# Lint with ruff
ruff check scrapedrive tests

# Type check with mypy
mypy scrapedrive
```

### Running Examples

```bash
# Set your API key
export SCRAPEDRIVE_API_KEY="your-api-key"

# Run examples
python examples/basic_usage.py
python examples/async_usage.py
python examples/error_handling.py
```

## Code Style

- Follow PEP 8 guidelines
- Use black for code formatting (line length: 88)
- Use type hints for all functions
- Write docstrings for all public APIs
- Keep functions focused and simple

## Testing Guidelines

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Mock external API calls
- Test both success and error cases

## Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Reference issue numbers when applicable

Examples:
- `Add support for custom headers`
- `Fix timeout handling in async client`
- `Update documentation for proxy configuration`

## Pull Request Process

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add your feature"
   ```

3. Run tests and linting:
   ```bash
   pytest
   black scrapedrive tests
   ruff check scrapedrive tests
   mypy scrapedrive
   ```

4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a pull request on GitHub

6. Ensure CI passes

7. Wait for review

## Release Process

1. Update version in `pyproject.toml` and `scrapedrive/__init__.py`
2. Update `CHANGELOG.md`
3. Create a git tag:
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin v0.1.0
   ```
4. GitHub Actions will automatically publish to PyPI

## Questions?

If you have questions, please:
1. Check the [documentation](https://docs.scrapedrive.com)
2. Search [existing issues](https://github.com/yourusername/scrapedrive-py/issues)
3. Open a [new issue](https://github.com/yourusername/scrapedrive-py/issues/new)

Thank you for contributing!
