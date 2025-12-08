# 🚀 Echo AI Trading Intelligence Platform

[![CI/CD Pipeline](https://github.com/OxainZ/echo-ai-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/OxainZ/echo-ai-dashboard/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

## 🌟 Overview

Echo AI is a comprehensive, professional-grade trading intelligence platform featuring real-time market signals, AI/ML predictions, risk analytics, portfolio management, and advanced visualization capabilities.

**⚠️ IMPORTANT DISCLAIMER**: This platform is for **educational and informational purposes only**. See [DISCLAIMER.md](DISCLAIMER.md) for full legal terms.

---

## ✨ Key Features

### 🔐 Secure Authentication
- Password-protected access with SHA-256 hashed credentials
- Session-based security management
- Configurable access codes

### 🧠 AI/ML Capabilities
- **LSTM Neural Networks** - Time series prediction
- **Transformer Models** - Advanced pattern recognition with attention mechanisms
- **Technical Indicators** - 15+ automated technical analysis features
- **Data Preprocessing** - Automated feature engineering and normalization
- **Model Registry** - Manage multiple prediction models

### 📊 Real-time Dashboard
- **Composite Conviction Score** - Overall market confidence (0-100)
- **Risk Level Assessment** - Automated risk evaluation
- **Capital Efficiency Metrics** - Portfolio utilization tracking
- **Active Signal Monitoring** - Critical market signal alerts

### 📡 Signal Analysis
- Multi-signal processing (FOMC, Turn-of-Month, PEAD, Volatility, etc.)
- Signal scoring system (0-100 confidence)
- Color-coded visual indicators
- Detailed signal explanations

### 💼 Portfolio Management
- Multi-slot allocation (Core, Momentum, Wildcard)
- Real-time position tracking
- Dynamic position sizing
- AI-optimized allocations

### ⚠️ Risk Analytics
- Risk/Reward assessment
- Volatility analysis
- Sharpe ratio tracking
- Maximum drawdown monitoring

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/OxainZ/echo-ai-dashboard.git
   cd echo-ai-dashboard
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Copy example secrets file
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

5. **Edit secrets (optional)**
   ```bash
   # Edit .streamlit/secrets.toml to change password
   # Default password: echo2024
   # Generate new hash: python -c "import hashlib; print(hashlib.sha256('your_password'.encode()).hexdigest())"
   ```

6. **Run the dashboard**
   ```bash
   streamlit run UI.py
   ```

7. **Access the dashboard**
   - Open browser to: http://localhost:8501
   - Enter access code: `echo2024` (or your custom password)

---

## 📋 Dashboard Variants

The repository includes multiple dashboard versions for different use cases:

| File | Purpose | Authentication | AI Features | Production Ready |
|------|---------|----------------|-------------|------------------|
| `UI.py` | **Main Production Dashboard** | ✅ Yes | ❌ No | ✅ Yes |
| `ai_powered_dashboard.py` | AI-Enhanced Version | ✅ Yes | ✅ Yes | ✅ Yes |
| `basic_app.py` | Deployment Testing | ❌ No | ❌ No | ❌ No |
| `simple_app.py` | Development Testing | ❌ No | ❌ No | ❌ No |

See [DASHBOARD_FILES.md](DASHBOARD_FILES.md) for detailed comparison.

**Recommended for Production:**
```bash
streamlit run UI.py               # Standard dashboard
streamlit run ai_powered_dashboard.py  # AI-enhanced dashboard
```

---

## 🧪 Testing

Run the test suite to verify installation:

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_echo_engine.py -v

# Run with coverage report
pytest tests/ --cov=echo --cov-report=html
```

**Test Coverage:**
- Echo Engine: Unit tests for core trading logic
- Data Providers: Yahoo Finance integration tests
- ML Models: LSTM and Transformer model tests
- Data Preprocessing: Feature engineering tests

---

## 🛠️ Configuration

### Echo Engine Configuration

Edit `echo/config.yaml` to customize:

```yaml
timezone: "America/Chicago"
providers:
  price_data:
    name: "yfinance"
slots:
  core: "SPY"
  momentum: "QQQ"
  wildcard: "ARKK"
```

### Streamlit Configuration

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
```

---

## 🤖 AI/ML Models

### Available Models

1. **LSTM Predictor** (`echo.ml.lstm_predictor`)
   - Time series prediction using LSTM neural networks
   - Configurable sequence length and hidden units
   - Technical indicator integration

2. **Transformer Predictor** (`echo.ml.transformer_predictor`)
   - Self-attention mechanism for pattern recognition
   - Multi-head attention (8 heads default)
   - Configurable layers and embedding dimension

3. **Data Preprocessor** (`echo.ml.data_preprocessing`)
   - 15+ technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
   - Feature normalization and scaling
   - Missing value handling
   - Train/test splitting with temporal ordering

### Example Usage

```python
from echo.ml.lstm_predictor import LSTMPredictor
from echo.ml.data_preprocessing import FinancialDataPreprocessor

# Initialize predictor
predictor = LSTMPredictor(sequence_length=60, hidden_units=128)

# Preprocess data
preprocessor = FinancialDataPreprocessor()
data = preprocessor.preprocess_for_training(historical_df)

# Train (stub implementation)
metrics = predictor.train(data['train_data'], target)

# Predict
prediction = predictor.predict("AAPL", horizon="1d")
print(f"Predicted: ${prediction.predicted_price:.2f}")
print(f"Confidence: {prediction.confidence:.2%}")
```

**⚠️ Note:** Current ML implementations are stubs for demonstration. See `echo/ml/README.md` for production deployment guidelines.

---

## 📁 Project Structure

```
echo-ai-dashboard/
├── echo/                      # Core package
│   ├── engine/               # Trading engine
│   │   ├── echo_engine.py   # Main engine
│   │   ├── reports.py       # Report formatting
│   │   └── portfolio.py     # Portfolio management
│   ├── rules/                # Trading rules
│   │   ├── fomc_tilt.py     # FOMC event detection
│   │   ├── tom_window.py    # Turn-of-month
│   │   ├── pead.py          # Post-earnings drift
│   │   └── volatility_regime.py
│   ├── data_providers/       # Data sources
│   │   ├── base.py          # Base provider
│   │   └── yfinance_provider.py
│   ├── ml/                   # Machine learning
│   │   ├── base.py          # Base classes
│   │   ├── lstm_predictor.py
│   │   ├── transformer_predictor.py
│   │   └── data_preprocessing.py
│   └── utils/               # Utilities
│       ├── dates.py
│       └── logging.py
├── tests/                    # Test suite
│   ├── test_echo_engine.py
│   ├── test_data_providers.py
│   └── test_ml_models.py
├── .github/workflows/        # CI/CD
│   └── ci.yml
├── docs/                     # Documentation
├── UI.py                     # Main dashboard
├── ai_powered_dashboard.py  # AI dashboard
├── requirements.txt          # Dependencies
├── pytest.ini               # Test configuration
├── SECURITY.md              # Security policy
├── DISCLAIMER.md            # Legal disclaimer
└── README.md                # This file
```

---

## 🔒 Security

### Authentication

Default password: `echo2024`

To change the password:

1. Generate a new hash:
   ```bash
   python -c "import hashlib; print(hashlib.sha256('your_new_password'.encode()).hexdigest())"
   ```

2. Update `.streamlit/secrets.toml`:
   ```toml
   password_hash = "your_generated_hash"
   ```

### Best Practices

- Never commit `.streamlit/secrets.toml` to version control
- Use strong, unique passwords for production
- Rotate credentials regularly
- Enable HTTPS for production deployments
- Review [SECURITY.md](SECURITY.md) for complete security guidelines

---

## 📊 Data Sources

### Primary Provider: Yahoo Finance

The platform uses Yahoo Finance via the `yfinance` library:
- Real-time quotes (15-20 minute delay for most markets)
- Historical OHLCV data
- Multiple timeframes (1d, 5d, 1mo, 3mo, etc.)
- No API key required

### Optional Providers

Documentation includes configuration templates for:
- Alpha Vantage (requires API key)
- IEX Cloud (requires API key)
- Quandl (requires API key)

Add API keys to `.env` file (see `.env.example`).

---

## 🧑‍💻 Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_echo_engine.py

# With coverage
pytest tests/ --cov=echo --cov-report=term-missing

# Skip slow tests
pytest tests/ -m "not slow"
```

### Code Style

```bash
# Install dev dependencies
pip install flake8 pylint black

# Check code style
flake8 echo/ tests/

# Auto-format code
black echo/ tests/
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 🚀 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Main file: `UI.py`
5. Add secrets in dashboard settings:
   ```toml
   password_hash = "your_hash_here"
   ```

### Docker (Coming Soon)

```bash
# Build image
docker build -t echo-ai-dashboard .

# Run container
docker run -p 8501:8501 echo-ai-dashboard
```

### Requirements for Production

- Python 3.10+
- 1GB RAM minimum
- Stable internet connection
- HTTPS enabled
- Environment variables configured

---

## 📖 Documentation

- [DASHBOARD_FILES.md](DASHBOARD_FILES.md) - Dashboard variants guide
- [SECURITY.md](SECURITY.md) - Security policies and best practices
- [DISCLAIMER.md](DISCLAIMER.md) - Legal terms and disclaimers
- [echo/ml/README.md](echo/ml/README.md) - ML models documentation
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Ensure all tests pass

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## ⚠️ Important Disclaimers

### Not Financial Advice

This platform is for **educational and informational purposes only**. It does NOT constitute financial, investment, or trading advice. Always consult with qualified financial professionals before making investment decisions.

### Risk Warning

- Trading involves substantial risk of loss
- Past performance is not indicative of future results
- AI/ML predictions are probabilistic and can be wrong
- You may lose some or all of your invested capital

### Model Limitations

- ML models are stubs/demonstrations, not production-trained
- Predictions should not be used for actual trading decisions
- Models require extensive training and validation for production use

See [DISCLAIMER.md](DISCLAIMER.md) for complete legal terms.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/OxainZ/echo-ai-dashboard/issues)
- **Documentation**: Check the `docs/` directory
- **Email**: See repository settings

---

## 🙏 Acknowledgments

- **Streamlit** - Modern dashboard framework
- **Yahoo Finance** - Market data provider
- **Python Community** - Excellent libraries and tools

---

## 📈 Roadmap

- [ ] Production-ready ML model training
- [ ] Additional data providers (Alpha Vantage, IEX)
- [ ] Backtesting framework
- [ ] Trade execution simulation
- [ ] Advanced portfolio optimization
- [ ] Mobile-responsive design improvements
- [ ] Real-time WebSocket data streams
- [ ] Docker deployment support

---

**Version**: Echo AI v62 Professional  
**Last Updated**: December 2024  
**Python**: 3.10+  
**Status**: ✅ Active Development

---

⭐ **Star this repository** if you find it useful!

📢 **Follow** for updates on new features and improvements!
