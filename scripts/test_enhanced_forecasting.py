#!/usr/bin/env python3
"""
Test script for enhanced forecasting capabilities.
Demonstrates the new Prophet and ARIMA forecasting methods.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from packagingco_insights.analysis.forecasting import SalesForecaster
from packagingco_insights.utils.data_generator import MockDataGenerator

def test_enhanced_forecasting():
    """Test the enhanced forecasting capabilities."""
    print("🧪 Testing Enhanced Forecasting Models")
    print("=" * 50)
    
    # Generate sample data
    print("📊 Generating sample sales data...")
    generator = MockDataGenerator(seed=42)
    sample_data = generator.generate_transaction_level_sales(
        start_date='2023-01-01',
        end_date='2024-01-01',
        daily_transactions=50
    )
    
    # Initialize forecaster
    forecaster = SalesForecaster(sample_data)
    
    print(f"✅ Data prepared: {len(forecaster.prepared_data)} records")
    print(f"📅 Date range: {forecaster.prepared_data['date'].min()} to {forecaster.prepared_data['date'].max()}")
    print(f"🏷️  Product lines: {forecaster.prepared_data['product_line'].unique()}")
    print()
    
    # Test different forecasting models
    models_to_test = [
        ('Exponential Smoothing', 'simple_linear_forecast'),
        ('Moving Average', 'moving_average_forecast'),
    ]
    
    # Add advanced models if available
    try:
        from prophet import Prophet
        models_to_test.append(('Prophet', 'prophet_forecast'))
        print("✅ Prophet is available")
    except ImportError:
        print("❌ Prophet not available")
    
    try:
        from statsmodels.tsa.arima.model import ARIMA
        models_to_test.append(('ARIMA', 'arima_forecast'))
        print("✅ Statsmodels ARIMA is available")
    except ImportError:
        print("❌ Statsmodels not available")
    
    try:
        from pmdarima import auto_arima
        models_to_test.append(('Auto-ARIMA', 'auto_arima_forecast'))
        print("✅ Auto-ARIMA is available")
    except ImportError:
        print("❌ pmdarima not available")
    
    print()
    
    # Test each model
    results = {}
    for model_name, method_name in models_to_test:
        print(f"🔮 Testing {model_name}...")
        try:
            method = getattr(forecaster, method_name)
            
            if method_name == 'prophet_forecast':
                forecast = method(periods=6, group_by='product_line')
            elif method_name in ['arima_forecast', 'auto_arima_forecast']:
                forecast = method(periods=6, group_by='product_line')
            else:
                forecast = method(periods=6, group_by='product_line')
            
            if not forecast.empty:
                total_forecast = forecast['forecasted_revenue'].sum()
                print(f"   ✅ {model_name}: ${total_forecast:,.0f} total forecast")
                results[model_name] = forecast
            else:
                print(f"   ⚠️  {model_name}: No forecast generated")
                
        except Exception as e:
            print(f"   ❌ {model_name}: Error - {str(e)}")
    
    print()
    
    # Compare models if we have multiple results
    if len(results) > 1:
        print("📈 Comparing Forecasting Models")
        print("-" * 30)
        
        try:
            comparison = forecaster.compare_forecasting_models(
                periods=6, 
                group_by='product_line',
                test_size=0.2
            )
            
            if 'performance_metrics' in comparison:
                metrics = comparison['performance_metrics']
                print("📊 Model Performance Metrics:")
                print(metrics.groupby('model')[['mae', 'mape', 'rmse']].mean().round(2))
                
                # Get recommendations
                recommendations = forecaster.get_model_recommendations(metrics)
                print("\n💡 Model Recommendations:")
                for key, recommendation in recommendations.items():
                    print(f"   • {recommendation}")
            else:
                print("⚠️  Insufficient data for performance comparison")
                
        except Exception as e:
            print(f"❌ Error comparing models: {str(e)}")
    
    # Generate insights
    if results:
        print("\n🔍 Forecast Insights")
        print("-" * 20)
        
        # Use the first available forecast for insights
        first_forecast = list(results.values())[0]
        insights = forecaster.get_forecast_insights(first_forecast)
        
        for key, insight in insights.items():
            print(f"   • {insight}")
    
    print("\n✅ Enhanced forecasting test completed!")

if __name__ == "__main__":
    test_enhanced_forecasting() 