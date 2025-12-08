# Contributing to Echo AI Dashboard

Thank you for your interest in contributing to the Echo AI Dashboard project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and professional in all interactions
- Focus on constructive feedback and collaboration
- Help maintain a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/OxainZ/echo-ai-dashboard/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Enhancements

1. Check existing issues and pull requests for similar suggestions
2. Create a new issue with the `enhancement` label
3. Clearly describe the enhancement and its benefits
4. Include examples or mockups if applicable

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes following our coding standards
4. Write or update tests for your changes
5. Update documentation as needed
6. Commit your changes with clear, descriptive messages
7. Push to your fork and submit a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/OxainZ/echo-ai-dashboard.git
cd echo-ai-dashboard

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run tests
pytest

# Run the application
streamlit run UI.py
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise
- Use type hints where appropriate

### Example Code Style

```python
from typing import Dict, Optional
import pandas as pd

def calculate_indicator(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate a technical indicator.
    
    Args:
        data: Price series to analyze
        period: Calculation period
        
    Returns:
        Series with calculated indicator values
    """
    # Implementation here
    pass
```

### Testing

- Write unit tests for all new functions
- Aim for >80% code coverage
- Use pytest fixtures for test data
- Mock external API calls in tests

```python
import pytest

class TestYourFeature:
    @pytest.fixture
    def sample_data(self):
        return pd.DataFrame(...)
    
    def test_your_function(self, sample_data):
        result = your_function(sample_data)
        assert result is not None
```

### Documentation

- Update README.md if adding new features
- Add docstrings to all public functions and classes
- Include code examples in documentation
- Update CHANGELOG.md for significant changes

## Project Structure

```
echo-ai-dashboard/
├── echo/                   # Core application package
│   ├── data_providers/    # Data fetching modules
│   ├── engine/            # Trading engine
│   ├── ml/                # Machine learning models
│   ├── rules/             # Trading rules
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                  # Documentation
├── UI.py                  # Main Streamlit application
└── requirements.txt       # Python dependencies
```

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
type: Brief description (50 chars or less)

More detailed explanation if needed (wrap at 72 chars).
Include motivation for the change and contrast with previous behavior.

Fixes #123
```

### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

## Release Process

1. Update version number in relevant files
2. Update CHANGELOG.md
3. Create a pull request to main branch
4. After review and approval, merge to main
5. Tag the release with version number
6. Deploy to production

## Getting Help

- Check existing documentation in the `docs/` folder
- Review closed issues for similar questions
- Create a new issue with the `question` label
- Join community discussions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Echo AI Dashboard!
