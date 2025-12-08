# 🚀 Echo AI Trading Intelligence Platform

## AI-Powered Trading Dashboard with Continuous Learning

A sophisticated, professional-grade trading intelligence platform featuring **AI/ML models**, real-time market analytics, autonomous decision-making, and continuous learning capabilities. Built with Python, Streamlit, and TensorFlow.

---

## ⚠️ IMPORTANT DISCLAIMER

**This software is provided for EDUCATIONAL and RESEARCH purposes only.**

- ❌ NOT financial advice
- ❌ NOT a recommendation to buy, sell, or hold any securities
- ❌ Past performance does NOT guarantee future results
- ✅ Users assume ALL risks
- ✅ Please read [ETHICAL_USAGE.md](ETHICAL_USAGE.md) before using

---

## ✨ Key Features

### 🤖 **AI/ML Models**
- **LSTM Networks** - Time series prediction for stock prices
- **Transformer Models** - Pattern recognition and trend analysis
- **Reinforcement Learning** - Adaptive trading strategy optimization
- **Continuous Learning** - Models update with new data automatically
- **Memory Persistence** - Training history and model state saved between sessions

### 📊 **Advanced Data Integration**
- **Multiple Data Providers**:
  - Yahoo Finance (real-time quotes)
  - Alpha Vantage (comprehensive market data)
  - Quandl/NASDAQ Data Link (economic indicators)
- **Technical Indicators**:
  - RSI, MACD, Bollinger Bands
  - Moving Averages (SMA, EMA)
  - Stochastic Oscillator, ATR
  - Volume indicators (OBV)
- **Automated Preprocessing**:
  - Data cleaning and validation
  - Feature engineering
  - Normalization and scaling

### 🎯 **Intelligent Trading Decisions**
- **AI-Powered Signals** - BUY/SELL/HOLD recommendations
- **Risk Management**:
  - Automatic stop-loss calculation
  - Take-profit targets
  - Position sizing optimization
  - Portfolio risk assessment
- **Backtesting Framework** - Test strategies on historical data
- **Real-time Decision Engine** - Combines AI predictions with technical analysis

### 📈 **Interactive Dashboard**
- **Real-time Predictions** - 5-day forecast with confidence intervals
- **Model Performance Tracking** - Accuracy, precision, recall, Sharpe ratio
- **Learning Progress Visualization** - Training curves and metrics
- **Feature Importance Analysis** - Understand what drives predictions
- **Risk/Reward Heatmaps** - Visual portfolio risk assessment
- **Historical Performance** - Comprehensive backtesting results

### 🔒 **Security & Compliance**
- **Environment Variable Management** - Secure API key storage
- **No Hardcoded Secrets** - All sensitive data externalized
- **Audit Logging** - Track all system activities
- **Ethical Guidelines** - Comprehensive usage guidelines
- **CI/CD Security Scanning** - Automated vulnerability detection

---

## 🛠️ Installation

### Prerequisites
- Python 3.9, 3.10, or 3.11
- pip package manager
- Git

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/OxainZ/echo-ai-dashboard.git
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
   ```

4. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Run the Dashboard**
   ```bash
   streamlit run UI.py
   ```

---

## 🔑 Configuration

### API Keys Required

Add these to your `.env` file:

```bash
# Data Provider API Keys
ALPHA_VANTAGE_API_KEY=your_key_here
QUANDL_API_KEY=your_key_here

# Optional: Yahoo Finance (usually works without key)
YAHOO_FINANCE_API_KEY=optional

# Dashboard Authentication
PASSWORD_HASH=your_hashed_password_here
```

### Getting API Keys

- **Alpha Vantage**: [Get Free API Key](https://www.alphavantage.co/support/#api-key)
- **Quandl**: [Get Free API Key](https://data.nasdaq.com/sign-up)

### Configuration Files

- `echo/config.yaml` - Trading strategy configuration
- `.streamlit/config.toml` - Dashboard settings
- `.streamlit/secrets.toml` - Authentication secrets

---

## 📚 Usage

### Running the Main Dashboard

```bash
streamlit run UI.py
```

Default access code: `echo2024` (change in `.streamlit/secrets.toml`)

### Running CLI Reports

```bash
python -m echo.main --report daily --config echo/config.yaml
```

### Training AI Models

```python
from echo.models.lstm.lstm_predictor import LSTMPredictor
from echo.preprocessing.financial_data import FinancialDataPreprocessor
import yfinance as yf

