# Contributing to Echo AI Trading Intelligence Platform

Thank you for your interest in contributing to Echo AI! This guide will help you get started with contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)
- [Areas for Contribution](#areas-for-contribution)

## 🤝 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards others

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:

- Python 3.9 or higher
- Git
- pip and virtualenv
- Basic knowledge of Python, Pandas, and ML concepts
- Understanding of financial markets (helpful but not required)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/echo-ai-dashboard.git
   cd echo-ai-dashboard
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/OxainZ/echo-ai-dashboard.git
   ```

## 💻 Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Development Dependencies

```bash
pip install -r requirements.txt
pip install -e .  # Install package in editable mode
```

### 3. Install Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

### 4. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your local settings
```

### 5. Verify Installation

```bash
pytest
streamlit run UI.py
```

## 📝 Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line Length**: 120 characters (not 79)
- **Imports**: Organized by standard library, third-party, local
- **Docstrings**: Required for all public functions, classes, and modules
- **Type Hints**: Encouraged for function signatures

### Code Formatting

We use **Black** for code formatting:

```bash
# Format code
black echo/ tests/

# Check formatting
black --check echo/ tests/
```

### Linting

We use **Flake8** for linting:

```bash
# Run linting
flake8 echo/ tests/ --max-line-length=120 --ignore=E203,W503
```

### Type Checking

We use **MyPy** for type checking:

```bash
# Run type checking
mypy echo/ --ignore-missing-imports
```

### Docstring Format

Use Google-style docstrings:

```python
def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate the Sharpe ratio for a return series.
    
    The Sharpe ratio measures risk-adjusted returns by comparing
    excess returns to volatility.
    
    Args:
        returns (pd.Series): Series of periodic returns
        risk_free_rate (float): Risk-free rate of return (default: 0.0)
        
    Returns:
        float: Sharpe ratio value
        
    Raises:
        ValueError: If returns series is empty
        
    Examples:
        >>> returns = pd.Series([0.01, 0.02, -0.01, 0.03])
        >>> sharpe = calculate_sharpe_ratio(returns)
        >>> print(f"Sharpe ratio: {sharpe:.2f}")
    """
    if returns.empty:
        raise ValueError("Returns series cannot be empty")
    
    excess_returns = returns - risk_free_rate
    return excess_returns.mean() / excess_returns.std() * np.sqrt(252)
```

## 🧪 Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Name test functions as `test_*`
- Use descriptive test names
- Follow AAA pattern: Arrange, Act, Assert

### Test Structure

```python
def test_feature_with_valid_input():
    """Test feature behavior with valid input."""
    # Arrange
    input_data = create_test_data()
    expected_output = compute_expected_result()
    
    # Act
    actual_output = feature_function(input_data)
    
    # Assert
    assert actual_output == expected_output
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_engine.py

# Run with coverage
pytest --cov=echo --cov-report=html

# Run only fast tests
pytest -m "not slow"
```

### Test Coverage

- Aim for >80% code coverage
- Focus on critical paths
- Include edge cases
- Test error handling

### Mocking External Services

```python
import pytest
from unittest.mock import Mock, patch

@patch('echo.data_providers.yfinance_provider.yf.Ticker')
def test_data_provider(mock_ticker):
    """Test data provider with mocked yfinance."""
    # Setup mock
    mock_ticker.return_value.history.return_value = create_mock_data()
    
    # Test
    provider = YFinanceProvider()
    data = provider.history('AAPL')
    
    # Assert
    assert not data.empty
    mock_ticker.assert_called_once_with('AAPL')
```

## 🔄 Pull Request Process

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/changes

### 2. Make Changes

- Write clean, documented code
- Add tests for new functionality
- Update documentation
- Keep commits atomic and well-described

### 3. Commit Changes

```bash
git add .
git commit -m "feat: Add LSTM model for price prediction"
```

Commit message format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

### 4. Update Your Branch

```bash
git fetch upstream
git rebase upstream/main
```

### 5. Run Tests and Checks

```bash
# Run tests
pytest

# Run linting
black --check echo/ tests/
flake8 echo/ tests/

# Run type checking
mypy echo/
```

### 6. Push Changes

```bash
git push origin feature/your-feature-name
```

### 7. Create Pull Request

1. Go to GitHub and create a pull request
2. Fill in the PR template
3. Link related issues
4. Request reviews
5. Address review comments
6. Wait for CI checks to pass

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] No breaking changes

