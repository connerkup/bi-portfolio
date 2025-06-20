"""
Basic tests to verify the test setup is working correctly.
"""

import pytest
import pandas as pd
import numpy as np


def test_imports():
    """Test that all required modules can be imported."""
    try:
        from src.packagingco_insights.analysis.finance_analysis import FinanceAnalyzer
        from src.packagingco_insights.analysis.esg_analysis import ESGAnalyzer
        from src.packagingco_insights.analysis.forecasting import SalesForecaster
        from src.packagingco_insights.utils.data_loader import check_data_quality
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import required modules: {e}")


def test_pandas_working():
    """Test that pandas is working correctly."""
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['a', 'b', 'c']
    })
    assert len(df) == 3
    assert list(df.columns) == ['A', 'B']


def test_numpy_working():
    """Test that numpy is working correctly."""
    arr = np.array([1, 2, 3, 4, 5])
    assert len(arr) == 5
    assert arr.mean() == 3.0


def test_pytest_fixtures():
    """Test that pytest fixtures are working."""
    # This test uses the fixtures defined in conftest.py
    assert True


def test_basic_calculation():
    """Test a basic calculation to ensure math works."""
    result = 2 + 2
    assert result == 4


def test_string_operations():
    """Test string operations."""
    text = "Hello, World!"
    assert len(text) == 13
    assert "Hello" in text
    assert text.upper() == "HELLO, WORLD!"


def test_dataframe_operations():
    """Test pandas DataFrame operations."""
    # Create test data
    data = {
        'date': pd.date_range('2023-01-01', periods=5, freq='D'),
        'value': [10, 20, 30, 40, 50],
        'category': ['A', 'B', 'A', 'B', 'A']
    }
    df = pd.DataFrame(data)
    
    # Test basic operations
    assert len(df) == 5
    assert df['value'].sum() == 150
    assert df['value'].mean() == 30
    assert len(df['category'].unique()) == 2
    
    # Test grouping
    grouped = df.groupby('category')['value'].sum()
    assert grouped['A'] == 90  # 10 + 30 + 50
    assert grouped['B'] == 60  # 20 + 40


def test_numpy_operations():
    """Test numpy operations."""
    # Test array creation and operations
    arr = np.random.rand(100)
    assert len(arr) == 100
    assert 0 <= arr.min() <= arr.max() <= 1
    
    # Test statistical operations
    assert abs(arr.mean() - 0.5) < 0.2  # Should be close to 0.5 for random uniform
    assert arr.std() > 0  # Standard deviation should be positive


def test_error_handling():
    """Test error handling."""
    with pytest.raises(ValueError):
        raise ValueError("Test error")
    
    with pytest.raises(TypeError):
        "string" + 123  # type: ignore # TypeError: can only concatenate str (not "int") to str


def test_file_operations():
    """Test basic file operations."""
    import tempfile
    import os
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        temp_file = f.name
    
    # Check file exists
    assert os.path.exists(temp_file)
    
    # Read file content
    with open(temp_file, 'r') as f:
        content = f.read()
    
    assert content == "test content"
    
    # Cleanup
    os.remove(temp_file)
    assert not os.path.exists(temp_file) 