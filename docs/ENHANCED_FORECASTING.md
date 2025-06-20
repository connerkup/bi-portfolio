# Enhanced Forecasting Models

This document describes the enhanced forecasting capabilities added to the PackagingCo BI Portfolio project.

## Overview

The forecasting module has been enhanced with advanced time-series forecasting models beyond the original LinearRegression approach. The new models provide better handling of seasonality, trends, and complex time-series patterns.

## Available Models

### 1. Exponential Smoothing (Original Enhanced)
- **Method**: `simple_linear_forecast()`
- **Best for**: Smooth forecasts with trend and seasonality
- **Data requirements**: Minimum 3 months of data
- **Features**: 
  - Smooth transitions from historical data
  - Trend consideration
  - Subtle seasonal adjustments

### 2. Moving Average (Original Enhanced)
- **Method**: `moving_average_forecast()`
- **Best for**: Stable forecasts with trend consideration
- **Data requirements**: Minimum 3 months of data
- **Features**:
  - Configurable window size
  - Trend calculation from recent moving averages
  - Seasonal adjustments

### 3. Facebook Prophet (New)
- **Method**: `prophet_forecast()`
- **Best for**: Data with seasonality, trend changes, and holiday effects
- **Data requirements**: Minimum 3 months of data
- **Features**:
  - Automatic seasonality detection
  - Holiday effects handling
  - Missing data tolerance
  - Confidence intervals
  - Trend change detection

### 4. ARIMA (New)
- **Method**: `arima_forecast()`
- **Best for**: Stationary time series with trend and seasonality
- **Data requirements**: Minimum 6 months of data
- **Features**:
  - Configurable (p, d, q) parameters
  - Seasonal ARIMA support
  - Model diagnostics (AIC, BIC)

### 5. Auto-ARIMA (New)
- **Method**: `auto_arima_forecast()`
- **Best for**: Automatic parameter selection for ARIMA models
- **Data requirements**: Minimum 6 months of data
- **Features**:
  - Automatic parameter optimization
  - AIC/BIC-based model selection
  - Seasonal component detection

## Model Comparison

The enhanced system includes a model comparison feature that:

1. **Splits data** into training and testing sets
2. **Generates forecasts** using multiple models
3. **Calculates performance metrics**:
   - Mean Absolute Error (MAE)
   - Mean Squared Error (MSE)
   - Root Mean Squared Error (RMSE)
   - Mean Absolute Percentage Error (MAPE)
4. **Provides recommendations** based on performance

## Usage Examples

### Basic Forecasting
```python
from packagingco_insights.analysis.forecasting import SalesForecaster

# Initialize forecaster
forecaster = SalesForecaster(sales_data)

# Generate forecast with Prophet
prophet_forecast = forecaster.prophet_forecast(
    periods=6,
    group_by='product_line',
    seasonality_mode='multiplicative',
    yearly_seasonality=True
)

# Generate forecast with ARIMA
arima_forecast = forecaster.arima_forecast(
    periods=6,
    group_by='product_line',
    order=(1, 1, 1)
)
```

### Model Comparison
```python
# Compare multiple models
comparison_results = forecaster.compare_forecasting_models(
    periods=6,
    group_by='product_line',
    test_size=0.2
)

# Get performance metrics
if 'performance_metrics' in comparison_results:
    metrics = comparison_results['performance_metrics']
    print(metrics.groupby('model')[['mae', 'mape', 'rmse']].mean())

# Get model recommendations
recommendations = forecaster.get_model_recommendations(metrics)
```

## Installation Requirements

The enhanced forecasting requires additional packages:

```bash
pip install prophet>=1.1.0
pip install statsmodels>=0.13.0
pip install pmdarima>=2.0.0
```

These are already included in the project's `requirements.txt`.

## Model Selection Guidelines

### Choose Prophet when:
- You have seasonal patterns in your data
- You expect trend changes over time
- You have holiday effects
- You want confidence intervals
- You have sufficient historical data (>3 months)

### Choose ARIMA when:
- Your time series is stationary
- You have clear trend patterns
- You want fine control over model parameters
- You have sufficient historical data (>6 months)

### Choose Auto-ARIMA when:
- You want automatic parameter selection
- You're unsure about optimal ARIMA parameters
- You want to compare multiple ARIMA configurations
- You have sufficient historical data (>6 months)

### Choose Exponential Smoothing when:
- You want smooth forecasts
- You have limited historical data
- You need quick forecasts
- You want simple trend handling

### Choose Moving Average when:
- You want stable forecasts
- You have noisy data
- You need simple trend consideration
- You want configurable smoothing

## Performance Considerations

- **Prophet**: Can be slower for large datasets but provides robust seasonality handling
- **ARIMA**: Fast for small to medium datasets, slower for large datasets
- **Auto-ARIMA**: Can be slow due to parameter search, but provides optimal results
- **Exponential Smoothing**: Fastest option, good for real-time applications
- **Moving Average**: Very fast, good for simple trend analysis

## Error Handling

All models include comprehensive error handling:
- Insufficient data warnings
- Missing value handling
- Model fitting error recovery
- Graceful degradation when advanced models fail

## Integration with Streamlit

The enhanced forecasting is fully integrated with the Streamlit application:

1. **Model Selection**: Dropdown menu with available models
2. **Model Comparison**: Interactive comparison interface
3. **Performance Metrics**: Visual comparison charts
4. **Recommendations**: Automated model recommendations
5. **Confidence Intervals**: Display for Prophet forecasts

## Testing

Run the enhanced forecasting test:

```bash
python scripts/test_enhanced_forecasting.py
```

This will test all available models and provide performance comparisons.

## Future Enhancements

Potential future improvements:
- LSTM neural networks for deep learning forecasting
- Ensemble methods combining multiple models
- Real-time forecasting with streaming data
- Automated model retraining
- More sophisticated seasonality detection
- Holiday effect customization
- External factor integration (weather, events, etc.) 