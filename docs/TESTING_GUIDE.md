# Testing Guide for PackagingCo Insights

This document provides a comprehensive guide to the testing implementation for the PackagingCo Insights project.

## Overview

The project includes a robust testing suite built with pytest that covers:

- **Unit Tests**: Individual function and class testing
- **Integration Tests**: End-to-end pipeline testing
- **Data Quality Tests**: Validation of data processing
- **Edge Case Testing**: Error handling and boundary conditions

## Test Structure

```
tests/
├── __init__.py                 # Tests package
├── conftest.py                 # Pytest fixtures and configuration
├── test_basic.py               # Basic functionality tests
├── test_finance_analysis.py    # FinanceAnalyzer tests
├── test_esg_analysis.py        # ESGAnalyzer tests
├── test_forecasting.py         # SalesForecaster tests
├── test_utils.py               # Utility function tests
└── test_integration.py         # Integration tests
```

## Test Categories

### 1. Unit Tests

#### FinanceAnalyzer Tests (`test_finance_analysis.py`)
- **Initialization**: Valid and invalid data handling
- **Revenue Trends**: Monthly, quarterly, yearly calculations
- **Profitability Metrics**: Gross profit, margins, per-unit calculations
- **Growth Rates**: Percentage change calculations with smoothing
- **Contribution Margin**: Margin analysis and calculations
- **Chart Generation**: Plotly figure creation
- **Data Validation**: Edge cases and error handling

#### ESGAnalyzer Tests (`test_esg_analysis.py`)
- **Initialization**: Data validation and setup
- **Emissions Trends**: Time-series analysis by different periods
- **Material Efficiency**: Recycling rates and waste calculations
- **ESG Scoring**: Composite score calculation with custom weights
- **Chart Generation**: Emissions and materials visualization
- **Score Normalization**: Proper scaling and ranking

#### SalesForecaster Tests (`test_forecasting.py`)
- **Data Preparation**: Time-series feature engineering
- **Exponential Smoothing**: Smooth forecast generation
- **Moving Average**: Alternative forecasting method
- **Trend Analysis**: Direction and strength calculations
- **Chart Generation**: Forecast visualization
- **Performance**: Large dataset handling

#### Utility Tests (`test_utils.py`)
- **Database Operations**: Connection and query execution
- **CSV Loading**: File handling and error cases
- **Data Quality**: Missing values, duplicates, statistics
- **Database Info**: Schema and metadata retrieval

### 2. Integration Tests (`test_integration.py`)

#### Complete Pipeline Testing
- **End-to-End Analysis**: Full workflow from data to insights
- **Cross-Component Consistency**: Analyzer interoperability
- **Data Flow**: Sequential processing validation
- **Error Handling**: Graceful failure management
- **Performance**: Large dataset processing

### 3. Basic Tests (`test_basic.py`)
- **Import Verification**: Module availability
- **Core Libraries**: Pandas, NumPy functionality
- **File Operations**: Temporary file handling
- **Error Handling**: Exception testing

## Test Fixtures

### Data Fixtures (`conftest.py`)

#### Sample Data Generation
- **`sample_finance_data`**: Realistic financial metrics
- **`sample_esg_data`**: ESG metrics with proper relationships
- **`sample_sales_data`**: Time-series sales data with trends
- **`empty_dataframe`**: Empty DataFrame for edge cases
- **`invalid_finance_data`**: Missing required columns
- **`invalid_esg_data`**: Incomplete ESG data

#### Data Characteristics
- **Realistic Values**: Business-appropriate ranges
- **Proper Relationships**: Correlated metrics (e.g., revenue vs. costs)
- **Time Series**: Monthly data with trends and seasonality
- **Multiple Dimensions**: Product lines, regions, facilities

## Running Tests

### Quick Start
```bash
# Run all tests
python scripts/run_tests.py

# Run tests directly
python -m pytest tests/ -v
```

### Specific Test Categories
```bash
# Unit tests only
python -m pytest tests/ -v -m "not integration"

# Integration tests only
python -m pytest tests/ -v -m integration

# With coverage
python -m pytest tests/ -v --cov=src --cov-report=html:htmlcov
```

### Individual Test Files
```bash
# Finance analysis tests
python -m pytest tests/test_finance_analysis.py -v

# ESG analysis tests
python -m pytest tests/test_esg_analysis.py -v

# Forecasting tests
python -m pytest tests/test_forecasting.py -v
```

