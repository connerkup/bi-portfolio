#!/usr/bin/env python3
"""
Test script to verify color standardization across all pages.
This script checks that all pages are importing and using the color_config module.
"""

import os
import re
from pathlib import Path

def check_file_for_color_imports(file_path):
    """Check if a file imports and uses the color_config module."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for color_config import
        has_import = 'from color_config import' in content or 'import color_config' in content
        
        # Check for usage of color functions
        color_functions = [
            'get_comparison_colors',
            'get_monochrome_colors', 
            'get_heat_colors',
            'get_sustainability_color',
            'get_financial_color',
            'get_performance_color',
            'CSS_COLORS',
            'CHART_COLORS'
        ]
        
        used_functions = [func for func in color_functions if func in content]
        
        # Check for old hardcoded colors
        old_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#4ECDC4', '#45B7D1', '#FF6B6B', '#9B59B6', '#E67E22',
            '#8E44AD', '#27AE60', '#F39C12', '#E74C3C', '#FFA07A'
        ]
        
        found_old_colors = [color for color in old_colors if color in content]
        
        return {
            'file': file_path,
            'has_import': has_import,
            'used_functions': used_functions,
            'found_old_colors': found_old_colors,
            'needs_update': len(found_old_colors) > 0 or not has_import
        }
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e),
            'needs_update': True
        }

def main():
    """Main function to check all Python files in the ecometrics directory."""
    ecometrics_dir = Path('.')
    
    # Find all Python files
    python_files = list(ecometrics_dir.glob('*.py')) + list(ecometrics_dir.glob('pages/*.py'))
    
    print("🔍 Checking color standardization across all pages...")
    print("=" * 60)
    
    results = []
    for file_path in python_files:
        if file_path.name != 'color_config.py' and file_path.name != 'test_color_standardization.py':
            result = check_file_for_color_imports(file_path)
            results.append(result)
    
    # Report results
    updated_files = [r for r in results if not r.get('needs_update', True)]
    needs_update = [r for r in results if r.get('needs_update', True)]
    
    print(f"✅ Files using standardized colors: {len(updated_files)}")
    for result in updated_files:
        print(f"  ✓ {result['file']}")
        if result.get('used_functions'):
            print(f"    Functions used: {', '.join(result['used_functions'])}")
    
    print(f"\n⚠️  Files needing updates: {len(needs_update)}")
    for result in needs_update:
        print(f"  ⚠ {result['file']}")
        if result.get('found_old_colors'):
            print(f"    Old colors found: {', '.join(result['found_old_colors'])}")
        if not result.get('has_import'):
            print(f"    Missing color_config import")
        if result.get('error'):
            print(f"    Error: {result['error']}")
    
    print("\n" + "=" * 60)
    if needs_update:
        print("🎨 Color standardization is not complete. Some files still need updates.")
        return False
    else:
        print("🎨 Color standardization is complete! All files are using the standardized color palette.")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 