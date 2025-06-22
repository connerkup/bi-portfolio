#!/usr/bin/env python3
"""
Test script to verify the EcoMetrics deployment setup.
This script tests the data connector and verifies that dbt data is accessible.
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from data_connector import DBTDataConnector, check_dbt_availability
    import duckdb
    import pandas as pd
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required dependencies: pip install -r requirements.txt")
    sys.exit(1)


def test_database_connection():
    """Test database connection."""
    print("🔌 Testing database connection...")
    
    connector = DBTDataConnector()
    
    if connector.connect():
        print("✅ Database connection successful")
        print(f"   Database path: {connector.db_path}")
        return True
    else:
        print("❌ Database connection failed")
        print(f"   Database path: {connector.db_path}")
        return False


def test_available_tables():
    """Test getting available tables."""
    print("\n📋 Testing available tables...")
    
    connector = DBTDataConnector()
    
    if not connector.connect():
        print("❌ Cannot test tables - no database connection")
        return False
    
    try:
        tables = connector.get_available_tables()
        
        if tables:
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
            return True
        else:
            print("❌ No tables found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error getting tables: {e}")
        return False
    finally:
        connector.disconnect()


def test_key_models():
    """Test access to key dbt models."""
    print("\n🎯 Testing key dbt models...")
    
    connector = DBTDataConnector()
    
    if not connector.connect():
        print("❌ Cannot test models - no database connection")
        return False
    
    key_models = ['fact_esg_monthly', 'fact_financial_monthly', 'stg_sales_data', 'stg_esg_data']
    available_models = []
    
    try:
        for model in key_models:
            try:
                # Try to get table info
                info = connector.get_table_info(model)
                if info and info.get('row_count', 0) > 0:
                    print(f"✅ {model}: {info['row_count']:,} rows")
                    available_models.append(model)
                else:
                    print(f"❌ {model}: No data or table not found")
            except Exception as e:
                print(f"❌ {model}: Error - {e}")
        
        return len(available_models) > 0
        
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return False
    finally:
        connector.disconnect()


def test_data_loading():
    """Test loading data from models."""
    print("\n📊 Testing data loading...")
    
    connector = DBTDataConnector()
    
    if not connector.connect():
        print("❌ Cannot test data loading - no database connection")
        return False
    
    try:
        # Test ESG data loading
        print("Testing ESG data loading...")
        esg_data, esg_status = connector.load_esg_data()
        if not esg_data.empty:
            print(f"✅ ESG data loaded: {len(esg_data):,} rows - {esg_status}")
        else:
            print(f"❌ ESG data loading failed: {esg_status}")
        
        # Test finance data loading
        print("Testing finance data loading...")
        finance_data, finance_status = connector.load_finance_data()
        if not finance_data.empty:
            print(f"✅ Finance data loaded: {len(finance_data):,} rows - {finance_status}")
        else:
            print(f"❌ Finance data loading failed: {finance_status}")
        
        return not esg_data.empty or not finance_data.empty
        
    except Exception as e:
        print(f"❌ Error testing data loading: {e}")
        return False
    finally:
        connector.disconnect()


def test_data_quality():
    """Test data quality metrics."""
    print("\n🔍 Testing data quality metrics...")
    
    connector = DBTDataConnector()
    
    if not connector.connect():
        print("❌ Cannot test data quality - no database connection")
        return False
    
    try:
        metrics = connector.get_data_quality_metrics()
        
        if metrics:
            print(f"✅ Data quality metrics available for {len(metrics)} tables:")
            for table, table_metrics in metrics.items():
                if 'error' not in table_metrics:
                    print(f"   - {table}: {table_metrics['row_count']:,} rows")
                else:
                    print(f"   - {table}: Error - {table_metrics['error']}")
            return True
        else:
            print("❌ No data quality metrics available")
            return False
            
    except Exception as e:
        print(f"❌ Error testing data quality: {e}")
        return False
    finally:
        connector.disconnect()


def test_availability_check():
    """Test the availability check function."""
    print("\n🔎 Testing availability check...")
    
    try:
        availability = check_dbt_availability()
        
        print(f"Availability: {availability['available']}")
        print(f"Message: {availability['message']}")
        print(f"Database path: {availability['db_path']}")
        
        if availability['available']:
            print("✅ Availability check passed")
            return True
        else:
            print("❌ Availability check failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in availability check: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing EcoMetrics deployment setup...")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Available Tables", test_available_tables),
        ("Key Models", test_key_models),
        ("Data Loading", test_data_loading),
        ("Data Quality", test_data_quality),
        ("Availability Check", test_availability_check),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment setup is ready.")
        return True
    elif passed > 0:
        print("⚠️ Some tests passed. Check the failures above.")
        return False
    else:
        print("❌ All tests failed. Please check your setup.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 