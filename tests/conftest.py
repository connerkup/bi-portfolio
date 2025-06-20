"""
Pytest configuration and common fixtures for packagingco_insights tests.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_finance_data():
    """Sample financial data for testing FinanceAnalyzer."""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='ME')
    product_lines = ['Beverage Containers', 'Food Packaging', 'Industrial Packaging']
    regions = ['North America', 'Europe', 'Asia Pacific']
    
    data = []
    for date in dates:
        for product in product_lines:
            for region in regions:
                revenue = np.random.uniform(100000, 500000)
                cog = revenue * np.random.uniform(0.4, 0.7)
                operating_cost = revenue * np.random.uniform(0.1, 0.3)
                profit_margin = revenue - cog - operating_cost
                units_sold = np.random.randint(1000, 10000)
                
                data.append({
                    'date': date,
                    'product_line': product,
                    'region': region,
                    'total_revenue': revenue,
                    'total_cost_of_goods': cog,
                    'total_operating_cost': operating_cost,
                    'total_profit_margin': profit_margin,
                    'total_units_sold': units_sold
                })
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_esg_data():
    """Sample ESG data for testing ESGAnalyzer."""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='ME')
    product_lines = ['Beverage Containers', 'Food Packaging', 'Industrial Packaging']
    facilities = ['Facility A', 'Facility B', 'Facility C']
    
    data = []
    for date in dates:
        for product in product_lines:
            for facility in facilities:
                emissions = np.random.uniform(100, 1000)
                energy = np.random.uniform(5000, 50000)
                recycled_pct = np.random.uniform(20, 80)
                virgin_pct = 100 - recycled_pct
                recycling_rate = np.random.uniform(60, 95)
                waste = np.random.uniform(50, 500)
                
                data.append({
                    'date': date,
                    'product_line': product,
                    'facility': facility,
                    'total_emissions_kg_co2': emissions,
                    'total_energy_consumption_kwh': energy,
                    'avg_recycled_material_pct': recycled_pct,
                    'avg_virgin_material_pct': virgin_pct,
                    'avg_recycling_rate_pct': recycling_rate,
                    'total_waste_generated_kg': waste
                })
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_sales_data():
    """Sample sales data for testing SalesForecaster."""
    dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='ME')
    product_lines = ['Beverage Containers', 'Food Packaging', 'Industrial Packaging']
    
    data = []
    for date in dates:
        for product in product_lines:
            # Create some trend and seasonality
            base_revenue = 100000
            trend = (date.year - 2022) * 50000 + (date.month - 1) * 2000
            seasonal = 20000 * np.sin(2 * np.pi * date.month / 12)
            noise = np.random.normal(0, 10000)
            
            revenue = base_revenue + trend + seasonal + noise
            revenue = max(0, revenue)  # Ensure non-negative
            
            units_sold = int(revenue / np.random.uniform(10, 50))
            
            data.append({
                'date': date,
                'product_line': product,
                'revenue': revenue,
                'units_sold': units_sold
            })
    
    return pd.DataFrame(data)


@pytest.fixture
def empty_dataframe():
    """Empty DataFrame for testing edge cases."""
    return pd.DataFrame()


@pytest.fixture
def invalid_finance_data():
    """DataFrame missing required columns for testing validation."""
    return pd.DataFrame({
        'date': ['2023-01-01'],
        'product_line': ['Test Product'],
        'total_revenue': [100000]
        # Missing required columns
    })


@pytest.fixture
def invalid_esg_data():
    """DataFrame missing required columns for testing validation."""
    return pd.DataFrame({
        'date': ['2023-01-01'],
        'product_line': ['Test Product'],
        'total_emissions_kg_co2': [100]
        # Missing required columns
    }) 