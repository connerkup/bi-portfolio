#!/usr/bin/env python3
"""
Comprehensive Sanity Check Script for BI Portfolio Calculations

This script performs common sense checks on our calculated values to ensure:
1. ESG metrics are within reasonable ranges
2. Financial calculations are mathematically correct
3. Sustainability scores make business sense
4. Growth rates and trends are logical
5. Material percentages add up correctly
6. Efficiency metrics are reasonable

Usage: python debug_forecast.py
"""

import pandas as pd
import numpy as np
import duckdb
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def connect_to_database():
    """Connect to the DuckDB database."""
    try:
        # Connect to the database file
        db_path = "data/processed/portfolio.duckdb"
        if not os.path.exists(db_path):
            print(f"❌ Database file not found: {db_path}")
            print("Please run 'dbt run' first to create the database.")
            return None
        
        conn = duckdb.connect(db_path)
        print(f"✅ Connected to database: {db_path}")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def check_esg_data_sanity(conn):
    """Check ESG data for common sense values."""
    print("\n" + "="*60)
    print("🌱 ESG DATA SANITY CHECKS")
    print("="*60)
    
    # Get ESG fact table data
    esg_query = """
    SELECT 
        date,
        product_line,
        facility,
        total_emissions_kg_co2,
        total_energy_consumption_kwh,
        total_water_usage_liters,
        total_waste_generated_kg,
        avg_recycled_material_pct,
        avg_virgin_material_pct,
        avg_renewable_energy_pct,
        avg_efficiency_rating,
        avg_quality_score,
        sustainability_score,
        total_batches,
        overall_emissions_per_unit,
        overall_energy_per_unit,
        overall_water_per_unit,
        overall_waste_per_unit
    FROM fact_esg_monthly
    ORDER BY date DESC
    LIMIT 50
    """
    
    esg_data = conn.execute(esg_query).fetchdf()
    
    if esg_data.empty:
        print("❌ No ESG data found!")
        return
    
    print(f"📊 Analyzing {len(esg_data)} ESG records...")
    
    # 1. Check material percentages add up to ~100%
    print("\n1️⃣ MATERIAL PERCENTAGE CHECKS:")
    esg_data['material_sum'] = esg_data['avg_recycled_material_pct'] + esg_data['avg_virgin_material_pct']
    
    material_issues = esg_data[
        (esg_data['material_sum'] < 95) | (esg_data['material_sum'] > 105)
    ]
    
    if not material_issues.empty:
        print(f"⚠️  Found {len(material_issues)} records where material percentages don't add up to ~100%:")
        print(material_issues[['date', 'product_line', 'facility', 'avg_recycled_material_pct', 'avg_virgin_material_pct', 'material_sum']].head())
    else:
        print("✅ Material percentages add up correctly (95-105% range)")
    
    # 2. Check sustainability score ranges
    print("\n2️⃣ SUSTAINABILITY SCORE CHECKS:")
    print(f"   Min score: {esg_data['sustainability_score'].min():.2f}")
    print(f"   Max score: {esg_data['sustainability_score'].max():.2f}")
    print(f"   Mean score: {esg_data['sustainability_score'].mean():.2f}")
    
    if esg_data['sustainability_score'].min() < 0 or esg_data['sustainability_score'].max() > 100:
        print("❌ Sustainability scores outside expected 0-100 range!")
    else:
        print("✅ Sustainability scores within expected 0-100 range")
    
    # 3. Check efficiency and quality scores
    print("\n3️⃣ EFFICIENCY & QUALITY CHECKS:")
    print(f"   Efficiency rating - Min: {esg_data['avg_efficiency_rating'].min():.3f}, Max: {esg_data['avg_efficiency_rating'].max():.3f}")
    print(f"   Quality score - Min: {esg_data['avg_quality_score'].min():.3f}, Max: {esg_data['avg_quality_score'].max():.3f}")
    
    if (esg_data['avg_efficiency_rating'].min() < 0 or esg_data['avg_efficiency_rating'].max() > 1 or
        esg_data['avg_quality_score'].min() < 0 or esg_data['avg_quality_score'].max() > 1):
        print("❌ Efficiency or quality scores outside expected 0-1 range!")
    else:
        print("✅ Efficiency and quality scores within expected 0-1 range")
    
    # 4. Check per-unit metrics for reasonableness
    print("\n4️⃣ PER-UNIT METRICS CHECKS:")
    print(f"   Emissions per unit - Min: {esg_data['overall_emissions_per_unit'].min():.6f}, Max: {esg_data['overall_emissions_per_unit'].max():.6f}")
    print(f"   Energy per unit - Min: {esg_data['overall_energy_per_unit'].min():.6f}, Max: {esg_data['overall_energy_per_unit'].max():.6f}")
    print(f"   Water per unit - Min: {esg_data['overall_water_per_unit'].min():.6f}, Max: {esg_data['overall_water_per_unit'].max():.6f}")
    
    # Check for extreme outliers
    emissions_outliers = esg_data[esg_data['overall_emissions_per_unit'] > 10]
    if not emissions_outliers.empty:
        print(f"⚠️  Found {len(emissions_outliers)} records with unusually high emissions per unit")
    
    # 5. Check renewable energy percentages
    print("\n5️⃣ RENEWABLE ENERGY CHECKS:")
    print(f"   Renewable energy % - Min: {esg_data['avg_renewable_energy_pct'].min():.2f}%, Max: {esg_data['avg_renewable_energy_pct'].max():.2f}%")
    
    if esg_data['avg_renewable_energy_pct'].max() > 100:
        print("❌ Renewable energy percentage exceeds 100%!")
    else:
        print("✅ Renewable energy percentages within expected range")
    
    # 6. Check batch counts
    print("\n6️⃣ BATCH COUNT CHECKS:")
    print(f"   Total batches - Min: {esg_data['total_batches'].min()}, Max: {esg_data['total_batches'].max()}")
    
    zero_batches = esg_data[esg_data['total_batches'] == 0]
    if not zero_batches.empty:
        print(f"⚠️  Found {len(zero_batches)} records with zero batches")
    
    return esg_data

