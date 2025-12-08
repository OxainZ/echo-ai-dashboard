# Contributing to Echo AI Dashboard

Thank you for your interest in contributing to Echo AI Dashboard! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Review Process](#review-process)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of pandas, NumPy, and Streamlit

### Setting Up Development Environment

1. **Fork the Repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/echo-ai-dashboard.git
   cd echo-ai-dashboard
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Configure Pre-commit Hooks** (Optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development Process

### Branch Naming Convention

Use descriptive branch names:
- `feature/your-feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/documentation-update` - Documentation changes
- `refactor/code-improvement` - Code refactoring
- `test/test-improvement` - Test additions/improvements

### Workflow

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write code following our coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run all tests
   pytest tests/ -v
   
   # Run with coverage
   pytest tests/ --cov=echo --cov-report=html
   
   # Run specific test
   pytest tests/test_core.py::TestLSTMStockPredictor -v
   ```

4. **Lint Your Code**
   ```bash
   # Format with black
   black echo/ tests/ *.py
   
   # Check with flake8
   flake8 echo/ tests/ *.py
   
   # Sort imports
   isort echo/ tests/ *.py
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Type: Brief description
   
   Detailed explanation of changes.
   
   Closes #issue_number"
   ```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with the following specifications:

- **Line Length**: Maximum 127 characters
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Use double quotes for strings
- **Naming Conventions**:
  - Classes: `PascalCase`
  - Functions/Variables: `snake_case`
  - Constants: `UPPER_CASE`
  - Private: Prefix with `_`

### Type Hints

All function signatures must include type hints:

```python
from typing import Dict, List, Optional, Any

def process_data(
    data: pd.DataFrame,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, float]:
    """Process data and return metrics."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed. Explain the purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param2 is negative
        RuntimeError: When operation fails
    
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

### Comments

- Use comments to explain **why**, not **what**
- Keep comments up-to-date with code changes
- Use `# TODO:` for future improvements
- Use `# FIXME:` for known issues

```python
# Good comment - explains why
# Using exponential moving average here because it responds
# faster to recent price changes than simple moving average
ema = data['Close'].ewm(span=12).mean()

# Bad comment - just repeats the code
# Calculate the exponential moving average
ema = data['Close'].ewm(span=12).mean()
```

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors appropriately

```python
try:
    result = process_data(df)
except ValueError as e:
    logger.error(f"Invalid data format: {e}")
    raise
except Exception as e:
    logger.exception("Unexpected error in process_data")
    raise RuntimeError(f"Processing failed: {e}") from e
```

## Testing Guidelines

### Test Structure

- One test file per module: `test_module_name.py`
- Group related tests in classes
- Use descriptive test names

```python
class TestLSTMPredictor:
    """Test suite for LSTM predictor."""
    
    def test_initialization_with_default_params(self):
        """Test that predictor initializes with default parameters."""
        predictor = LSTMStockPredictor()
        assert predictor.lookback_days == 60
    
    def test_training_updates_model_state(self):
        """Test that training sets is_trained flag to True."""
        predictor = LSTMStockPredictor()
        predictor.train(sample_data)
        assert predictor.is_trained
```

### Test Coverage

- Aim for >80% code coverage
- Test edge cases and error conditions
- Use fixtures for common test data

```python
import pytest

@pytest.fixture
def sample_data():
    """Shared fixture for test data."""
    return pd.DataFrame({
        'Close': [100, 101, 102],
        'Volume': [1000, 1100, 1200]
    })

def test_with_fixture(sample_data):
    """Test using the shared fixture."""
    assert len(sample_data) == 3
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_core.py -v

# Run specific test class
pytest tests/test_core.py::TestLSTMStockPredictor -v

# Run with coverage
pytest tests/ --cov=echo --cov-report=html
open htmlcov/index.html

# Run with output
pytest tests/ -v -s
```

## Documentation

### Code Documentation

- All public functions/classes must have docstrings
- Update docstrings when changing function behavior
- Include examples in docstrings when helpful

### README Updates

Update README.md when:
- Adding new features
- Changing installation process
- Modifying configuration options
- Adding new dependencies

### API Documentation

Update `docs/API_DOCUMENTATION.md` when:
- Adding new public APIs
- Changing function signatures
- Adding new modules

## Submitting Changes

### Creating a Pull Request

1. **Update Your Branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push Your Changes**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Open Pull Request**
   - Go to GitHub and click "New Pull Request"
   - Fill in the PR template
   - Link related issues
   - Add screenshots for UI changes

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated documentation

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #123
```

### Commit Message Guidelines

Format: `Type: Brief description (50 chars or less)`

**Types:**
- `Add`: New feature or functionality
- `Fix`: Bug fix
- `Update`: Update to existing feature
- `Remove`: Remove feature or file
- `Refactor`: Code refactoring
- `Docs`: Documentation changes
- `Test`: Test additions or changes
- `Style`: Code style changes (formatting, etc.)
- `Chore`: Maintenance tasks

**Examples:**
```
Add: LSTM prediction model for stock forecasting

Fix: Resolve data normalization bug in technical indicators

Update: Improve sentiment analysis accuracy

Docs: Add comprehensive API documentation

Test: Add unit tests for SentimentAnalyzer
```

## Review Process

### What Reviewers Look For

1. **Code Quality**
   - Follows coding standards
   - Well-structured and readable
   - Properly documented

2. **Testing**
   - Adequate test coverage
   - Tests pass
   - Edge cases covered

3. **Documentation**
   - README updated if needed
   - API docs updated
   - Docstrings present

4. **Security**
   - No security vulnerabilities
   - Sensitive data handled properly
   - Input validation present

### Addressing Feedback

- Respond to all review comments
- Make requested changes promptly
- Push updates to the same branch
- Mark conversations as resolved

## Development Tips

### Debugging

Use Python debugger:
```python
import pdb; pdb.set_trace()
```

Use logging:
```python
from echo.utils.logging import get_logger
logger = get_logger(__name__)
logger.debug(f"Processing {len(data)} records")
```

### Performance

- Profile code for performance issues:
  ```python
  import cProfile
  cProfile.run('your_function()')
  ```

- Use appropriate data structures
- Avoid premature optimization

### Security

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate all user inputs
- Keep dependencies updated

## Getting Help

### Resources

- **Documentation**: Check `/docs` directory
- **Examples**: Review existing code for patterns
- **Issues**: Search existing issues on GitHub

### Asking Questions

1. Search existing issues first
2. Provide context and code samples
3. Include error messages and logs
4. Describe what you've already tried

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Request Comments**: Code-specific discussions

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Git commit history

Thank you for contributing to Echo AI Dashboard! 🚀

---

**Questions?** Open an issue or start a discussion on GitHub.