# Fetch data
data = yf.Ticker("AAPL").history(period="2y")

# Preprocess
preprocessor = FinancialDataPreprocessor()
processed = preprocessor.process_pipeline(data)

# Train model
model = LSTMPredictor(model_id="aapl_predictor")
X, y = preprocessor.prepare_features(processed)
model.train(X.values, y.values, epochs=50)

# Make predictions
predictions = model.predict_next_days(processed.values[-60:], n_days=5)
print(f"5-day forecast: {predictions}")
```

### Generating Trading Signals

```python
from echo.engine.trading_decision import TradingDecisionEngine

engine = TradingDecisionEngine()
signal = engine.generate_signal(
    ticker="AAPL",
    current_price=150.0,
    ai_prediction=155.0,
    ai_confidence=0.85,
    technical_score=75,
    portfolio_value=10000
)

print(f"Action: {signal.action.value}")
print(f"Confidence: {signal.confidence:.2f}")
print(f"Stop Loss: ${signal.stop_loss:.2f}")
print(f"Target: ${signal.target_price:.2f}")
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ -v --cov=echo --cov-report=html
```

### Run Specific Test Suite

```bash
# Test AI models
pytest tests/unit/test_base_model.py -v

# Test preprocessing
pytest tests/unit/test_preprocessing.py -v

# Test trading logic
pytest tests/unit/test_trading_decision.py -v
```

---

## 📦 Project Structure

```
echo-ai-dashboard/
├── echo/
│   ├── models/              # AI/ML models
│   │   ├── base_model.py   # Base model with memory
│   │   ├── lstm/           # LSTM implementation
│   │   ├── transformer/    # Transformer models
│   │   └── rl_agent/       # Reinforcement learning
│   ├── preprocessing/       # Data preprocessing
│   │   └── financial_data.py
│   ├── data_providers/      # Data sources
│   │   ├── yfinance_provider.py
│   │   ├── alphavantage_provider.py
│   │   └── quandl_provider.py
│   ├── engine/             # Trading logic
│   │   ├── echo_engine.py
│   │   ├── portfolio.py
│   │   └── trading_decision.py
│   ├── rules/              # Trading rules
│   ├── utils/              # Utilities
│   └── dashboard/          # Dashboard components
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── docs/                   # Documentation
├── .github/
│   └── workflows/          # CI/CD pipelines
├── UI.py                   # Main dashboard
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── ETHICAL_USAGE.md       # Usage guidelines
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Follow Code Standards**
   - PEP 8 compliance
   - Type hints required
   - Add unit tests for new features
   - Update documentation
4. **Run Tests**
   ```bash
   pytest tests/ -v
   ```
5. **Submit Pull Request**

### Code Quality

All contributions must pass:
- Linting (flake8, black)
- Type checking (mypy)
- Unit tests
- Security scans

---

## 🔐 Security

### Reporting Vulnerabilities

Please report security issues privately to the maintainers. Do NOT create public issues.

### Security Features

- ✅ No hardcoded secrets
- ✅ Environment variable management
- ✅ Secure password hashing (SHA-256)
- ✅ Input validation and sanitization
- ✅ Automated security scanning (CodeQL, Bandit)
- ✅ Dependency vulnerability checking

---

## 📄 License

This project is proprietary software. All rights reserved.

See [LICENSE](LICENSE) for details.

---

## 🌟 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Dashboard framework
- [TensorFlow](https://www.tensorflow.org/) - AI/ML models
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [Plotly](https://plotly.com/) - Interactive visualizations
- [yfinance](https://github.com/ranaroussi/yfinance) - Market data

---

## 📞 Support

- **Documentation**: See `/docs` directory
- **Issues**: [GitHub Issues](https://github.com/OxainZ/echo-ai-dashboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/OxainZ/echo-ai-dashboard/discussions)

---

## 📈 Roadmap

- [ ] Advanced transformer models
- [ ] Multi-asset portfolio optimization
- [ ] Real-time paper trading
- [ ] Mobile app integration
- [ ] Social sentiment analysis
- [ ] Options strategy recommendations
- [ ] Automated model retraining pipeline

---

**Version**: 2.0.0 (AI-Enhanced)  
**Last Updated**: December 2024  
**Status**: Active Development

⚠️ **Remember**: Always read [ETHICAL_USAGE.md](ETHICAL_USAGE.md) before using this software.
