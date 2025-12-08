# Setup Guide - Echo AI Trading Dashboard

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: Version 3.9, 3.10, or 3.11
- **RAM**: Minimum 4GB (8GB+ recommended for model training)
- **Disk Space**: 2GB free space
- **Internet**: Stable connection for data fetching

### Required Accounts
1. **Alpha Vantage** (Free tier available)
   - Sign up at: https://www.alphavantage.co/support/#api-key
   - Free tier: 25 API requests per day

2. **Quandl/NASDAQ Data Link** (Optional)
   - Sign up at: https://data.nasdaq.com/sign-up
   - Free tier: 50 requests per day

3. **GitHub** (for deployment)
   - Account for Streamlit Cloud or GitHub Actions

---

## Quick Start (5 minutes)

### 1. Clone Repository

```bash
git clone https://github.com/OxainZ/echo-ai-dashboard.git
cd echo-ai-dashboard
```

### 2. Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Core libraries (pandas, numpy, etc.)
- Streamlit for dashboard
- TensorFlow for AI models (optional, but recommended)
- Data providers and utilities

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your favorite editor
```

**Minimum required in .env:**
```bash
ALPHA_VANTAGE_API_KEY=your_key_here
```

### 5. Run Dashboard

```bash
streamlit run UI.py
```

The dashboard will open at: http://localhost:8501

**Default Access Code**: `echo2024`

---

## Detailed Setup

### Step 1: Python Environment Setup

#### Check Python Version

```bash
python --version
```

Should output Python 3.9.x, 3.10.x, or 3.11.x

#### Install Python (if needed)

**macOS:**
```bash
brew install python@3.10
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

**Windows:**
Download from https://www.python.org/downloads/

### Step 2: Install Dependencies

#### Full Installation

```bash
pip install -r requirements.txt
```

#### Minimal Installation (without AI models)

```bash
pip install pandas numpy streamlit plotly yfinance requests pyyaml python-dotenv
```

#### With TensorFlow for AI Models

```bash
# CPU version (lighter)
pip install tensorflow-cpu

# GPU version (if you have NVIDIA GPU)
pip install tensorflow-gpu
```

### Step 3: Configuration

#### Environment Variables (.env)

Create `.env` file with:

```bash
# API Keys (Required)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
QUANDL_API_KEY=your_quandl_key  # Optional

# Trading Configuration
ENABLE_PAPER_TRADING=true
ENABLE_LIVE_TRADING=false  # Keep false for safety
MAX_POSITION_SIZE_USD=10000
RISK_TOLERANCE=medium

# Model Configuration
MODEL_SAVE_PATH=./models
ENABLE_MODEL_RETRAINING=true
RETRAINING_INTERVAL_HOURS=24

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/trading.log

# Dashboard
STREAMLIT_SERVER_PORT=8501
AUTO_REFRESH_INTERVAL_SECONDS=30
```

#### Streamlit Secrets (.streamlit/secrets.toml)

Create `.streamlit/secrets.toml` for authentication:

```toml
# Dashboard password (hashed with SHA-256)
password_hash = "your_sha256_hash_here"

# Generate hash in Python:
# import hashlib
# print(hashlib.sha256("your_password".encode()).hexdigest())
```

**Example:**
```python
import hashlib
password = "mySecurePassword123"
hash_value = hashlib.sha256(password.encode()).hexdigest()
print(hash_value)
```

#### Trading Configuration (echo/config.yaml)

Edit `echo/config.yaml` to customize:

```yaml
timezone: America/New_York

slots:
  core: SPY      # Core holding
  momentum: QQQ  # Momentum play
  wildcard: TSLA # High-conviction pick

risk:
  cash_buffer_percent: 5
  max_risk_per_trade_usd: 100
  max_slot_risk_usd: 200
  kill_switch_drawdown_30d_pct: 15

# Add your tickers and strategies
```

### Step 4: Verify Installation

#### Run Tests

```bash
pytest tests/ -v
```

Should show all tests passing.

#### Test Data Providers

```python
python << EOF
from echo.data_providers.yfinance_provider import YFinanceProvider

provider = YFinanceProvider()
quote = provider.quote('AAPL')
print(f"AAPL Price: ${quote['price']:.2f}")
EOF
```

#### Test AI Models

```python
python << EOF
from echo.models.base_model import BaseModel

class TestModel(BaseModel):
    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=100):
        self.model = "trained"
    def predict(self, X):
        return [1, 2, 3]
    def evaluate(self, X, y):
        return {'accuracy': 0.95}

model = TestModel("test")
print(f"Model initialized: {model.model_id}")
print(f"Memory created: {model.memory is not None}")
EOF
```

---

## Running the Dashboard

### Development Mode

```bash
streamlit run UI.py
```

