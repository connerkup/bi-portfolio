#!/usr/bin/env python3
"""
Script to prepare the EcoMetrics app for Streamlit Cloud deployment.
This script builds the dbt pipeline and copies the database file to the ecometrics directory.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    if cwd:
        print(f"Working directory: {cwd}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        print(f"✅ Command completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_dbt_installation():
    """Check if dbt is installed."""
    try:
        result = subprocess.run(
            ["dbt", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print("✅ dbt is installed")
            return True
        else:
            print("❌ dbt is not installed")
            return False
    except FileNotFoundError:
        print("❌ dbt is not installed")
        return False


def build_dbt_pipeline():
    """Build the dbt pipeline."""
    print("\n🔨 Building dbt pipeline...")
    
    # Check if dbt directory exists
    dbt_dir = Path("../dbt")
    if not dbt_dir.exists():
        print(f"❌ dbt directory not found: {dbt_dir}")
        return False
    
    # Install dbt dependencies
    print("Installing dbt dependencies...")
    run_command("dbt deps", cwd=dbt_dir)
    
    # Run dbt models
    print("Running dbt models...")
    run_command("dbt run", cwd=dbt_dir)
    
    # Test dbt models
    print("Testing dbt models...")
    run_command("dbt test", cwd=dbt_dir, check=False)
    
    return True


def copy_database_file():
    """Copy the database file to the ecometrics directory."""
    print("\n📁 Copying database file...")
    
    # Source database path
    source_db = Path("../data/processed/portfolio.duckdb")
    
    # Destination database path
    dest_db = Path("portfolio.duckdb")
    
    if not source_db.exists():
        print(f"❌ Source database not found: {source_db}")
        print("Please run 'dbt run' first to build the database.")
        return False
    
    try:
        # Copy the database file
        shutil.copy2(source_db, dest_db)
        print(f"✅ Database copied to: {dest_db}")
        
        # Check file size
        size_mb = dest_db.stat().st_size / (1024 * 1024)
        print(f"📊 Database size: {size_mb:.2f} MB")
        
        return True
    except Exception as e:
        print(f"❌ Failed to copy database: {e}")
        return False


def check_database_content():
    """Check the content of the copied database."""
    print("\n🔍 Checking database content...")
    
    try:
        import duckdb
        
        # Connect to the database
        conn = duckdb.connect("portfolio.duckdb")
        
        # Get list of tables
        tables = conn.execute("SHOW TABLES").fetchdf()
        
        print(f"✅ Database contains {len(tables)} tables:")
        for table in tables['name']:
            # Get row count for each table
            count = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchdf()
            print(f"  - {table}: {count['count'].iloc[0]:,} rows")
        
        conn.close()
        return True
        
    except ImportError:
        print("❌ duckdb not installed, skipping content check")
        return False
    except Exception as e:
        print(f"❌ Failed to check database content: {e}")
        return False


def create_deployment_info():
    """Create deployment information file."""
    print("\n📝 Creating deployment information...")
    
    info_content = f"""# Deployment Information

Generated on: {os.popen('date').read().strip()}

## Database Information
- File: portfolio.duckdb
- Size: {Path('portfolio.duckdb').stat().st_size / (1024 * 1024):.2f} MB
- Location: ecometrics/portfolio.duckdb

## dbt Models
This database contains the following dbt models:
"""
    
    try:
        import duckdb
        conn = duckdb.connect("portfolio.duckdb")
        tables = conn.execute("SHOW TABLES").fetchdf()
        
        for table in tables['name']:
            count = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchdf()
            info_content += f"- {table}: {count['count'].iloc[0]:,} rows\n"
        
        conn.close()
    except:
        info_content += "- Unable to read table information\n"
    
    info_content += """
## Deployment Steps
1. Commit this database file to your repository
2. Deploy to Streamlit Cloud using ecometrics/Home.py as the main file
3. Verify connection in the Data Browser page

## Notes
- This database file should be included in version control for Streamlit Cloud deployment
- The file will be automatically detected by the data connector
- For production, consider using an external database
"""
    
    with open("DEPLOYMENT_INFO.md", "w") as f:
        f.write(info_content)
    
    print("✅ Deployment information created: DEPLOYMENT_INFO.md")


def main():
    """Main function to prepare for deployment."""
    print("🚀 Preparing EcoMetrics for Streamlit Cloud deployment...")
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Check if we're in the ecometrics directory
    if not (current_dir / "Home.py").exists():
        print("❌ Please run this script from the ecometrics directory")
        sys.exit(1)
    
    # Check dbt installation
    if not check_dbt_installation():
        print("\n💡 To install dbt, run:")
        print("pip install dbt-core dbt-duckdb")
        sys.exit(1)
    
    # Build dbt pipeline
    if not build_dbt_pipeline():
        print("❌ Failed to build dbt pipeline")
        sys.exit(1)
    
    # Copy database file
    if not copy_database_file():
        print("❌ Failed to copy database file")
        sys.exit(1)
    
    # Check database content
    check_database_content()
    
    # Create deployment info
    create_deployment_info()
    
    print("\n🎉 Deployment preparation completed!")
    print("\nNext steps:")
    print("1. git add portfolio.duckdb")
    print("2. git commit -m 'Add dbt database for deployment'")
    print("3. git push")
    print("4. Deploy to Streamlit Cloud using ecometrics/Home.py as main file")


if __name__ == "__main__":
    main() 