### Specific Test Functions
```bash
# Run specific test
python -m pytest tests/test_finance_analysis.py::TestFinanceAnalyzer::test_calculate_profitability_metrics -v
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    basic: marks tests as basic functionality tests
```

### Coverage Configuration
- **Source Coverage**: `src/` directory
- **HTML Reports**: `htmlcov/index.html`
- **Terminal Output**: Missing line coverage
- **Exclusions**: Test files and configuration

## Test Quality Standards

### Code Coverage
- **Target**: >80% line coverage
- **Critical Paths**: 100% coverage for core calculations
- **Error Handling**: All exception paths tested

### Test Quality
- **Descriptive Names**: Clear test function names
- **Documentation**: Docstrings for all test functions
- **Isolation**: Tests don't depend on each other
- **Cleanup**: Proper resource cleanup

### Data Validation
- **Input Validation**: Invalid data handling
- **Edge Cases**: Empty datasets, missing values
- **Boundary Conditions**: Min/max values, zero values
- **Type Safety**: Proper data type handling

## Adding New Tests

### Unit Test Template
```python
def test_function_name():
    """Test description."""
    # Arrange
    test_data = create_test_data()
    
    # Act
    result = function_under_test(test_data)
    
    # Assert
    assert result is not None
    assert len(result) > 0
    # Add specific assertions
```

### Integration Test Template
```python
@pytest.mark.integration
def test_complete_workflow():
    """Test complete analysis pipeline."""
    # Setup
    data = create_comprehensive_test_data()
    
    # Execute pipeline
    result1 = component1.process(data)
    result2 = component2.process(result1)
    final_result = component3.process(result2)
    
    # Validate
    assert final_result is not None
    assert all_expected_columns_present(final_result)
```

### Fixture Template
```python
@pytest.fixture
def new_test_data():
    """Create test data for new functionality."""
    # Generate realistic test data
    data = {
        'column1': [value1, value2, value3],
        'column2': [value4, value5, value6]
    }
    return pd.DataFrame(data)
```

## Best Practices

### Test Organization
1. **Group Related Tests**: Use test classes for related functionality
2. **Clear Naming**: Descriptive test and fixture names
3. **Documentation**: Explain what each test validates
4. **Modularity**: Keep tests focused and independent

### Data Management
1. **Realistic Data**: Use business-appropriate values
2. **Proper Relationships**: Maintain data consistency
3. **Edge Cases**: Include boundary conditions
4. **Cleanup**: Remove temporary files and data

### Error Testing
1. **Invalid Inputs**: Test with bad data
2. **Missing Data**: Handle empty or incomplete datasets
3. **Type Errors**: Test with wrong data types
4. **Exception Handling**: Verify error messages

### Performance Testing
1. **Large Datasets**: Test with realistic data volumes
2. **Memory Usage**: Monitor resource consumption
3. **Execution Time**: Ensure reasonable performance
4. **Scalability**: Test with increasing data sizes

## Continuous Integration

### Automated Testing
- **Pre-commit**: Run tests before commits
- **CI Pipeline**: Automated test execution
- **Coverage Reports**: Track coverage trends
- **Quality Gates**: Enforce minimum coverage

### Test Maintenance
- **Regular Updates**: Keep tests current with code changes
- **Refactoring**: Improve test quality over time
- **Documentation**: Update test documentation
- **Performance**: Optimize slow tests

## Troubleshooting

### Common Issues
1. **Import Errors**: Check module paths and dependencies
2. **Fixture Errors**: Verify fixture definitions and scope
3. **Data Issues**: Ensure test data is properly formatted
4. **Coverage Gaps**: Identify untested code paths

### Debugging Tests
```bash
# Run with debug output
python -m pytest tests/ -v -s

# Run single test with debugger
python -m pytest tests/test_file.py::test_function -v -s --pdb

# Check test collection
python -m pytest tests/ --collect-only
```

## Conclusion

The testing suite provides comprehensive coverage of the PackagingCo Insights functionality, ensuring:

- **Code Quality**: Reliable and maintainable code
- **Business Logic**: Accurate calculations and analysis
- **Error Handling**: Robust error management
- **Integration**: Seamless component interaction
- **Documentation**: Clear test specifications

Regular test execution and maintenance ensure the project remains reliable and ready for production use. 