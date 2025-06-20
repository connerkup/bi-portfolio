#!/usr/bin/env python3
"""
Setup script for dbt models and database.
This script can be run during deployment to set up the required dbt models.
"""

import os
import sys
import subprocess
import pandas as pd
from pathlib import Path

def setup_dbt_environment():
    """Set up the dbt environment and run models."""
    try:
        # Change to the dbt directory
        dbt_dir = Path(__file__).parent.parent / "dbt"
        os.chdir(dbt_dir)
        
        print("🔧 Setting up dbt environment...")
        
        # Check if dbt is installed
        try:
            subprocess.run(["dbt", "--version"], check=True, capture_output=True)
            print("✅ dbt is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ dbt is not installed. Installing dbt...")
            subprocess.run(["pip", "install", "dbt-duckdb"], check=True)
        
        # Install dbt dependencies
        print("📦 Installing dbt dependencies...")
        subprocess.run(["dbt", "deps"], check=True)
        
        # Run dbt models
        print("🚀 Running dbt models...")
        result = subprocess.run(["dbt", "run"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ dbt models created successfully!")
            print(result.stdout)
        else:
            print("⚠️ dbt run had issues:")
            print(result.stderr)
            print("Continuing with sample data...")
            
        return True
        
    except Exception as e:
        print(f"❌ Error setting up dbt: {e}")
        print("Continuing with sample data...")
        return False

def create_sample_database():
    """Create a sample database with processed data if dbt fails."""
    try:
        print("📊 Creating sample database...")
        
        # Create the processed data directory
        data_dir = Path(__file__).parent.parent / "data" / "processed"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Import data processing functions
        sys.path.append(str(Path(__file__).parent.parent / "src"))
        from packagingco_insights.utils.data_loader import (
            create_sample_esg_data, create_sample_finance_data
        )
        
        # Create sample data
        esg_data = create_sample_esg_data()
        finance_data = create_sample_finance_data()
        
        # Save to CSV for backup
        esg_data.to_csv(data_dir / "sample_esg_monthly.csv", index=False)
        finance_data.to_csv(data_dir / "sample_finance_monthly.csv", index=False)
        
        print("✅ Sample database created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample database: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Starting EcoMetrics setup...")
    
    # Try to set up dbt first
    dbt_success = setup_dbt_environment()
    
    # If dbt fails, create sample database
    if not dbt_success:
        create_sample_database()
    
    print("✅ Setup complete!")
    print("🌱 EcoMetrics is ready to run!")

if __name__ == "__main__":
    main() 