# API Documentation - Echo AI Trading Platform

## Table of Contents

1. [AI Models](#ai-models)
2. [Data Providers](#data-providers)
3. [Preprocessing](#preprocessing)
4. [Trading Decision Engine](#trading-decision-engine)
5. [Risk Management](#risk-management)

---

## AI Models

### BaseModel

Abstract base class for all AI models with memory persistence.

#### Constructor

```python
BaseModel(model_id: str, config: Optional[Dict] = None)
```

**Parameters:**
- `model_id`: Unique identifier for the model
- `config`: Optional configuration dictionary
  - `model_dir`: Directory for model weights (default: './models/weights')
  - `memory_dir`: Directory for memory files (default: './models/memory')

#### Methods

##### train()

```python
train(X_train, y_train, X_val=None, y_val=None, epochs: int = 100)
```

Train the model on provided data.

**Parameters:**
- `X_train`: Training features
- `y_train`: Training labels
- `X_val`: Validation features (optional)
- `y_val`: Validation labels (optional)
- `epochs`: Number of training epochs

##### predict()

```python
predict(X) -> Any
```

Make predictions on input data.

**Parameters:**
- `X`: Input features

**Returns:** Predictions (format depends on model implementation)

##### evaluate()

```python
evaluate(X, y) -> Dict[str, float]
```

Evaluate model performance.

**Parameters:**
- `X`: Test features
- `y`: Test labels

**Returns:** Dictionary of evaluation metrics

##### save_model() / load_model()

```python
save_model()
load_model() -> bool
```

Save/load model weights to/from disk.

##### save_memory()

```python
save_memory()
```

Persist model memory (training history, metrics) to disk.

---

### LSTMPredictor

LSTM-based time series predictor for stock prices.

#### Constructor

```python
LSTMPredictor(model_id: str = "lstm_stock_predictor", config: Optional[Dict] = None)
```

**Default Configuration:**
```python
{
    'sequence_length': 60,      # Look back period
    'forecast_horizon': 5,      # Days to predict ahead
    'lstm_units': [128, 64, 32],  # LSTM layer sizes
    'dropout_rate': 0.2,
    'learning_rate': 0.001,
    'batch_size': 32
}
```

#### Methods

##### predict_next_days()

```python
predict_next_days(recent_data: np.ndarray, n_days: int = 5) -> np.ndarray
```

Predict next N days of prices.

**Parameters:**
- `recent_data`: Recent historical data (at least sequence_length days)
- `n_days`: Number of days to predict

**Returns:** Array of predicted prices

**Example:**
```python
from echo.models.lstm.lstm_predictor import LSTMPredictor

model = LSTMPredictor()
predictions = model.predict_next_days(recent_data, n_days=5)
print(f"Next 5 days: {predictions}")
```

---

## Data Providers

### YFinanceProvider

Provider for Yahoo Finance data.

#### Constructor

```python
YFinanceProvider()
```

#### Methods

##### quote()

```python
quote(ticker: str) -> Dict
```

Get real-time quote for a ticker.

**Returns:**
```python
{
    'ticker': str,
    'price': float,
    'prev_close': float,
    'currency': str
}
```

##### history()

```python
history(ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame
```

Get historical data.

**Parameters:**
- `ticker`: Stock symbol
- `period`: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
- `interval`: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')

**Returns:** DataFrame with OHLCV data

---

### AlphaVantageProvider

Provider for Alpha Vantage data.

#### Constructor

```python
AlphaVantageProvider(api_key: Optional[str] = None)
```

**Parameters:**
- `api_key`: API key (or set ALPHA_VANTAGE_API_KEY environment variable)

#### Methods

##### quote()

```python
quote(ticker: str) -> Dict
```

Get real-time quote.

##### history()

```python
history(ticker: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame
```

Get historical data.

##### get_technical_indicator()

```python
get_technical_indicator(ticker: str, indicator: str, 
                       time_period: int = 14, series_type: str = 'close') -> pd.DataFrame
```

Get pre-calculated technical indicator from Alpha Vantage.

**Parameters:**
- `indicator`: 'RSI', 'MACD', 'SMA', 'EMA', 'BBANDS', 'ADX'
- `time_period`: Period for indicator calculation
- `series_type`: 'close', 'open', 'high', 'low'

##### get_company_overview()

```python
get_company_overview(ticker: str) -> Dict
```

Get company fundamental data.

**Example:**
```python
from echo.data_providers.alphavantage_provider import AlphaVantageProvider

provider = AlphaVantageProvider(api_key='YOUR_KEY')
quote = provider.quote('AAPL')
overview = provider.get_company_overview('AAPL')
rsi = provider.get_technical_indicator('AAPL', 'RSI', time_period=14)
```

---

### QuandlProvider

Provider for Quandl/NASDAQ Data Link.

#### Constructor

```python
QuandlProvider(api_key: Optional[str] = None)
```

#### Methods

##### get_economic_indicator()

```python
get_economic_indicator(indicator: str) -> pd.DataFrame
```

Get economic indicator from FRED database.

**Common Indicators:**
- 'GDP': Gross Domestic Product
- 'UNRATE': Unemployment Rate
- 'DGS10': 10-Year Treasury Rate
- 'CPIAUCSL': Consumer Price Index

**Example:**
```python
from echo.data_providers.quandl_provider import QuandlProvider

provider = QuandlProvider(api_key='YOUR_KEY')
gdp = provider.get_economic_indicator('GDP')
unemployment = provider.get_economic_indicator('UNRATE')
```

---

## Preprocessing

### FinancialDataPreprocessor

Data preprocessing and feature engineering.

#### Constructor

```python
FinancialDataPreprocessor(config: Optional[Dict] = None)
```

#### Methods

##### process_pipeline()

```python
process_pipeline(df: pd.DataFrame, add_indicators: bool = True) -> pd.DataFrame
```

Complete preprocessing pipeline.

**Steps:**
1. Clean data (remove duplicates, handle missing values)
2. Add technical indicators
3. Return processed DataFrame

##### add_technical_indicators()

```python
add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame
```

Add 20+ technical indicators.

**Indicators Added:**
- Returns and Log Returns
- SMA (5, 10, 20, 50)
- EMA (12, 26)
- MACD and Signal
- RSI
- Bollinger Bands
- Stochastic Oscillator
- ATR
- OBV
- Momentum and ROC

##### prepare_features()

```python
prepare_features(df: pd.DataFrame, target_col: str = 'Close') -> Tuple[pd.DataFrame, pd.Series]
```

Separate features and target.

**Returns:**
- `X`: Feature DataFrame
- `y`: Target Series

##### temporal_train_test_split()

```python
temporal_train_test_split(df: pd.DataFrame, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]
```

Split data maintaining temporal order.

**Example:**
```python
from echo.preprocessing.financial_data import FinancialDataPreprocessor
import yfinance as yf

# Get data
data = yf.Ticker("AAPL").history(period="1y")

# Preprocess
preprocessor = FinancialDataPreprocessor()
processed = preprocessor.process_pipeline(data)

# Prepare for ML
X, y = preprocessor.prepare_features(processed)

# Split
train, test = preprocessor.temporal_train_test_split(processed)
```

---

## Trading Decision Engine

### TradingDecisionEngine

AI-powered trading decision maker.

#### Constructor

```python
TradingDecisionEngine(config: Optional[Dict] = None)
```

#### Methods

##### generate_signal()

```python
generate_signal(ticker: str, current_price: float,
               ai_prediction: float, ai_confidence: float,
               technical_score: float, portfolio_value: float) -> TradeSignal
```

Generate trading signal.

**Parameters:**
- `ticker`: Stock symbol
- `current_price`: Current market price
- `ai_prediction`: AI model's price prediction
- `ai_confidence`: AI confidence (0-1)
- `technical_score`: Technical analysis score (0-100)
- `portfolio_value`: Total portfolio value

**Returns:** `TradeSignal` object with:
- `action`: TradeAction (BUY/SELL/HOLD)
- `confidence`: Combined confidence score
- `target_price`: Take-profit target
- `stop_loss`: Stop-loss price
- `position_size`: Recommended position size
- `reasoning`: Explanation

##### check_exit_conditions()

```python
check_exit_conditions(position: Dict) -> Optional[TradeSignal]
```

Check if position should be closed.

**Position Dict:**
```python
{
    'ticker': str,
    'entry_price': float,
    'current_price': float,
    'stop_loss': float,
    'take_profit': float
}
```

##### optimize_portfolio_allocation()

```python
optimize_portfolio_allocation(signals: List[TradeSignal],
                             portfolio_value: float) -> Dict[str, float]
```

Optimize allocation across multiple signals.

**Returns:** Dictionary of ticker -> allocation percentage

**Example:**
```python
from echo.engine.trading_decision import TradingDecisionEngine

engine = TradingDecisionEngine()

# Generate signal
signal = engine.generate_signal(
    ticker="AAPL",
    current_price=150.0,
    ai_prediction=155.0,
    ai_confidence=0.85,
    technical_score=75,
    portfolio_value=10000
)

print(f"Action: {signal.action.value}")
print(f"Stop Loss: ${signal.stop_loss:.2f}")
print(f"Target: ${signal.target_price:.2f}")
print(f"Position Size: {signal.position_size:.0f} shares")
```

---

## Risk Management

### RiskManager

Portfolio risk management.

#### Constructor

```python
RiskManager(config: Optional[Dict] = None)
```

**Default Configuration:**
```python
{
    'max_position_size': 0.2,    # Max 20% per position
    'risk_per_trade': 0.02,      # Risk 2% per trade
    'stop_loss_pct': 0.05,       # 5% stop loss
    'take_profit_ratio': 2.0,    # 2:1 reward:risk
    'max_portfolio_risk': 0.10,  # Max 10% portfolio risk
}
```

#### Methods

##### calculate_position_size()

```python
calculate_position_size(portfolio_value: float, entry_price: float,
                       stop_loss_price: float) -> float
```

Calculate optimal position size based on risk.

##### calculate_stop_loss()

```python
calculate_stop_loss(entry_price: float, is_long: bool = True) -> float
```

Calculate stop loss price.

##### calculate_take_profit()

```python
calculate_take_profit(entry_price: float, stop_loss_price: float,
                     is_long: bool = True) -> float
```

Calculate take profit based on risk:reward ratio.

##### assess_portfolio_risk()

```python
assess_portfolio_risk(positions: List[Dict]) -> Dict[str, float]
```

Assess overall portfolio risk.

**Returns:**
```python
{
    'total_risk': float,           # Total $ at risk
    'risk_percentage': float,      # % of portfolio at risk
    'risk_utilization': float,     # Risk utilization (0-1)
    'max_risk_allowed': float      # Max risk threshold
}
```

**Example:**
```python
from echo.engine.trading_decision import RiskManager

risk_manager = RiskManager()

# Calculate position size
size = risk_manager.calculate_position_size(
    portfolio_value=10000,
    entry_price=100,
    stop_loss_price=95
)

# Calculate targets
stop_loss = risk_manager.calculate_stop_loss(100)
take_profit = risk_manager.calculate_take_profit(100, stop_loss)

print(f"Position Size: {size:.0f} shares")
print(f"Stop Loss: ${stop_loss:.2f}")
print(f"Take Profit: ${take_profit:.2f}")
```

---

## Error Handling

All methods handle errors gracefully and return appropriate error messages or empty results.

**Common Patterns:**

```python
try:
    result = provider.quote('AAPL')
    if 'error' in result:
        print(f"Error: {result['error']}")
except Exception as e:
    print(f"Exception: {str(e)}")
```

---

## Best Practices

1. **Always validate inputs** before making trading decisions
2. **Use try-except blocks** for API calls
3. **Check for empty DataFrames** before processing
4. **Respect API rate limits** 
5. **Save model memory regularly** after training
6. **Backtest strategies** before live use
7. **Monitor model performance** over time
8. **Set appropriate risk limits**

---

For more examples, see the `/tests` directory.
