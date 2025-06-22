#!/usr/bin/env python3
"""
Create a small sample database for Streamlit Cloud deployment testing.
"""

import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_sample_database():
    """Create a small sample database with basic tables."""
    
    # Connect to database (will create if doesn't exist)
    conn = duckdb.connect("sample_portfolio.duckdb")
    
    # Create sample ESG data
    dates = pd.date_range('2023-01-01', periods=12, freq='M')
    esg_data = []
    
    for date in dates:
        for product in ['Product A', 'Product B']:
            esg_data.append({
                'date': date,
                'product_line': product,
                'total_emissions_kg_co2': np.random.randint(800, 1200),
                'avg_recycled_material_pct': np.random.uniform(70, 85),
                'avg_efficiency_rating': np.random.uniform(7.5, 9.0),
                'avg_quality_score': np.random.uniform(8.5, 9.5),
                'avg_waste_reduction_pct': np.random.uniform(15, 25)
            })
    
    esg_df = pd.DataFrame(esg_data)
    conn.execute("CREATE TABLE IF NOT EXISTS fact_esg_monthly AS SELECT * FROM esg_df")
    
    # Create sample financial data
    finance_data = []
    for date in dates:
        for product in ['Product A', 'Product B']:
            revenue = np.random.randint(50000, 150000)
            cost = revenue * np.random.uniform(0.6, 0.8)
            profit = revenue - cost
            
            finance_data.append({
                'date': date,
                'product_line': product,
                'total_revenue': revenue,
                'total_cost': cost,
                'total_profit': profit,
                'total_profit_margin': (profit / revenue) * 100,
                'units_sold': np.random.randint(100, 500)
            })
    
    finance_df = pd.DataFrame(finance_data)
    conn.execute("CREATE TABLE IF NOT EXISTS fact_financial_monthly AS SELECT * FROM finance_df")
    
    # Create sample staging data
    stg_esg_data = esg_df.copy()
    stg_esg_data['transaction_id'] = range(len(stg_esg_data))
    conn.execute("CREATE TABLE IF NOT EXISTS stg_esg_data AS SELECT * FROM stg_esg_data")
    
    stg_sales_data = finance_df.copy()
    stg_sales_data['transaction_id'] = range(len(stg_sales_data))
    conn.execute("CREATE TABLE IF NOT EXISTS stg_sales_data AS SELECT * FROM stg_sales_data")
    
    # Create mart table
    mart_data = [{
        'metric': 'Total Emissions',
        'value': esg_df['total_emissions_kg_co2'].sum(),
        'unit': 'kg CO2'
    }, {
        'metric': 'Total Revenue',
        'value': finance_df['total_revenue'].sum(),
        'unit': 'USD'
    }]
    
    mart_df = pd.DataFrame(mart_data)
    conn.execute("CREATE TABLE IF NOT EXISTS mart_esg_summary AS SELECT * FROM mart_df")
    
    # Show table info
    tables = conn.execute("SHOW TABLES").fetchdf()
    print(f"Created {len(tables)} tables:")
    
    for table in tables['name']:
        count = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchdf()
        print(f"- {table}: {count['count'].iloc[0]} rows")
    
    conn.close()
    
    # Check file size
    import os
    size_mb = os.path.getsize("sample_portfolio.duckdb") / (1024 * 1024)
    print(f"\nSample database size: {size_mb:.2f} MB")
    
    return "sample_portfolio.duckdb"

if __name__ == "__main__":
    print("Creating sample database...")
    db_path = create_sample_database()
    print(f"✅ Sample database created: {db_path}") 