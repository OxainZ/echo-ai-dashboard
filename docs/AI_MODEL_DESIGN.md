# AI Model Design Documentation

## Overview

Echo AI Dashboard uses multiple machine learning and statistical models to provide trading intelligence, predictions, and risk analysis. This document describes the architecture, design decisions, and implementation details of the AI components.

## Table of Contents
1. [Model Architecture](#model-architecture)
2. [Stock Price Prediction](#stock-price-prediction)
3. [Trading Signal Generation](#trading-signal-generation)
4. [Sentiment Analysis](#sentiment-analysis)
5. [Backtesting Engine](#backtesting-engine)
6. [Portfolio Analytics](#portfolio-analytics)

---

## Model Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    Data Sources                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ YFinance │  │ AlphaVan │  │  Quandl  │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└───────┼────────────┼──────────────┼─────────────────────┘
        │            │              │
        └────────────┴──────────────┘
                     │
        ┌────────────▼────────────┐
        │   Data Pipeline          │
        │  • Caching               │
        │  • Sanitization          │
        │  • Augmentation          │
        └────────────┬─────────────┘
                     │
        ┌────────────▼────────────┐
        │   ML Models              │
        │  • Predictor             │
        │  • Sentiment Analyzer    │
        │  • Signal Generator      │
        └────────────┬─────────────┘
                     │
        ┌────────────▼────────────┐
        │   Analytics Engine       │
        │  • Portfolio Tracker     │
        │  • Risk Calculator       │
        │  • Backtester            │
        └────────────┬─────────────┘
                     │
        ┌────────────▼────────────┐
        │   Presentation Layer     │
        │  • Streamlit Dashboard   │
        │  • Reports               │
        └──────────────────────────┘
```

---

## Stock Price Prediction

### StockPredictor Class

Location: `echo/ml/predictor.py`

#### Prediction Methods

1. **Simple Statistical Model** (Default)
   - Uses moving averages and momentum indicators
   - Calculates trend strength and direction
   - Generates confidence intervals based on volatility
   - **Pros**: Fast, no training required, interpretable
   - **Cons**: Limited accuracy, no complex pattern recognition

2. **LSTM Model** (Framework only)
   - Long Short-Term Memory networks for time series
   - Placeholder for future implementation
   - Would require TensorFlow/PyTorch
   - **Pros**: Captures temporal dependencies, handles non-linearity
   - **Cons**: Requires training data, computational overhead

3. **Transformer Model** (Framework only)
   - Attention-based architecture for sequence modeling
   - Placeholder for future implementation
   - Would require transformer libraries
   - **Pros**: State-of-the-art performance, parallel processing
   - **Cons**: High computational cost, large data requirements

#### Prediction Output

```python
{
    'ticker': 'AAPL',
    'predictions': [
        {
            'day': 1,
            'date': '2024-01-15',
            'predicted_price': 182.50,
            'lower_bound': 178.30,
            'upper_bound': 186.70
        },
        # ... more days
    ],
    'confidence': 0.75,
    'trend': 'bullish',
    'trend_strength': 0.08,
    'model_type': 'simple_statistical',
    'last_price': 180.00,
    'volatility': 0.025
}
```

#### Algorithm Details

**Simple Statistical Prediction**

1. Calculate moving averages (MA7, MA30)
2. Compute momentum from recent returns
3. Estimate volatility from historical standard deviation
4. Determine trend direction (MA7 vs MA30)
5. Project future prices using trend and volatility
6. Add confidence intervals based on historical volatility

**Confidence Calculation**
```
confidence = min(0.85, max(0.45, 1 - volatility * 5))
```

---

## Trading Signal Generation

### TradingSignalGenerator Class

Location: `echo/ml/predictor.py`

#### Signal Types
- **BUY**: Expected return > 2% over 5 days
- **SELL**: Expected return < -2% over 5 days
- **HOLD**: Expected return between -2% and 2%

#### Signal Strength
```python
if signal == "BUY":
    strength = min(1.0, expected_return * 20)
elif signal == "SELL":
    strength = min(1.0, abs(expected_return) * 20)
else:
    strength = 0.5
```

#### Output Format

```python
{
    'ticker': 'TSLA',
    'signal': 'BUY',
    'strength': 0.85,
    'confidence': 0.72,
    'expected_return_5d': 4.2,
    'current_price': 250.00,
    'predicted_price_5d': 260.50,
    'reasoning': [
        'Expected 4.2% upside over 5 days',
        'Stock is in bullish trend',
        'Low volatility indicates stability'
    ],
    'trend': 'bullish',
    'volatility': 0.018
}
```

---

## Sentiment Analysis

### SentimentAnalyzer Class

Location: `echo/ml/sentiment.py`

#### Analysis Methods

1. **Keyword-Based Analysis** (Current implementation)
   - Maintains positive/negative keyword dictionaries
   - Counts sentiment words in text
   - Calculates sentiment score (-1 to 1)
   - Fast and lightweight

2. **FinBERT Model** (Framework only)
   - Pre-trained BERT model fine-tuned for financial sentiment
   - Would use `transformers` library
   - Higher accuracy for financial text

#### Keyword Dictionaries

**Positive Keywords**:
- bullish, growth, profit, gain, rise, surge, rally
- positive, strong, beat, exceed, outperform, upside
- momentum, upgrade, buy, long, optimistic, boost

**Negative Keywords**:
- bearish, loss, decline, fall, drop, crash, plunge
- negative, weak, miss, underperform, downside, risk
- downgrade, sell, short, pessimistic, concern, threat

#### Sentiment Calculation

```python
score = (positive_count - negative_count) / total_sentiment_words

if score > 0.2:
    sentiment = 'positive'
elif score < -0.2:
    sentiment = 'negative'
else:
    sentiment = 'neutral'
```

#### Batch Analysis

For multiple articles:
```python
overall_sentiment = determine_from_distribution(
    positive_count, negative_count, neutral_count
)
confidence = min(0.9, 0.4 + (article_count / 20))
```

---

## Backtesting Engine

### Backtester Class

Location: `echo/ml/backtester.py`

#### Features

1. **Portfolio Simulation**
   - Track cash and holdings over time
   - Execute buy/sell orders
   - Record all transactions

2. **Strategy Execution**
   - Custom strategy functions
   - Access to historical data
   - Trade execution at historical prices

3. **Performance Metrics**
   - Total return
   - Sharpe ratio
   - Maximum drawdown
   - Win rate
   - Volatility (annualized)

#### Usage Example

```python
from echo.ml.backtester import Backtester, simple_moving_average_strategy

# Initialize backtester
backtester = Backtester(initial_capital=10000)

# Define strategy
strategy = simple_moving_average_strategy(short_window=20, long_window=50)

# Prepare data
data = {
    'AAPL': apple_df,
    'TSLA': tesla_df
}

# Run backtest
results = backtester.run(
    strategy=strategy,
    data=data,
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# Results include:
# - initial_capital, final_value
# - total_return, sharpe_ratio
# - max_drawdown, volatility
# - trades, portfolio_history
```

#### Performance Metrics Calculations

**Sharpe Ratio**:
```python
sharpe = (total_return / volatility) if volatility > 0 else 0
```

**Maximum Drawdown**:
```python
cumulative = portfolio_values
running_max = cumulative.expanding().max()
drawdown = (cumulative - running_max) / running_max
max_drawdown = drawdown.min()
```

**Volatility (Annualized)**:
```python
returns = values.pct_change()
volatility = returns.std() * sqrt(252)
```

---

## Portfolio Analytics

### PortfolioTracker Class

Location: `echo/portfolio/tracker.py`

#### Core Features

1. **Position Tracking**
   - Average cost basis calculation
   - Unrealized P&L tracking
   - Return percentage calculation

2. **Transaction History**
   - Buy/sell records
   - Realized P&L calculation
   - Historical snapshots

3. **Performance Metrics**
   - Total value and returns
   - Realized/unrealized P&L
   - Sharpe ratio
   - Volatility
   - Days active

4. **Risk Metrics**
   - Concentration risk
   - Cash buffer
   - Exposure percentage
   - Diversification score

#### Metrics Formulas

**Total Return**:
```python
total_return = (total_value - total_invested) / total_invested * 100
```

**Diversification Score**:
```python
diversification = min(100, num_positions * 20)
```

**Risk Level Determination**:
```python
if max_concentration > 50:
    risk_level = "High"
elif max_concentration > 30 or num_positions < 3:
    risk_level = "Moderate"
else:
    risk_level = "Low"
```

#### Snapshot Format

```python
{
    'date': datetime,
    'total_value': 50000.00,
    'cash': 10000.00,
    'holdings_value': 40000.00,
    'num_positions': 5,
    'positions': {
        'AAPL': {
            'shares': 100,
            'avg_cost': 150.00,
            'current_price': 180.00,
            'market_value': 18000.00,
            'unrealized_pnl': 3000.00,
            'return_pct': 20.0
        },
        # ... more positions
    }
}
```

---

## Data Flow

### 1. Data Acquisition
```
Provider API → Raw Data → Sanitization → Cache → Application
```

### 2. Prediction Pipeline
```
Historical Data → Feature Engineering → Model Inference → Predictions
```

### 3. Signal Generation
```
Predictions + Current Data → Analysis → Trading Signal + Reasoning
```

### 4. Backtesting Pipeline
```
Historical Data → Strategy Function → Portfolio Simulation → Performance Metrics
```

---

## Future Enhancements

### Short Term
1. Implement actual LSTM model training
2. Add more technical indicators
3. Integrate FinBERT for sentiment
4. Add ensemble prediction methods

### Medium Term
1. Implement transformer-based models
2. Add reinforcement learning for strategy optimization
3. Multi-timeframe analysis
4. Advanced risk modeling (VaR, CVaR)

### Long Term
1. Deep learning for pattern recognition
2. Alternative data integration
3. Real-time model updates
4. Automated hyperparameter tuning

---

## Model Evaluation

### Prediction Accuracy Metrics
- Mean Absolute Error (MAE)
- Root Mean Square Error (RMSE)
- Mean Absolute Percentage Error (MAPE)
- Direction Accuracy

### Trading Performance Metrics
- Alpha and Beta
- Information Ratio
- Calmar Ratio
- Sortino Ratio

### Risk Metrics
- Value at Risk (VaR)
- Conditional Value at Risk (CVaR)
- Beta
- Maximum Drawdown Duration

---

## References

1. "Deep Learning for Trading" - Various papers on LSTM/Transformer applications
2. "Algorithmic Trading" - Ernest P. Chan
3. "Advances in Financial Machine Learning" - Marcos López de Prado
4. FinBERT: https://github.com/ProsusAI/finBERT
5. Yahoo Finance API: https://pypi.org/project/yfinance/

---

Last Updated: December 2024
Version: 1.0