def check_financial_data_sanity(conn):
    """Check financial data for common sense values."""
    print("\n" + "="*60)
    print("💰 FINANCIAL DATA SANITY CHECKS")
    print("="*60)
    
    # Get financial fact table data
    finance_query = """
    SELECT 
        date,
        product_line,
        region,
        total_revenue,
        total_cost_of_goods,
        total_operating_cost,
        total_profit_margin,
        total_units_sold,
        avg_unit_price,
        avg_unit_cost,
        overall_profit_margin_pct
    FROM fact_financial_monthly
    ORDER BY date DESC
    LIMIT 50
    """
    
    try:
        finance_data = conn.execute(finance_query).fetchdf()
    except Exception as e:
        print(f"❌ Error querying financial data: {e}")
        print("   This might be expected if financial models haven't been built yet.")
        return None
    
    if finance_data.empty:
        print("❌ No financial data found!")
        return None
    
    print(f"📊 Analyzing {len(finance_data)} financial records...")
    
    # 1. Check profit margin calculations
    print("\n1️⃣ PROFIT MARGIN CHECKS:")
    
    # Calculate both gross and net profit margins
    finance_data['calculated_gross_margin'] = (
        (finance_data['total_revenue'] - finance_data['total_cost_of_goods']) / 
        finance_data['total_revenue'] * 100
    )
    
    finance_data['calculated_net_margin'] = (
        finance_data['total_profit_margin'] / 
        finance_data['total_revenue'] * 100
    )
    
    # Check gross margin consistency (should match dbt if dbt uses gross margin)
    gross_margin_issues = finance_data[
        abs(finance_data['calculated_gross_margin'] - finance_data['overall_profit_margin_pct']) > 0.01
    ]
    
    if not gross_margin_issues.empty:
        print(f"⚠️  Found {len(gross_margin_issues)} records with gross margin discrepancies:")
        print(gross_margin_issues[['date', 'product_line', 'overall_profit_margin_pct', 'calculated_gross_margin']].head())
    else:
        print("✅ Gross profit margin calculations are consistent")
    
    # Display margin ranges for business sense check
    print(f"\n   📊 MARGIN RANGES:")
    print(f"   Gross Margin - Min: {finance_data['calculated_gross_margin'].min():.2f}%, Max: {finance_data['calculated_gross_margin'].max():.2f}%")
    print(f"   Net Margin - Min: {finance_data['calculated_net_margin'].min():.2f}%, Max: {finance_data['calculated_net_margin'].max():.2f}%")
    print(f"   DBT Overall Margin - Min: {finance_data['overall_profit_margin_pct'].min():.2f}%, Max: {finance_data['overall_profit_margin_pct'].max():.2f}%")
    
    # Check for reasonable margin ranges
    if (finance_data['calculated_gross_margin'].min() < -50 or 
        finance_data['calculated_gross_margin'].max() > 100):
        print("⚠️  Gross margins outside expected range (-50% to 100%)")
    else:
        print("✅ Gross margins within reasonable range")
        
    if (finance_data['calculated_net_margin'].min() < -50 or 
        finance_data['calculated_net_margin'].max() > 100):
        print("⚠️  Net margins outside expected range (-50% to 100%)")
    else:
        print("✅ Net margins within reasonable range")
    
    # 2. Check revenue and cost relationships
    print("\n2️⃣ REVENUE & COST CHECKS:")
    negative_profit = finance_data[finance_data['total_profit_margin'] < 0]
    if not negative_profit.empty:
        print(f"⚠️  Found {len(negative_profit)} records with negative profit margins")
    
    cost_greater_than_revenue = finance_data[
        finance_data['total_cost_of_goods'] > finance_data['total_revenue']
    ]
    if not cost_greater_than_revenue.empty:
        print(f"⚠️  Found {len(cost_greater_than_revenue)} records where cost of goods exceeds revenue")
    
    # 3. Check unit price and cost relationships
    print("\n3️⃣ UNIT PRICE & COST CHECKS:")
    print(f"   Unit price - Min: ${finance_data['avg_unit_price'].min():.2f}, Max: ${finance_data['avg_unit_price'].max():.2f}")
    print(f"   Unit cost - Min: ${finance_data['avg_unit_cost'].min():.2f}, Max: ${finance_data['avg_unit_cost'].max():.2f}")
    
    negative_unit_profit = finance_data[
        finance_data['avg_unit_price'] < finance_data['avg_unit_cost']
    ]
    if not negative_unit_profit.empty:
        print(f"⚠️  Found {len(negative_unit_profit)} records where unit cost exceeds unit price")
    
    # 4. Check for zero or negative values
    print("\n4️⃣ ZERO/NEGATIVE VALUE CHECKS:")
    zero_revenue = finance_data[finance_data['total_revenue'] == 0]
    zero_units = finance_data[finance_data['total_units_sold'] == 0]
    
    if not zero_revenue.empty:
        print(f"⚠️  Found {len(zero_revenue)} records with zero revenue")
    if not zero_units.empty:
        print(f"⚠️  Found {len(zero_units)} records with zero units sold")
    
    return finance_data

