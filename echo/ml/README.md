# Machine Learning Models for Echo AI

## Overview

This package contains machine learning models for stock price prediction and market analysis. The implementations are currently **stubs/prototypes** for demonstration purposes.

## ⚠️ Important Notice

**These are NOT production-ready trained models.** They serve as:
- Architecture templates for future ML integration
- Interface definitions for model implementations
- Demonstration of AI/ML capabilities in the dashboard

## Modules

### `base.py` - Base Classes
- `BasePredictor`: Abstract base class for all ML models
- `Prediction`: Data class for model predictions
- `ModelRegistry`: Registry for managing multiple models

### `data_preprocessing.py` - Data Processing
- `FinancialDataPreprocessor`: Preprocessing pipeline for financial time series
- `FeatureEngineer`: Advanced feature engineering utilities

Features include:
- Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
- Lag features and rolling statistics
- Time-based features (day of week, month, etc.)
- Normalization and scaling
- Train/test splitting with temporal ordering

### `lstm_predictor.py` - LSTM Model
LSTM (Long Short-Term Memory) model stub for time series prediction.

**Configuration:**
- Sequence length: 60 days default
- Hidden units: 128 default
- Dropout rate: 0.2 for regularization

**In Production Would Include:**
- Actual TensorFlow/Keras implementation
- Trained weights and checkpoints
- Proper data pipeline
- Model versioning

### `transformer_predictor.py` - Transformer Model
Transformer-based model stub using self-attention mechanisms.

**Configuration:**
- d_model: 128 (embedding dimension)
- num_heads: 8 (attention heads)
- num_layers: 4 (transformer encoder layers)

**Advantages:**
- Captures long-range dependencies
- Parallel processing of sequences
- Attention weights for interpretability

## Usage Example

```python
from echo.ml.lstm_predictor import LSTMPredictor
from echo.ml.data_preprocessing import FinancialDataPreprocessor

# Initialize predictor
predictor = LSTMPredictor(sequence_length=60, hidden_units=128)

# Train on data (stub implementation)
preprocessor = FinancialDataPreprocessor()
processed_data = preprocessor.preprocess_for_training(historical_df)
metrics = predictor.train(processed_data['train_data'], target)

# Make predictions
prediction = predictor.predict("AAPL", horizon="1d")
print(f"Predicted price: ${prediction.predicted_price:.2f}")
print(f"Confidence: {prediction.confidence:.2%}")
print(f"Direction: {prediction.direction}")
```

## Production Deployment Checklist

To deploy actual ML models in production:

### 1. Data Collection
- [ ] Set up automated data pipeline
- [ ] Implement data quality checks
- [ ] Handle missing data and outliers
- [ ] Ensure sufficient historical data (2+ years recommended)

### 2. Feature Engineering
- [ ] Analyze feature correlations
- [ ] Test technical indicators effectiveness
- [ ] Add fundamental data (if available)
- [ ] Consider sentiment data integration

### 3. Model Training
- [ ] Implement actual LSTM/Transformer with TensorFlow or PyTorch
- [ ] Use proper train/validation/test split
- [ ] Implement cross-validation for time series
- [ ] Track training metrics (loss, MAE, directional accuracy)
- [ ] Implement early stopping and regularization

### 4. Model Evaluation
- [ ] Backtest on out-of-sample data
- [ ] Calculate key metrics:
  - Mean Absolute Error (MAE)
  - Root Mean Squared Error (RMSE)
  - Directional Accuracy
  - Sharpe Ratio of trading strategy
- [ ] Compare against baseline models
- [ ] Test on various market conditions

### 5. Model Deployment
- [ ] Version control for models
- [ ] Implement model serving infrastructure
- [ ] Set up monitoring and alerting
- [ ] Create model rollback procedures
- [ ] Log predictions for audit trail

### 6. Ongoing Maintenance
- [ ] Monitor prediction accuracy
- [ ] Detect model drift
- [ ] Retrain models periodically
- [ ] A/B test new model versions
- [ ] Update features based on market changes

## Model Performance Metrics

For production models, track:

### Accuracy Metrics
- **MAE (Mean Absolute Error)**: Average prediction error
- **RMSE (Root Mean Squared Error)**: Penalty for large errors
- **MAPE (Mean Absolute Percentage Error)**: Relative error
- **Directional Accuracy**: % of correct direction predictions

### Trading Metrics
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Worst peak-to-trough decline
- **Win Rate**: % of profitable trades
- **Profit Factor**: Gross profit / Gross loss

### Model Health
- **Prediction Latency**: Time to generate predictions
- **Confidence Distribution**: Are predictions well-calibrated?
- **Feature Drift**: Are input distributions changing?
- **Error Distribution**: Are errors increasing over time?

## Recommended Libraries

For production implementation:

### Deep Learning
- **TensorFlow/Keras**: Industry standard, great for LSTMs
- **PyTorch**: Flexible, preferred for research
- **Fast.ai**: High-level API, good for prototyping

### Feature Engineering
- **TA-Lib**: Technical analysis indicators
- **pandas-ta**: Pandas integration for TA
- **tsfresh**: Automated time series feature extraction

### Model Monitoring
- **MLflow**: Experiment tracking and model registry
- **Weights & Biases**: Visualization and tracking
- **TensorBoard**: Training visualization

### Backtesting
- **Backtrader**: Python backtesting framework
- **Zipline**: Algorithmic trading library
- **VectorBT**: Fast backtesting with vectorization

## Legal and Ethical Considerations

⚠️ **Important:**
- ML predictions are NOT guarantees
- Past performance ≠ future results
- Models can and will fail
- Always implement risk management
- Comply with financial regulations
- Provide appropriate disclaimers

## Resources

### Learning
- [Deep Learning for Time Series Forecasting](https://machinelearningmastery.com/deep-learning-for-time-series-forecasting/)
- [Attention Is All You Need (Transformer Paper)](https://arxiv.org/abs/1706.03762)
- [LSTM for Stock Prediction](https://towardsdatascience.com/stock-prediction-using-lstm-3d1d5c85c426)

### Datasets
- Yahoo Finance (via yfinance)
- Alpha Vantage
- Quandl
- IEX Cloud

## Contributing

To add a new model:

1. Inherit from `BasePredictor`
2. Implement required methods (`train`, `predict`, `predict_batch`)
3. Add comprehensive docstrings
4. Include example usage
5. Document hyperparameters
6. Add tests

## Support

For questions or issues with ML models, please open an issue in the repository.
