#!/usr/bin/env python3
"""
Test runner script for the packagingco_insights project.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print(f"Error: {e}")
        if e.stdout:
            print("Stdout:")
            print(e.stdout)
        if e.stderr:
            print("Stderr:")
            print(e.stderr)
        return False


def main():
    """Main test runner function."""
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🧪 PackagingCo Insights Test Suite")
    print("="*60)
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"✅ pytest version: {pytest.__version__}")
    except ImportError:
        print("❌ pytest not found. Please install it with: pip install pytest")
        return False
    
    # Check if coverage is installed
    try:
        import coverage
        print(f"✅ coverage available")
    except ImportError:
        print("⚠️  coverage not found. Install with: pip install pytest-cov")
    
    # Run different types of tests
    tests_passed = True
    
    # 1. Run unit tests (excluding integration tests)
    print("\n📋 Running Unit Tests...")
    unit_test_result = run_command(
        'python -m pytest tests/ -v -m "not integration" --tb=short',
        "Unit Tests"
    )
    tests_passed = tests_passed and unit_test_result
    
    # 2. Run integration tests
    print("\n🔗 Running Integration Tests...")
    integration_test_result = run_command(
        'python -m pytest tests/ -v -m integration --tb=short',
        "Integration Tests"
    )
    tests_passed = tests_passed and integration_test_result
    
    # 3. Run all tests with coverage
    print("\n📊 Running Tests with Coverage...")
    coverage_result = run_command(
        'python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html:htmlcov',
        "Tests with Coverage"
    )
    tests_passed = tests_passed and coverage_result
    
    # 4. Run linting
    print("\n🔍 Running Code Linting...")
    lint_result = run_command(
        'python -m flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503',
        "Code Linting"
    )
    tests_passed = tests_passed and lint_result
    
    # 5. Run type checking
    print("\n🔍 Running Type Checking...")
    type_result = run_command(
        'python -m mypy src/ --ignore-missing-imports',
        "Type Checking"
    )
    tests_passed = tests_passed and type_result
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    if tests_passed:
        print("🎉 All tests passed!")
        print("\n📁 Coverage report generated in: htmlcov/index.html")
        print("📁 Test artifacts available in: htmlcov/")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 