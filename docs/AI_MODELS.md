# AI Models and Machine Learning

This document describes the AI and machine learning capabilities of the Echo AI Dashboard.

## Overview

The Echo AI Dashboard provides a foundation for implementing various machine learning models for predictive analytics in financial markets. The architecture supports:

- **LSTM (Long Short-Term Memory)** - For time series prediction
- **Transformer Models** - For advanced sequence modeling
- **Reinforcement Learning** - For adaptive trading strategies
- **Explainable AI** - Using SHAP and LIME for model interpretability

## Architecture

### Base Model Interface

All ML models inherit from `BasePredictor` which provides a consistent interface:

```python
from echo.ml.base_model import BasePredictor, ModelMetrics

class YourModel(BasePredictor):
    def train(self, X, y, **kwargs):
        # Training logic
        pass
    
    def predict(self, X):
        # Prediction logic
        pass
    
    def evaluate(self, X, y):
        # Evaluation logic
        pass
```

### Model Metrics

Models return standardized metrics:

```python
@dataclass
class ModelMetrics:
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    mae: Optional[float]
    mse: Optional[float]
    rmse: Optional[float]
    r2_score: Optional[float]
    confidence_interval: Optional[tuple]
```

## Feature Engineering

The `FeatureEngineer` class provides methods for calculating technical indicators:

### Technical Indicators

```python
from echo.ml.feature_engineering import FeatureEngineer

engineer = FeatureEngineer()

# RSI (Relative Strength Index)
rsi = engineer.calculate_rsi(price_series, period=14)

# MACD (Moving Average Convergence Divergence)
macd_df = engineer.calculate_macd(price_series)

# Bollinger Bands
bb_df = engineer.calculate_bollinger_bands(price_series, period=20, num_std=2)

# Moving Averages
sma_df = engineer.calculate_moving_averages(price_series, periods=[5, 10, 20, 50, 200])

# Comprehensive feature engineering
features_df = engineer.engineer_features(ohlcv_df)
```

### Available Indicators

1. **RSI (Relative Strength Index)**
   - Measures momentum and overbought/oversold conditions
   - Range: 0-100
   - Default period: 14

2. **MACD (Moving Average Convergence Divergence)**
   - Trend-following momentum indicator
   - Components: MACD line, Signal line, Histogram
   - Default periods: 12, 26, 9

3. **Bollinger Bands**
   - Volatility indicator with upper and lower bands
   - Default: 20-period SMA ± 2 standard deviations

4. **Moving Averages**
   - Simple Moving Averages (SMA) for trend identification
   - Common periods: 5, 10, 20, 50, 200 days

5. **Momentum**
   - Rate of price change over time
   - Default period: 14

6. **Volatility**
   - Rolling standard deviation of returns
   - Measures market uncertainty

7. **Returns**
   - Percentage price changes
   - Used for performance analysis

## Implementing Custom Models

### Example: LSTM Price Predictor

```python
import numpy as np
from echo.ml.base_model import BasePredictor, ModelMetrics

class LSTMPredictor(BasePredictor):
    """LSTM model for price prediction."""
    
    def __init__(self, sequence_length=60, units=50):
        super().__init__("LSTM_Predictor")
        self.sequence_length = sequence_length
        self.units = units
        self.model = None
    
    def train(self, X, y, epochs=50, batch_size=32):
        """Train the LSTM model."""
        # Reshape data for LSTM
        X_reshaped = self._reshape_for_lstm(X)
        
        # Build model (requires TensorFlow/Keras)
        # self.model = self._build_lstm_model()
        # history = self.model.fit(X_reshaped, y, epochs=epochs, batch_size=batch_size)
        
        self.is_trained = True
        
        # Calculate and return metrics
        predictions = self.predict(X)
        return self._calculate_metrics(y, predictions)
    
    def predict(self, X):
        """Make predictions."""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X_reshaped = self._reshape_for_lstm(X)
        # predictions = self.model.predict(X_reshaped)
        # return predictions
        pass
    
    def evaluate(self, X, y):
        """Evaluate model performance."""
        predictions = self.predict(X)
        return self._calculate_metrics(y, predictions)
```

### Example: Reinforcement Learning Agent

