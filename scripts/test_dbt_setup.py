#!/usr/bin/env python3
"""
Test dbt Setup Script

This script validates the dbt project setup, runs tests, and provides feedback
on the current state of the data pipeline.
"""

import subprocess
import sys
import os
from pathlib import Path
import pandas as pd
import duckdb


def run_command(command, description, cwd=None):
    """Run a command and return success status."""
    print(f"\n🔄 {description}...")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(
            command.split(),
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"   ✅ Success")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed")
        print(f"   Error: {e.stderr.strip()}")
        return False


def check_dbt_installation():
    """Check if dbt is properly installed."""
    print("\n🔍 Checking dbt installation...")
    
    try:
        result = subprocess.run(
            ["dbt", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"   ✅ dbt version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ❌ dbt not found or not properly installed")
        print("   Please install dbt with: pip install dbt-duckdb")
        return False


def check_project_structure():
    """Check if dbt project structure is correct."""
    print("\n🔍 Checking dbt project structure...")
    
    required_files = [
        "dbt/dbt_project.yml",
        "dbt/profiles.yml",
        "dbt/models/sustainability/stg_esg_data.sql",
        "dbt/models/finance/stg_sales_data.sql",
        "dbt/models/sustainability/fact_esg_monthly.sql",
        "dbt/models/finance/fact_financial_monthly.sql",
        "dbt/seeds/sample_sales_data.csv",
        "dbt/seeds/sample_esg_data.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"   ✅ {file_path}")
    
    if missing_files:
        print("   ❌ Missing files:")
        for file_path in missing_files:
            print(f"      - {file_path}")
        return False
    
    return True


def run_dbt_operations():
    """Run dbt operations and validate results."""
    print("\n🚀 Running dbt operations...")
    
    # Change to dbt directory
    os.chdir("dbt")
    
    # Run dbt deps
    if not run_command("dbt deps", "Installing dbt dependencies"):
        return False
    
    # Run dbt seed
    if not run_command("dbt seed", "Loading seed data"):
        return False
    
    # Run dbt models
    if not run_command("dbt run", "Running dbt models"):
        return False
    
    # Run dbt tests
    if not run_command("dbt test", "Running dbt tests"):
        return False
    
    # Generate documentation
    if not run_command("dbt docs generate", "Generating documentation"):
        return False
    
    # Change back to root directory
    os.chdir("..")
    
    return True


def validate_data_quality():
    """Validate data quality using DuckDB."""
    print("\n🔍 Validating data quality...")
    
    try:
        # Connect to DuckDB
        con = duckdb.connect("data/processed/portfolio.duckdb")
        
        # Check if tables exist
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'main'
        ORDER BY table_name
        """
        tables = con.execute(tables_query).fetchall()
        
        print("   📊 Available tables:")
        for table in tables:
            print(f"      - {table[0]}")
        
        # Check row counts
        print("\n   📈 Row counts:")
        for table in tables:
            table_name = table[0]
            count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"      - {table_name}: {count:,} rows")
        
        # Check for data quality issues
        print("\n   🔍 Data quality checks:")
        
        # Check for null values in key columns
        null_checks = [
            ("sample_sales_data", "date"),
            ("sample_sales_data", "product_line"),
            ("sample_esg_data", "date"),
            ("sample_esg_data", "product_line")
        ]
        
        for table, column in null_checks:
            try:
                null_count = con.execute(
                    f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL"
                ).fetchone()[0]
                if null_count == 0:
                    print(f"      ✅ {table}.{column}: No null values")
                else:
                    print(f"      ⚠️  {table}.{column}: {null_count} null values")
            except:
                print(f"      ❌ {table}.{column}: Column not found")
        
        # Check for negative values in numeric columns
        negative_checks = [
            ("sample_sales_data", "revenue"),
            ("sample_sales_data", "units_sold"),
            ("sample_esg_data", "emissions_kg_co2"),
            ("sample_esg_data", "energy_consumption_kwh")
        ]
        
        for table, column in negative_checks:
            try:
                negative_count = con.execute(
                    f"SELECT COUNT(*) FROM {table} WHERE {column} < 0"
                ).fetchone()[0]
                if negative_count == 0:
                    print(f"      ✅ {table}.{column}: No negative values")
                else:
                    print(f"      ⚠️  {table}.{column}: {negative_count} negative values")
            except:
                print(f"      ❌ {table}.{column}: Column not found")
        
        # Check date ranges
        print("\n   📅 Date ranges:")
        for table in ["sample_sales_data", "sample_esg_data"]:
            try:
                date_range = con.execute(f"""
                    SELECT 
                        MIN(date) as min_date,
                        MAX(date) as max_date,
                        COUNT(DISTINCT date) as unique_dates
                    FROM {table}
                """).fetchone()
                print(f"      - {table}: {date_range[0]} to {date_range[1]} ({date_range[2]} months)")
            except:
                print(f"      ❌ {table}: Could not check date range")
        
        con.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error validating data: {e}")
        return False


def check_model_outputs():
    """Check if dbt models produced expected outputs."""
    print("\n🔍 Checking model outputs...")
    
    try:
        con = duckdb.connect("data/processed/portfolio.duckdb")
        
        # Check staging models
        staging_models = ["stg_sales_data", "stg_esg_data"]
        for model in staging_models:
            try:
                count = con.execute(f"SELECT COUNT(*) FROM {model}").fetchone()[0]
                print(f"   ✅ {model}: {count:,} rows")
            except:
                print(f"   ❌ {model}: Table not found")
        
        # Check fact models
        fact_models = ["fact_financial_monthly", "fact_esg_monthly"]
        for model in fact_models:
            try:
                count = con.execute(f"SELECT COUNT(*) FROM {model}").fetchone()[0]
                print(f"   ✅ {model}: {count:,} rows")
            except:
                print(f"   ❌ {model}: Table not found")
        
        # Check calculated fields
        print("\n   🧮 Checking calculated fields:")
        
        # Check if gross profit calculation is correct
        try:
            validation = con.execute("""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(CASE WHEN gross_profit = revenue - cost_of_goods THEN 1 END) as correct_calculations
                FROM stg_sales_data
            """).fetchone()
            
            if validation[0] == validation[1]:
                print("      ✅ Gross profit calculations are correct")
            else:
                print(f"      ⚠️  Gross profit calculations: {validation[1]}/{validation[0]} correct")
        except:
            print("      ❌ Could not validate gross profit calculations")
        
        # Check if material percentages sum to 100%
        try:
            validation = con.execute("""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(CASE WHEN ABS(recycled_material_pct + virgin_material_pct - 100) <= 1 THEN 1 END) as correct_calculations
                FROM stg_esg_data
            """).fetchone()
            
            if validation[0] == validation[1]:
                print("      ✅ Material percentages sum to 100%")
            else:
                print(f"      ⚠️  Material percentages: {validation[1]}/{validation[0]} correct")
        except:
            print("      ❌ Could not validate material percentages")
        
        con.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking model outputs: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Testing dbt Setup for PackagingCo BI Portfolio")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("dbt"):
        print("❌ dbt directory not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Run all checks
    checks = [
        ("dbt installation", check_dbt_installation),
        ("project structure", check_project_structure),
        ("dbt operations", run_dbt_operations),
        ("data quality", validate_data_quality),
        ("model outputs", check_model_outputs)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"   ❌ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your dbt setup is working correctly.")
        print("\nNext steps:")
        print("1. Run 'dbt docs serve' to view documentation")
        print("2. Start the Streamlit app with 'streamlit run streamlit_app/app.py'")
        print("3. Explore the notebooks in the notebooks/ directory")
    else:
        print(f"\n⚠️  {total - passed} check(s) failed. Please review the errors above.")
        print("\nTroubleshooting tips:")
        print("1. Ensure dbt-duckdb is installed: pip install dbt-duckdb")
        print("2. Check that all required files exist in the dbt/ directory")
        print("3. Verify your DuckDB installation and permissions")
        print("4. Review the dbt logs for detailed error messages")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 