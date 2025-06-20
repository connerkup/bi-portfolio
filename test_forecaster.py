#!/usr/bin/env python3
"""
Test script to verify SalesForecaster methods
"""

import sys
import os
import pandas as pd

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from packagingco_insights.analysis import SalesForecaster

# Create sample data
sample_data = pd.DataFrame({
    'date': pd.date_range('2023-01-01', periods=12, freq='M'),
    'revenue': [1000, 1200, 1100, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100],
    'units_sold': [10, 12, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21],
    'product_line': ['Product A'] * 12
})

# Create forecaster instance
forecaster = SalesForecaster(sample_data)

# Check available methods
print("Available methods in SalesForecaster:")
methods = [method for method in dir(forecaster) if 'forecast' in method.lower()]
for method in methods:
    print(f"  - {method}")

# Test the exponential_smoothing_forecast method
print("\nTesting exponential_smoothing_forecast method:")
try:
    result = forecaster.exponential_smoothing_forecast(periods=3)
    print(f"✅ Method exists and works! Result keys: {list(result.keys())}")
except Exception as e:
    print(f"❌ Error: {e}") 