```python
class TradingAgent(BasePredictor):
    """Reinforcement learning agent for trading."""
    
    def __init__(self, state_size, action_size):
        super().__init__("RL_Trading_Agent")
        self.state_size = state_size
        self.action_size = action_size  # Buy, Hold, Sell
        self.memory = []
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
    
    def act(self, state):
        """Choose an action based on current state."""
        # Epsilon-greedy action selection
        if np.random.random() <= self.epsilon:
            return np.random.randint(self.action_size)
        
        # Use model to predict best action
        # q_values = self.model.predict(state)
        # return np.argmax(q_values[0])
        pass
    
    def train(self, state, action, reward, next_state, done):
        """Train the agent with experience replay."""
        self.memory.append((state, action, reward, next_state, done))
        
        if len(self.memory) > 32:
            # Sample batch and train
            # batch = random.sample(self.memory, 32)
            # self._replay(batch)
            pass
```

## Model Explainability

### Using SHAP (SHapley Additive exPlanations)

```python
import shap

class ExplainableModel(BasePredictor):
    def explain_prediction(self, X, instance_idx=0):
        """Explain a prediction using SHAP."""
        explainer = shap.Explainer(self.model)
        shap_values = explainer(X)
        
        return {
            'shap_values': shap_values[instance_idx],
            'base_value': explainer.expected_value,
            'feature_values': X.iloc[instance_idx].to_dict()
        }
```

### Using LIME (Local Interpretable Model-agnostic Explanations)

```python
from lime import lime_tabular

class ExplainableModel(BasePredictor):
    def explain_prediction(self, X, instance_idx=0):
        """Explain a prediction using LIME."""
        explainer = lime_tabular.LimeTabularExplainer(
            X.values,
            feature_names=X.columns,
            mode='regression'
        )
        
        explanation = explainer.explain_instance(
            X.iloc[instance_idx].values,
            self.model.predict
        )
        
        return explanation.as_list()
```

## Model Evaluation

### Training Pipeline

```python
from sklearn.model_selection import train_test_split
from echo.ml.feature_engineering import FeatureEngineer

# 1. Load and prepare data
df = provider.history("AAPL", period="2y")

# 2. Engineer features
engineer = FeatureEngineer()
features_df = engineer.engineer_features(df)

# 3. Prepare target variable (e.g., next day returns)
features_df['Target'] = features_df['Close'].pct_change().shift(-1)
features_df = features_df.dropna()

# 4. Split data
X = features_df.drop('Target', axis=1)
y = features_df['Target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# 5. Train model
model = YourModel()
train_metrics = model.train(X_train, y_train)

# 6. Evaluate on test set
test_metrics = model.evaluate(X_test, y_test)

print(f"Train MAE: {train_metrics.mae:.4f}")
print(f"Test MAE: {test_metrics.mae:.4f}")
```

### Backtesting

```python
class Backtester:
    """Simple backtesting framework."""
    
    def __init__(self, model, initial_capital=10000):
        self.model = model
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []
    
    def run(self, X, y_true, prices):
        """Run backtest on historical data."""
        predictions = self.model.predict(X)
        
        for i, (pred, price) in enumerate(zip(predictions, prices)):
            # Trading logic based on predictions
            if pred > 0.01:  # Buy signal
                self._buy(price)
            elif pred < -0.01:  # Sell signal
                self._sell(price)
        
        return self._calculate_performance()
```

## Best Practices

1. **Data Quality**: Ensure clean, complete data before training
2. **Feature Scaling**: Normalize features for neural networks
3. **Cross-Validation**: Use time-series aware cross-validation
4. **Overfitting Prevention**: Monitor train/test performance gap
5. **Model Versioning**: Save and version trained models
6. **Regular Retraining**: Update models with new data periodically
7. **Risk Management**: Always include risk controls in trading strategies

## Future Enhancements

- [ ] Implement LSTM price predictor
- [ ] Add Transformer-based models
- [ ] Develop reinforcement learning trading agent
- [ ] Integrate SHAP/LIME explainability
- [ ] Add automated hyperparameter tuning
- [ ] Implement ensemble methods
- [ ] Add model monitoring and drift detection
- [ ] Create automated retraining pipeline

## Resources

- [TensorFlow/Keras Documentation](https://www.tensorflow.org/)
- [PyTorch Documentation](https://pytorch.org/)
- [SHAP Documentation](https://shap.readthedocs.io/)
- [LIME Documentation](https://github.com/marcotcr/lime)
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)

---

For implementation examples, see the `examples/` directory (coming soon).