def check_calculation_consistency(conn):
    """Check for consistency between different calculation methods."""
    print("\n" + "="*60)
    print("🔍 CALCULATION CONSISTENCY CHECKS")
    print("="*60)
    
    # Check if revenue calculations match between different approaches
    consistency_query = """
    SELECT 
        date,
        product_line,
        total_revenue,
        total_units_sold,
        avg_unit_price,
        calculated_revenue = total_units_sold * avg_unit_price,
        revenue_diff = abs(total_revenue - (total_units_sold * avg_unit_price))
    FROM fact_financial_monthly
    WHERE total_units_sold > 0 AND avg_unit_price > 0
    ORDER BY revenue_diff DESC
    LIMIT 10
    """
    
    try:
        consistency_data = conn.execute(consistency_query).fetchdf()
        if not consistency_data.empty:
            print("📊 Revenue calculation consistency check:")
            print(consistency_data[['date', 'product_line', 'total_revenue', 'calculated_revenue', 'revenue_diff']].head())
            
            large_diffs = consistency_data[consistency_data['revenue_diff'] > 1.0]
            if not large_diffs.empty:
                print(f"⚠️  Found {len(large_diffs)} records with revenue calculation differences > $1.00")
            else:
                print("✅ Revenue calculations are consistent")
    except Exception as e:
        print(f"⚠️  Could not perform revenue consistency check: {e}")