## Related Issues
Closes #123
```

## 📁 Project Structure

### Core Modules

- `echo/engine/` - Trading engine and orchestration
- `echo/rules/` - Signal generation rules
- `echo/ml_models/` - Machine learning models
- `echo/strategies/` - Trading strategies
- `echo/data_providers/` - Market data sources
- `echo/utils/` - Utility functions

### Key Files

- `UI.py` - Main Streamlit dashboard
- `echo/engine/echo_engine.py` - Core engine
- `echo/config.yaml` - Configuration
- `requirements.txt` - Dependencies
- `pytest.ini` - Test configuration

### Adding New Components

#### Adding a New Rule

1. Create file in `echo/rules/`
2. Inherit from `Rule` base class
3. Implement `run(context)` method
4. Register in `EchoEngine`
5. Add tests

```python
# echo/rules/my_new_rule.py
from .base import Rule, Signal

class MyNewRule(Rule):
    """Describe what this rule does."""
    
    def run(self, context) -> Signal:
        # Analysis logic here
        return Signal(
            name="My New Rule",
            score=75.0,
            detail="Detailed explanation",
            severity="green"
        )
```

#### Adding a New Strategy

1. Create file in `echo/strategies/`
2. Inherit from `BaseStrategy`
3. Implement `generate_signals()` method
4. Add backtesting support
5. Add tests

#### Adding a New ML Model

1. Create file in `echo/ml_models/`
2. Implement training and prediction methods
3. Add model saving/loading
4. Document model architecture
5. Add tests

## 🎯 Areas for Contribution

### High Priority

- [ ] Additional ML models (Transformer, XGBoost)
- [ ] More trading strategies (mean-reversion, pairs trading)
- [ ] Enhanced risk management features
- [ ] Real-time alerts system
- [ ] Portfolio optimization
- [ ] Sentiment analysis integration

### Medium Priority

- [ ] Additional data providers (Alpha Vantage, Finnhub)
- [ ] Enhanced visualization options
- [ ] Mobile-responsive improvements
- [ ] Performance optimizations
- [ ] Caching layer
- [ ] Database integration

### Documentation

- [ ] API documentation
- [ ] Tutorial notebooks
- [ ] Video guides
- [ ] Architecture diagrams
- [ ] Deployment guides
- [ ] Best practices guide

### Testing

- [ ] Increase test coverage
- [ ] Integration tests
- [ ] Performance tests
- [ ] Load tests
- [ ] End-to-end tests

## 🐛 Reporting Bugs

### Before Reporting

1. Check if bug already reported
2. Verify bug exists in latest version
3. Collect relevant information

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g., Windows 10]
- Python version: [e.g., 3.11]
- Browser: [e.g., Chrome 120]

**Additional context**
Any other relevant information
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Description of the problem

**Describe the solution you'd like**
Clear description of desired functionality

**Describe alternatives you've considered**
Other approaches you've thought about

**Additional context**
Mockups, examples, or references
```

## 📚 Resources

### Documentation

- [Python Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [TensorFlow Documentation](https://www.tensorflow.org/api_docs)

### Learning Resources

- [Algorithmic Trading](https://www.quantstart.com/)
- [Time Series Forecasting](https://www.tensorflow.org/tutorials/structured_data/time_series)
- [Financial Machine Learning](https://www.amazon.com/Advances-Financial-Machine-Learning-Marcos/dp/1119482089)

## 🤔 Questions?

- Open a GitHub Discussion
- Check existing documentation
- Review closed issues
- Ask in pull request comments

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to Echo AI! 🚀
