#!/usr/bin/env python3
"""
Setup script for PackagingCo BI Portfolio

This script helps users quickly set up the project environment.
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        # Set encoding for Windows compatibility
        env = os.environ.copy()
        if platform.system() == "Windows":
            env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_platform():
    """Check platform and provide specific guidance."""
    system = platform.system()
    print(f"🖥️  Platform: {system}")
    
    if system == "Windows":
        print("⚠️  Windows detected - some dependencies may have compilation issues")
        print("   Using Windows-compatible requirements file")
        return "windows"
    elif system == "Darwin":
        print("🍎 macOS detected")
        return "macos"
    else:
        print("🐧 Linux detected")
        return "linux"

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        "data/raw",
        "data/processed",
        "logs",
        "docs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def install_dependencies(platform_type):
    """Install Python dependencies based on platform."""
    if platform_type == "windows":
        requirements_file = "requirements-windows.txt"
        if not os.path.exists(requirements_file):
            print(f"❌ {requirements_file} not found, falling back to requirements.txt")
            requirements_file = "requirements.txt"
    else:
        requirements_file = "requirements.txt"
    
    return run_command(f"pip install -r {requirements_file}", f"Installing Python dependencies from {requirements_file}")

def install_package():
    """Install the package in development mode."""
    print("⏭️  Skipping package installation (not required for core functionality)")
    print("   Package can be imported directly from src/ directory")
    return True

def setup_dbt():
    """Set up dbt project."""
    if not os.path.exists("dbt/dbt_project.yml"):
        print("❌ dbt project not found")
        print("   Skipping dbt setup...")
        return True  # Continue with setup
    
    # Change to dbt directory
    os.chdir("dbt")
    
    # Install dbt dependencies
    success = run_command("dbt deps", "Installing dbt dependencies")
    
    # Only continue with dbt operations if deps succeeded
    if success:
        # Run dbt seed
        success &= run_command("dbt seed", "Loading seed data")
        
        # Run dbt models
        success &= run_command("dbt run", "Running dbt models")
        
        # Run dbt tests
        success &= run_command("dbt test", "Running dbt tests")
        
        # Generate documentation
        success &= run_command("dbt docs generate", "Generating dbt documentation")
    else:
        print("⚠️  dbt dependencies failed to install, skipping dbt operations")
    
    # Change back to root directory
    os.chdir("..")
    
    return True  # Continue with setup even if dbt fails

def test_setup():
    """Test the setup by running basic checks."""
    print("🧪 Testing setup...")
    
    # Test Python imports
    try:
        import pandas
        import streamlit
        import plotly
        import duckdb
        print("✅ Python dependencies imported successfully")
    except ImportError as e:
        print(f"❌ Python import failed: {e}")
        return False
    
    # Test package import
    try:
        sys.path.append("src")
        from packagingco_insights.utils import data_loader
        print("✅ Package imported successfully")
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False
    
    # Test database connection (optional)
    try:
        import duckdb
        conn = duckdb.connect(':memory:')
        conn.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"⚠️  Database connection test skipped: {e}")
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up PackagingCo BI Portfolio")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check platform
    platform_type = check_platform()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies(platform_type):
        print("❌ Failed to install dependencies")
        if platform_type == "windows":
            print("\n💡 Windows-specific troubleshooting:")
            print("1. Try installing Visual Studio Build Tools")
            print("2. Use WSL2 for full compatibility")
            print("3. Use Docker for isolated environment")
            print("4. Check the requirements-windows.txt file")
        sys.exit(1)
    
    # Install package (optional)
    install_package()
    
    # Setup dbt
    if not setup_dbt():
        print("❌ Failed to setup dbt")
        sys.exit(1)
    
    # Test setup
    if not test_setup():
        print("❌ Setup test failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the dashboard: streamlit run streamlit_app/app.py")
    print("2. Open Jupyter notebooks: jupyter notebook notebooks/")
    print("3. View dbt docs: dbt docs serve (in dbt directory)")
    print("4. Explore the code in src/ directory")
    
    if platform_type == "windows":
        print("\n⚠️  Windows Notes:")
        print("- Apache Airflow was excluded due to compilation issues")
        print("- Consider using Prefect or Dagster as alternatives")
        print("- Or run Airflow in Docker/WSL2")
    
    print("\n🌐 Dashboard will be available at: http://localhost:8501")
    print("📚 Documentation: Check the README.md file")

if __name__ == "__main__":
    main() 