def check_data_distributions(conn):
    """Check data distributions for anomalies."""
    print("\n" + "="*60)
    print("📈 DATA DISTRIBUTION CHECKS")
    print("="*60)
    
    # ESG data distribution
    esg_dist_query = """
    SELECT 
        product_line,
        COUNT(*) as record_count,
        AVG(sustainability_score) as avg_sustainability,
        STDDEV(sustainability_score) as std_sustainability,
        MIN(sustainability_score) as min_sustainability,
        MAX(sustainability_score) as max_sustainability,
        AVG(avg_recycled_material_pct) as avg_recycled,
        AVG(avg_renewable_energy_pct) as avg_renewable
    FROM fact_esg_monthly
    GROUP BY product_line
    ORDER BY avg_sustainability DESC
    """
    
    try:
        esg_dist = conn.execute(esg_dist_query).fetchdf()
        print("🌱 ESG Data Distribution by Product Line:")
        print(esg_dist.to_string(index=False))
        
        # Check for unusual patterns
        low_sustainability = esg_dist[esg_dist['avg_sustainability'] < 30]
        if not low_sustainability.empty:
            print(f"⚠️  Product lines with low average sustainability scores: {list(low_sustainability['product_line'])}")
            
    except Exception as e:
        print(f"⚠️  Could not analyze ESG distributions: {e}")

def check_streamlit_calculations():
    """Check if Streamlit calculations would work with our data."""
    print("\n" + "="*60)
    print("🎯 STREAMLIT CALCULATION CHECKS")
    print("="*60)
    
    try:
        # Test importing the analysis modules
        from packagingco_insights.analysis import ESGAnalyzer, FinanceAnalyzer
        from packagingco_insights.utils import load_esg_data, load_finance_data
        
        print("✅ Successfully imported analysis modules")
        
        # Test data loading functions
        try:
            esg_data = load_esg_data()
            print(f"✅ ESG data loaded: {len(esg_data)} records")
            
            # Test ESG analyzer
            esg_analyzer = ESGAnalyzer(esg_data)
            print("✅ ESG analyzer initialized successfully")
            
            # Test some calculations
            emissions_trends = esg_analyzer.calculate_emissions_trends()
            print(f"✅ Emissions trends calculated: {len(emissions_trends)} records")
            
            esg_scores = esg_analyzer.calculate_esg_score()
            print(f"✅ ESG scores calculated: {len(esg_scores)} records")
            
        except Exception as e:
            print(f"❌ Error testing ESG calculations: {e}")
        
        try:
            finance_data = load_finance_data()
            print(f"✅ Finance data loaded: {len(finance_data)} records")
            
            # Test finance analyzer
            finance_analyzer = FinanceAnalyzer(finance_data)
            print("✅ Finance analyzer initialized successfully")
            
            # Test some calculations
            revenue_trends = finance_analyzer.calculate_revenue_trends()
            print(f"✅ Revenue trends calculated: {len(revenue_trends)} records")
            
            profitability = finance_analyzer.calculate_profitability_metrics()
            print(f"✅ Profitability metrics calculated: {len(profitability)} records")
            
        except Exception as e:
            print(f"❌ Error testing finance calculations: {e}")
            
    except ImportError as e:
        print(f"❌ Error importing analysis modules: {e}")

def main():
    """Run all sanity checks."""
    print("🔍 BI PORTFOLIO SANITY CHECK REPORT")
    print("="*60)
    print("This script performs comprehensive checks on our calculated values")
    print("to ensure they make business sense and are mathematically correct.")
    print("="*60)
    
    # Connect to database
    conn = connect_to_database()
    if conn is None:
        return
    
    try:
        # Run all checks
        esg_data = check_esg_data_sanity(conn)
        finance_data = check_financial_data_sanity(conn)
        check_calculation_consistency(conn)
        check_data_distributions(conn)
        check_streamlit_calculations()
        
        print("\n" + "="*60)
        print("✅ SANITY CHECK COMPLETE")
        print("="*60)
        print("All checks have been performed. Review any warnings above.")
        print("If you see any ❌ errors or ⚠️ warnings, investigate further.")
        
    finally:
        conn.close()
        print("\n🔌 Database connection closed.")

if __name__ == "__main__":
    main() 