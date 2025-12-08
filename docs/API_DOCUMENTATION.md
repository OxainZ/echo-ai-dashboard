# Echo AI Dashboard - API Documentation

## Table of Contents
- [AI Models API](#ai-models-api)
- [Data Providers API](#data-providers-api)
- [Echo Engine API](#echo-engine-api)
- [Utilities API](#utilities-api)

## AI Models API

### LSTMStockPredictor

Long Short-Term Memory neural network for stock price prediction.

#### Initialization

```python
from echo.ai_models import LSTMStockPredictor

predictor = LSTMStockPredictor(
    lookback_days=60,        # Number of historical days for sequences
    prediction_horizon=5,    # Number of days to predict ahead
    features=['Close', 'Volume', 'High', 'Low']  # Features to use
)
```

#### Methods

##### `prepare_data(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]`

Prepare and normalize data for LSTM training.

**Parameters:**
- `df`: DataFrame with historical stock data

**Returns:**
- Tuple of (X_sequences, y_targets) as numpy arrays

**Example:**
```python
X, y = predictor.prepare_data(historical_data)
print(f"Sequences shape: {X.shape}, Targets shape: {y.shape}")
```

##### `train(df: pd.DataFrame, epochs: int = 50, batch_size: int = 32, validation_split: float = 0.2) -> Dict[str, List[float]]`

Train the LSTM model on historical data.

**Parameters:**
- `df`: Historical stock data DataFrame
- `epochs`: Number of training epochs (default: 50)
- `batch_size`: Training batch size (default: 32)
- `validation_split`: Fraction for validation (default: 0.2)

**Returns:**
- Dictionary containing training history (loss, val_loss, etc.)

**Example:**
```python
history = predictor.train(
    historical_data,
    epochs=100,
    batch_size=64
)
print(f"Final loss: {history['loss'][-1]}")
```

##### `predict(recent_data: pd.DataFrame) -> Dict[str, Any]`

Generate predictions for future stock prices.

**Parameters:**
- `recent_data`: Recent historical data (at least `lookback_days` rows)

**Returns:**
Dictionary with:
- `predictions`: Array of predicted prices
- `confidence`: Prediction confidence score (0-1)
- `dates`: Predicted dates
- `trend`: Overall trend direction ('upward', 'downward', 'sideways')
- `last_actual_price`: Most recent actual price
- `predicted_change_pct`: Percentage change prediction

**Example:**
```python
predictions = predictor.predict(recent_data)

print(f"Trend: {predictions['trend']}")
print(f"Confidence: {predictions['confidence']:.2%}")
print(f"Predicted prices: {predictions['predictions']}")
print(f"Expected change: {predictions['predicted_change_pct']:.2f}%")
```

##### `continuous_learn(new_data: pd.DataFrame, learning_rate: float = 0.001) -> bool`

Update the model with new data for continuous learning.

**Parameters:**
- `new_data`: New stock data to learn from
- `learning_rate`: Learning rate for incremental updates

**Returns:**
- True if learning was successful, False otherwise

**Example:**
```python
success = predictor.continuous_learn(new_market_data)
if success:
    print("Model updated with new data")
```

##### `evaluate(test_data: pd.DataFrame) -> Dict[str, float]`

Evaluate model performance on test data.

**Parameters:**
- `test_data`: Test dataset for evaluation

**Returns:**
Dictionary with metrics:
- `mae`: Mean Absolute Error
- `rmse`: Root Mean Square Error
- `mape`: Mean Absolute Percentage Error
- `accuracy`: Overall accuracy score

**Example:**
```python
metrics = predictor.evaluate(test_data)
print(f"MAE: {metrics['mae']:.2f}")
print(f"Accuracy: {metrics['accuracy']:.2%}")
```

### SentimentAnalyzer

Analyze market sentiment from various signals and indicators.

#### Initialization

```python
from echo.ai_models import SentimentAnalyzer

analyzer = SentimentAnalyzer()
```

#### Methods

##### `analyze(signals: List[Dict]) -> Dict[str, Any]`

Analyze market sentiment from signals.

**Parameters:**
- `signals`: List of market signals with severity and scores

**Returns:**
Dictionary with:
- `sentiment`: Sentiment label ('strongly_bullish', 'bullish', 'neutral', 'bearish', 'strongly_bearish')
- `confidence`: Confidence score (0-1)
- `score`: Numerical sentiment score (0-100)
- `analysis`: Text analysis description
- `bullish_count`: Number of bullish signals
- `bearish_count`: Number of bearish signals
- `neutral_count`: Number of neutral signals

**Example:**
```python
sentiment = analyzer.analyze(market_signals)

print(f"Market Sentiment: {sentiment['sentiment']}")
print(f"Confidence: {sentiment['confidence']:.2%}")
print(f"Analysis: {sentiment['analysis']}")
print(f"Bullish signals: {sentiment['bullish_count']}")
```

### Technical Indicators

Calculate common technical indicators for stock analysis.

#### Function Signature

```python
def calculate_technical_indicators(
    df: pd.DataFrame,
    periods: Optional[Dict[str, int]] = None
) -> pd.DataFrame
```

**Parameters:**
- `df`: DataFrame with OHLCV data
- `periods`: Dictionary specifying periods for indicators
  - Default: `{'sma': 20, 'ema': 12, 'rsi': 14, 'macd_fast': 12, 'macd_slow': 26}`

**Returns:**
- DataFrame with additional columns for technical indicators

**Available Indicators:**
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands (Upper and Lower)

**Example:**
```python
from echo.ai_models import calculate_technical_indicators

# Use default periods
data_with_indicators = calculate_technical_indicators(stock_data)

# Custom periods
custom_periods = {
    'sma': 50,
    'ema': 20,
    'rsi': 21,
    'macd_fast': 12,
    'macd_slow': 26
}
data_with_indicators = calculate_technical_indicators(stock_data, custom_periods)

# Access indicators
print(data_with_indicators[['Close', 'SMA_50', 'RSI', 'MACD']].tail())
```

## Data Providers API

### YFinanceProvider

Yahoo Finance data provider for real-time and historical market data.

#### Initialization

```python
from echo.data_providers.yfinance_provider import YFinanceProvider

provider = YFinanceProvider()
```

#### Methods

##### `quote(ticker: str) -> Dict`

Get current quote for a ticker.

**Parameters:**
- `ticker`: Stock ticker symbol (e.g., 'AAPL', 'TSLA')

**Returns:**
Dictionary with:
- `ticker`: Ticker symbol
- `price`: Current price
- `prev_close`: Previous closing price
- `currency`: Currency (default: 'USD')

**Example:**
```python
quote = provider.quote('AAPL')
print(f"Current price: ${quote['price']:.2f}")
print(f"Previous close: ${quote['prev_close']:.2f}")
```

##### `history(ticker: str, period: str = '1mo', interval: str = '1d') -> pd.DataFrame`

Get historical price data.

**Parameters:**
- `ticker`: Stock ticker symbol
- `period`: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
- `interval`: Data interval ('1m', '5m', '15m', '1h', '1d', '1wk', '1mo')

**Returns:**
- DataFrame with columns: Open, High, Low, Close, Volume, Dividends, Stock Splits

**Example:**
```python
# Get 3 months of daily data
data = provider.history('TSLA', period='3mo', interval='1d')

# Get intraday 5-minute data for 1 day
intraday = provider.history('SPY', period='1d', interval='5m')

print(data.head())
```

## Echo Engine API

### EchoEngine

Core trading engine that processes rules and generates verdicts.

#### Initialization

```python
from echo.engine.echo_engine import EchoEngine

engine = EchoEngine(config_path='echo/config.yaml')
```

#### Methods

##### `run() -> Verdict`

Execute all trading rules and generate a verdict.

**Returns:**
- `Verdict` object with:
  - `asof`: Timestamp
  - `composite`: Composite conviction score (0-100)
  - `risk_label`: Risk level ('Low', 'Moderate', 'Elevated', 'High')
  - `cap_efficiency`: Capital efficiency percentage
  - `signals`: List of Signal objects
  - `actions`: List of recommended actions
  - `allocations`: Portfolio allocations

**Example:**
```python
engine = EchoEngine('echo/config.yaml')
verdict = engine.run()

print(f"Conviction: {verdict.composite:.1f}/100")
print(f"Risk: {verdict.risk_label}")
print(f"Actions: {verdict.actions}")

for signal in verdict.signals:
    print(f"{signal.name}: {signal.score:.0f} - {signal.severity}")
```

### Verdict

Result object from Echo Engine analysis.

**Attributes:**
- `asof` (str): Timestamp of analysis
- `composite` (float): Composite conviction score
- `risk_label` (str): Risk level assessment
- `cap_efficiency` (float): Capital efficiency percentage
- `signals` (List[Signal]): List of market signals
- `actions` (List[str]): Recommended actions
- `allocations` (Dict[str, str]): Portfolio allocations

### Signal

Individual market signal result.

**Attributes:**
- `name` (str): Signal name
- `score` (float): Signal score (0-100)
- `severity` (str): Severity level ('green', 'yellow', 'red')
- `detail` (str): Detailed explanation

## Utilities API

### Date Utilities

```python
from echo.utils.dates import now_tz, fmt_ts

# Get current time in specific timezone
current_time = now_tz('America/Chicago')

# Format timestamp
formatted = fmt_ts(current_time)
```

### Logging Utilities

```python
from echo.utils.logging import get_logger

logger = get_logger('MyModule')
logger.info('Processing data...')
logger.error('An error occurred')
```

## Complete Usage Example

```python
from echo.engine.echo_engine import EchoEngine
from echo.ai_models import LSTMStockPredictor, SentimentAnalyzer, calculate_technical_indicators
from echo.data_providers.yfinance_provider import YFinanceProvider

# Initialize components
engine = EchoEngine('echo/config.yaml')
provider = YFinanceProvider()
predictor = LSTMStockPredictor(lookback_days=60, prediction_horizon=5)
analyzer = SentimentAnalyzer()

# Get current market verdict
verdict = engine.run()

# Analyze sentiment
sentiment = analyzer.analyze(verdict.signals)
print(f"Market Sentiment: {sentiment['sentiment']} ({sentiment['confidence']:.2%} confidence)")

# Get historical data and add technical indicators
ticker = 'AAPL'
data = provider.history(ticker, period='1y', interval='1d')
data_with_indicators = calculate_technical_indicators(data)

# Train prediction model
predictor.train(data_with_indicators, epochs=50)

# Make predictions
recent_data = data_with_indicators.tail(100)
predictions = predictor.predict(recent_data)

print(f"\n{ticker} Prediction:")
print(f"Trend: {predictions['trend']}")
print(f"Confidence: {predictions['confidence']:.2%}")
print(f"Predicted change: {predictions['predicted_change_pct']:.2f}%")
print(f"Next 5 days: {predictions['predictions']}")

# Continuous learning with new data
new_data = provider.history(ticker, period='5d', interval='1d')
predictor.continuous_learn(new_data)

# Evaluate model
metrics = predictor.evaluate(data_with_indicators.tail(100))
print(f"\nModel Performance:")
print(f"MAE: {metrics['mae']:.2f}")
print(f"Accuracy: {metrics['accuracy']:.2%}")
```

## Error Handling

All API functions include proper error handling. Wrap calls in try-except blocks:

```python
try:
    predictions = predictor.predict(recent_data)
except ValueError as e:
    print(f"Insufficient data: {e}")
except RuntimeError as e:
    print(f"Model not trained: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Type Hints

All functions include type hints for better IDE support and type checking:

```python
def predict(self, recent_data: pd.DataFrame) -> Dict[str, Any]:
    """Type-hinted function signature"""
    pass
```

Use with mypy for static type checking:
```bash
mypy echo/
```