**Features:**
- Auto-reload on file changes
- Debug console
- Development toolbar

### Production Mode

```bash
streamlit run UI.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false
```

### Docker (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "UI.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t echo-ai-dashboard .
docker run -p 8501:8501 --env-file .env echo-ai-dashboard
```

---

## Training AI Models

### Preparing Data

```python
from echo.data_providers.yfinance_provider import YFinanceProvider
from echo.preprocessing.financial_data import FinancialDataPreprocessor
import yfinance as yf

# Fetch data
ticker = "AAPL"
data = yf.Ticker(ticker).history(period="2y")

# Preprocess
preprocessor = FinancialDataPreprocessor()
processed = preprocessor.process_pipeline(data, add_indicators=True)

# Split data
train_data, test_data = preprocessor.temporal_train_test_split(processed, test_size=0.2)

print(f"Training samples: {len(train_data)}")
print(f"Test samples: {len(test_data)}")
```

### Training LSTM Model

```python
from echo.models.lstm.lstm_predictor import LSTMPredictor

# Initialize model
config = {
    'sequence_length': 60,
    'forecast_horizon': 5,
    'lstm_units': [128, 64, 32],
    'batch_size': 32,
    'model_dir': './models/weights',
    'memory_dir': './models/memory'
}

model = LSTMPredictor(model_id="aapl_lstm", config=config)

# Train
model.train(train_data.values, None, epochs=50)

# Make predictions
recent_data = test_data.tail(60).values
predictions = model.predict_next_days(recent_data, n_days=5)

print(f"5-day forecast: {predictions}")
```

### Evaluating Model

```python
# Evaluate on test set
metrics = model.evaluate(test_data.values)

print(f"Test MSE: {metrics['mse']:.4f}")
print(f"Test MAE: {metrics['mae']:.4f}")
print(f"Test RMSE: {metrics['rmse']:.4f}")

# Get performance summary
summary = model.get_performance_summary()
print(f"\nModel Summary:")
print(f"Created: {summary['created_at']}")
print(f"Total epochs: {summary['total_training_epochs']}")
print(f"Current metrics: {summary['current_metrics']}")
```

---

## Troubleshooting

### Issue: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'tensorflow'`

**Solution:**
```bash
pip install tensorflow
# or for CPU-only version:
pip install tensorflow-cpu
```

### Issue: API Rate Limit

**Error:** `API rate limit exceeded`

**Solution:**
- Wait for rate limit to reset (usually next day)
- Upgrade to paid API tier
- Implement caching to reduce API calls

### Issue: TensorFlow GPU Issues

**Error:** GPU not detected

**Solution:**
```bash
# Check GPU availability
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Install CUDA toolkit if needed (NVIDIA GPUs only)
# See: https://www.tensorflow.org/install/gpu
```

### Issue: Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Use different port
streamlit run UI.py --server.port 8502

# Or kill existing process
lsof -ti:8501 | xargs kill -9  # macOS/Linux
```

### Issue: Data Not Loading

**Error:** Empty dataframes or no data

**Solution:**
1. Check internet connection
2. Verify API keys in `.env`
3. Try different ticker symbols
4. Check API provider status

### Issue: Memory Errors

**Error:** `MemoryError` during model training

**Solution:**
```python
# Reduce batch size
config = {
    'batch_size': 16,  # Reduce from 32
    'lstm_units': [64, 32],  # Smaller network
}
```

---

## Performance Optimization

### Caching Data

```python
import pickle
import os

def get_cached_data(ticker, period="1y", cache_dir="./cache"):
    cache_file = f"{cache_dir}/{ticker}_{period}.pkl"
    
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    # Fetch fresh data
    data = yf.Ticker(ticker).history(period=period)
    
    # Cache it
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)
    
    return data
```

### Streamlit Caching

```python
import streamlit as st

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_stock_data(ticker):
    return yf.Ticker(ticker).history(period="1y")

@st.cache_resource
def load_model(model_id):
    model = LSTMPredictor(model_id=model_id)
    model.load_model()
    return model
```

---

## Next Steps

1. **Explore the Dashboard** - Navigate through different tabs
2. **Train Your First Model** - Follow the training guide above
3. **Customize Strategies** - Edit `echo/config.yaml`
4. **Read Documentation** - See `docs/API_DOCUMENTATION.md`
5. **Run Tests** - `pytest tests/ -v`
6. **Join Community** - Check GitHub Discussions

---

## Getting Help

- **Documentation**: `/docs` directory
- **Issues**: [GitHub Issues](https://github.com/OxainZ/echo-ai-dashboard/issues)
- **API Docs**: `docs/API_DOCUMENTATION.md`
- **Examples**: `tests/` directory

---

**Happy Trading! 🚀📈**

Remember: This is for educational purposes only. Always do your own research and never invest more than you can afford to lose.
