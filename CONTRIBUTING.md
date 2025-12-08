# Contributing to Echo AI Dashboard

Thank you for your interest in contributing to Echo AI Dashboard! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## Getting Started

1. **Fork the Repository**
   ```bash
   gh repo fork OxainZ/echo-ai-dashboard --clone
   cd echo-ai-dashboard
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites
- Python 3.11 or higher
- pip or conda
- Git
- (Optional) Docker for containerized development

### Installation

1. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/echo-ai-dashboard.git
   cd echo-ai-dashboard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   streamlit run UI.py
   ```

## Making Changes

### Branch Naming Convention
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or updates

### Commit Messages
Follow conventional commits format:
```
type(scope): subject

body

footer
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(ml): add LSTM prediction model

- Implement LSTM-based stock price prediction
- Add training pipeline
- Include model evaluation metrics

Closes #123
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_predictor.py

# Run with coverage
pytest --cov=echo --cov-report=html
```

### Writing Tests
- Place tests in the `tests/` directory
- Mirror the structure of the `echo/` directory
- Use descriptive test names
- Test edge cases and error conditions

Example:
```python
def test_stock_predictor_basic():
    predictor = StockPredictor()
    data = generate_sample_data()
    result = predictor.predict("AAPL", data, days_ahead=5)
    assert 'predictions' in result
    assert len(result['predictions']) == 5
```

## Submitting Changes

1. **Ensure all tests pass**
   ```bash
   pytest
   ```

2. **Format code** (if using black/autopep8)
   ```bash
   black echo/
   flake8 echo/
   ```

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Link related issues

### Pull Request Guidelines
- Provide clear description of changes
- Link to related issues
- Include screenshots for UI changes
- Ensure CI/CD checks pass
- Request review from maintainers

## Code Style

### Python Style Guide
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

Example:
```python
def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate the Sharpe ratio for a return series.
    
    Args:
        returns: Series of periodic returns
        risk_free_rate: Annual risk-free rate (default: 0.0)
    
    Returns:
        Sharpe ratio as a float
    """
    excess_returns = returns - risk_free_rate / 252
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
```

### Documentation Style
- Use clear, concise language
- Include code examples
- Update relevant documentation with code changes
- Add inline comments for complex logic

## Project Structure

```
echo-ai-dashboard/
├── echo/                      # Main application package
│   ├── engine/               # Trading engine and core logic
│   ├── ml/                   # Machine learning models
│   ├── data_providers/       # Data source integrations
│   ├── portfolio/            # Portfolio management
│   ├── rules/                # Trading rules
│   └── utils/                # Utility functions
├── tests/                    # Test suite
├── docs/                     # Documentation
├── .github/                  # GitHub workflows
├── UI.py                     # Main Streamlit application
└── requirements.txt          # Python dependencies
```

## Feature Development Guidelines

### Adding a New Data Provider
1. Create file in `echo/data_providers/`
2. Inherit from `PriceProvider` protocol
3. Implement `quote()` and `history()` methods
4. Add tests in `tests/test_data_providers.py`
5. Update documentation

### Adding a New ML Model
1. Create model class in `echo/ml/`
2. Follow existing predictor patterns
3. Include training and prediction methods
4. Add evaluation metrics
5. Document model architecture and usage

### Adding a New Trading Rule
1. Create file in `echo/rules/`
2. Inherit from `Rule` base class
3. Implement `run(context)` method
4. Return `Signal` object
5. Register in `EchoEngine`

## Questions or Issues?

- Check existing [Issues](https://github.com/OxainZ/echo-ai-dashboard/issues)
- Create a new issue for bugs or feature requests
- Join discussions in [Discussions](https://github.com/OxainZ/echo-ai-dashboard/discussions)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
