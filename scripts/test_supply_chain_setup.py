#!/usr/bin/env python3
"""
Test script for supply chain setup and dbt models.
"""

import os
import sys
import subprocess
import pandas as pd
import duckdb
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ecometrics.data_connector import load_supply_chain_data


def run_dbt_command(command, cwd=None):
    """Run a dbt command and return the result."""
    if cwd is None:
        cwd = project_root / "dbt"
    
    print(f"Running: dbt {command}")
    print(f"Working directory: {cwd}")
    
    try:
        result = subprocess.run(
            ["dbt", *command.split()],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Command completed successfully")
        print(f"Output:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        return False


def test_supply_chain_models():
    """Test the supply chain dbt models."""
    print("\n" + "="*60)
    print("TESTING SUPPLY CHAIN DBT MODELS")
    print("="*60)
    
    # Check if we're in the right directory
    dbt_dir = project_root / "dbt"
    if not (dbt_dir / "dbt_project.yml").exists():
        print(f"❌ dbt_project.yml not found in {dbt_dir}")
        return False
    
    # Run dbt deps to install dependencies
    print("\n1. Installing dbt dependencies...")
    if not run_dbt_command("deps"):
        return False
    
    # Run dbt run for supply chain models
    print("\n2. Running supply chain models...")
    if not run_dbt_command("run --select supply_chain"):
        return False
    
    # Run dbt test for supply chain models
    print("\n3. Testing supply chain models...")
    if not run_dbt_command("test --select supply_chain"):
        return False
    
    # Run dbt docs generate
    print("\n4. Generating documentation...")
    if not run_dbt_command("docs generate"):
        return False
    
    return True


def test_data_connector():
    """Test the data connector with supply chain data."""
    print("\n" + "="*60)
    print("TESTING DATA CONNECTOR")
    print("="*60)
    
    try:
        # Test loading supply chain data
        print("Loading supply chain data...")
        df, status = load_supply_chain_data()
        
        if df.empty:
            print(f"❌ No data loaded: {status}")
            return False
        
        print(f"✅ Data loaded successfully: {status}")
        print(f"   - Rows: {len(df):,}")
        print(f"   - Columns: {len(df.columns)}")
        print(f"   - Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"   - Suppliers: {df['supplier'].nunique()}")
        
        # Check for required columns
        required_columns = [
            'date', 'supplier', 'order_id', 'order_quantity', 'order_value',
            'expected_delivery', 'actual_delivery', 'on_time_delivery',
            'quality_issues', 'defect_quantity', 'supplier_reliability',
            'sustainability_rating'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return False
        
        print("✅ All required columns present")
        
        # Check data quality
        print("\nData Quality Check:")
        print(f"   - Null values in date: {df['date'].isnull().sum()}")
        print(f"   - Null values in supplier: {df['supplier'].isnull().sum()}")
        print(f"   - Null values in order_value: {df['order_value'].isnull().sum()}")
        print(f"   - Negative order values: {(df['order_value'] < 0).sum()}")
        print(f"   - Zero order quantities: {(df['order_quantity'] == 0).sum()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing data connector: {e}")
        return False


def test_supply_chain_analysis():
    """Test the supply chain analysis module."""
    print("\n" + "="*60)
    print("TESTING SUPPLY CHAIN ANALYSIS")
    print("="*60)
    
    try:
        from src.packagingco_insights.analysis.supply_chain_analysis import (
            SupplyChainAnalyzer, analyze_supply_chain_data, generate_supply_chain_report
        )
        
        # Load test data
        df, status = load_supply_chain_data()
        if df.empty:
            print(f"❌ No data available for analysis: {status}")
            return False
        
        print(f"✅ Loaded {len(df):,} records for analysis")
        
        # Test analyzer initialization
        print("\n1. Testing analyzer initialization...")
        analyzer = SupplyChainAnalyzer(df)
        print("✅ Analyzer initialized successfully")
        
        # Test supplier performance summary
        print("\n2. Testing supplier performance summary...")
        summary = analyzer.get_supplier_performance_summary()
        print(f"✅ Generated summary for {len(summary)} suppliers")
        
        # Test delivery analysis
        print("\n3. Testing delivery analysis...")
        delivery_analysis = analyzer.get_delivery_performance_analysis()
        print(f"✅ Delivery analysis completed")
        print(f"   - Overall on-time rate: {delivery_analysis['overall_on_time_rate']:.1f}%")
        
        # Test quality analysis
        print("\n4. Testing quality analysis...")
        quality_analysis = analyzer.get_quality_control_analysis()
        print(f"✅ Quality analysis completed")
        print(f"   - Average defect rate: {quality_analysis['overall_quality_metrics']['avg_defect_rate']:.2f}%")
        
        # Test sustainability analysis
        print("\n5. Testing sustainability analysis...")
        sustainability_analysis = analyzer.get_sustainability_analysis()
        print(f"✅ Sustainability analysis completed")
        print(f"   - Average sustainability rating: {sustainability_analysis['overall_sustainability_metrics']['avg_sustainability_rating']:.2f}")
        
        # Test cost analysis
        print("\n6. Testing cost analysis...")
        cost_analysis = analyzer.get_cost_analysis()
        print(f"✅ Cost analysis completed")
        print(f"   - Average unit cost: ${cost_analysis['overall_cost_metrics']['avg_unit_cost']:.2f}")
        
        # Test risk assessment
        print("\n7. Testing risk assessment...")
        risk_assessment = analyzer.get_supplier_risk_assessment()
        print(f"✅ Risk assessment completed")
        print(f"   - Risk scores range: {risk_assessment['overall_risk_score'].min():.1f} - {risk_assessment['overall_risk_score'].max():.1f}")
        
        # Test key insights
        print("\n8. Testing key insights...")
        insights = analyzer.get_key_insights()
        print(f"✅ Generated {len(insights)} key insights")
        
        # Test recommendations
        print("\n9. Testing recommendations...")
        recommendations = analyzer.get_recommendations()
        print(f"✅ Generated {len(recommendations)} recommendations")
        
        # Test comprehensive analysis
        print("\n10. Testing comprehensive analysis...")
        analysis = analyze_supply_chain_data(df)
        print("✅ Comprehensive analysis completed")
        
        # Test report generation
        print("\n11. Testing report generation...")
        report = generate_supply_chain_report(df)
        print(f"✅ Generated report ({len(report)} characters)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing supply chain analysis: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_database_tables():
    """Check what tables are available in the database."""
    print("\n" + "="*60)
    print("CHECKING DATABASE TABLES")
    print("="*60)
    
    try:
        # Try to connect to the database
        db_paths = [
            "ecometrics/portfolio.duckdb",
            "portfolio.duckdb",
            "data/processed/portfolio.duckdb"
        ]
        
        db_path = None
        for path in db_paths:
            if os.path.exists(path):
                db_path = path
                break
        
        if db_path is None:
            print("❌ No database file found")
            return False
        
        print(f"✅ Found database at: {db_path}")
        
        # Connect and check tables
        conn = duckdb.connect(db_path)
        
        # Get list of tables
        tables = conn.execute("SHOW TABLES").fetchdf()
        print(f"\nAvailable tables ({len(tables)}):")
        for table in tables['name']:
            # Get row count
            count = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchdf()
            print(f"   - {table}: {count['count'].iloc[0]:,} rows")
        
        # Check for supply chain specific tables
        supply_chain_tables = [t for t in tables['name'] if 'supply' in t.lower() or 'chain' in t.lower()]
        print(f"\nSupply chain related tables ({len(supply_chain_tables)}):")
        for table in supply_chain_tables:
            count = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchdf()
            print(f"   - {table}: {count['count'].iloc[0]:,} rows")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking database tables: {e}")
        return False


def main():
    """Main test function."""
    print("SUPPLY CHAIN SETUP TEST")
    print("="*60)
    
    # Check database tables first
    check_database_tables()
    
    # Test dbt models
    dbt_success = test_supply_chain_models()
    
    # Test data connector
    connector_success = test_data_connector()
    
    # Test analysis module
    analysis_success = test_supply_chain_analysis()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"dbt Models: {'✅ PASS' if dbt_success else '❌ FAIL'}")
    print(f"Data Connector: {'✅ PASS' if connector_success else '❌ FAIL'}")
    print(f"Analysis Module: {'✅ PASS' if analysis_success else '❌ FAIL'}")
    
    overall_success = dbt_success and connector_success and analysis_success
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Supply chain setup is ready!")
        print("\nNext steps:")
        print("1. Run 'dbt run --select supply_chain' to build models")
        print("2. Run 'dbt test --select supply_chain' to validate data")
        print("3. Start the Streamlit app to view supply chain insights")
    else:
        print("\n⚠️  Please fix the failing tests before proceeding")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 