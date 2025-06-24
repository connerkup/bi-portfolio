# Supply Chain Insights Setup Guide

This document provides a comprehensive guide to setting up and using the supply chain insights functionality in the EcoMetrics BI Portfolio.

## Overview

The supply chain insights module provides comprehensive analysis of supplier performance, delivery optimization, quality control, and sustainability metrics. It includes:

- **dbt Models**: Data transformation and aggregation pipelines
- **Analysis Module**: Python-based analytics and insights generation
- **Streamlit Integration**: Interactive dashboard for supply chain insights
- **Testing Framework**: Comprehensive validation and quality checks

## Architecture

```
data/raw/supply_chain_data.csv          # Raw supply chain data
    ↓
dbt/models/supply_chain/
├── stg_supply_chain_data.sql          # Staging model
├── fact_supply_chain_monthly.sql      # Monthly aggregations
└── mart_supply_chain_summary.sql      # Summary mart table
    ↓
src/packagingco_insights/analysis/
└── supply_chain_analysis.py           # Analysis module
    ↓
ecometrics/pages/3_Supply_Chain_Insights.py  # Streamlit dashboard
```

## Data Schema

### Raw Data Structure

The supply chain data should contain the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `date` | Date | Order date |
| `supplier` | String | Supplier name |
| `order_id` | String | Unique order identifier |
| `order_quantity` | Integer | Quantity ordered |
| `order_value` | Decimal | Total order value |
| `expected_delivery` | Date | Expected delivery date |
| `actual_delivery` | Date | Actual delivery date |
| `on_time_delivery` | Boolean | Whether delivery was on time |
| `quality_issues` | Boolean | Whether quality issues occurred |
| `defect_quantity` | Integer | Number of defective units |
| `supplier_reliability` | Decimal | Supplier reliability score (0-1) |
| `sustainability_rating` | Decimal | Sustainability rating (1-5) |

### Calculated Fields

The staging model automatically calculates:

- `unit_cost`: Order value / order quantity
- `defect_rate_pct`: Defect quantity / order quantity * 100
- `delivery_variance_days`: Actual delivery - expected delivery (days)
- `delivery_performance`: Categorized delivery performance
- `quality_status`: Quality issue status
- `reliability_category`: Supplier reliability category
- `sustainability_category`: Sustainability category

## Setup Instructions

### 1. Enable Supply Chain Models

The supply chain models are enabled by default in `dbt/dbt_project.yml`:

```yaml
supply_chain:
  +materialized: table
  +enabled: true
```

### 2. Run dbt Models

```bash
# Navigate to dbt directory
cd dbt

# Install dependencies
dbt deps

# Run supply chain models
dbt run --select supply_chain

# Test the models
dbt test --select supply_chain

# Generate documentation
dbt docs generate
```

### 3. Verify Data Loading

The data connector automatically tries to load from the fact table first, then falls back to the staging table:

```python
from ecometrics.data_connector import load_supply_chain_data

df, status = load_supply_chain_data()
print(f"Data loaded: {status}")
```

### 4. Test the Setup

Run the comprehensive test script:

```bash
python scripts/test_supply_chain_setup.py
```

## Analysis Features

### 1. Supplier Performance Analysis

```python
from src.packagingco_insights.analysis.supply_chain_analysis import SupplyChainAnalyzer

analyzer = SupplyChainAnalyzer(data)
summary = analyzer.get_supplier_performance_summary()

# Key metrics:
# - Total orders and order value
# - On-time delivery rate
# - Quality issue rate
# - Average defect rate
# - Supplier reliability and sustainability ratings
```

### 2. Delivery Performance Analysis

```python
delivery_analysis = analyzer.get_delivery_performance_analysis()

# Includes:
# - Overall on-time delivery rate
# - Delivery variance analysis
# - Supplier delivery performance
# - Monthly delivery trends
# - Delivery performance categories
```

### 3. Quality Control Analysis

```python
quality_analysis = analyzer.get_quality_control_analysis()

# Includes:
# - Overall quality metrics
# - Defect rate analysis
# - Supplier quality performance
# - Quality issue trends
# - Quality categories
```

### 4. Sustainability Analysis

```python
sustainability_analysis = analyzer.get_sustainability_analysis()

# Includes:
# - Overall sustainability metrics
# - Supplier sustainability performance
# - Sustainability rating distribution
# - Monthly sustainability trends
```

### 5. Cost Analysis

```python
cost_analysis = analyzer.get_cost_analysis()

# Includes:
# - Overall cost metrics
# - Unit cost trends
# - Supplier cost performance
# - Cost-quality correlation
```

### 6. Risk Assessment

```python
risk_assessment = analyzer.get_supplier_risk_assessment()

# Includes:
# - Overall risk scores
# - Risk categories (Low, Medium, High, Critical)
# - Component risk scores (delivery, quality, reliability, cost)
```

### 7. Key Insights and Recommendations

```python
insights = analyzer.get_key_insights()
recommendations = analyzer.get_recommendations()

# Automatically generated insights and actionable recommendations
# based on the data analysis
```

## Streamlit Dashboard Features

The supply chain insights dashboard (`ecometrics/pages/3_Supply_Chain_Insights.py`) provides:

### 1. Key Performance Indicators
- Total orders and order value
- On-time delivery rate
- Average supplier reliability

### 2. Interactive Filters
- Date range selection
- Supplier filtering
- Delivery performance filtering
- Quality status filtering

### 3. Visualizations
- **Inventory Management**: Order quantity trends, value trends, unit cost analysis
- **Supplier Performance**: Bubble charts showing reliability, delivery, and sustainability
- **Logistics Optimization**: Delivery performance analysis, variance distribution
- **Material Tracking**: Quality status analysis, defect rate by supplier

### 4. Data Summary
- Data coverage information
- Key insights summary

## Testing

### dbt Tests

The following tests validate data quality and calculations:

- **Data Quality Tests**: `test_supply_chain_calculations.sql`
- **Fact Table Tests**: `test_supply_chain_fact_calculations.sql`

### Python Tests

Comprehensive test suite in `tests/test_supply_chain_analysis.py`:

```bash
pytest tests/test_supply_chain_analysis.py -v
```

## Data Quality Checks

The system includes automatic data quality validation:

1. **Required Columns**: Validates all required columns are present
2. **Data Types**: Ensures proper data types for calculations
3. **Value Ranges**: Validates supplier reliability (0-1) and sustainability ratings (1-5)
4. **Calculations**: Verifies calculated fields match expected formulas
5. **Aggregations**: Ensures monthly aggregations match daily data

## Performance Optimization

### dbt Model Optimization

- **Materialized Tables**: All supply chain models are materialized as tables for performance
- **Incremental Processing**: Models can be configured for incremental processing
- **Partitioning**: Monthly data is naturally partitioned by date

### Analysis Optimization

- **Caching**: Streamlit data connector includes caching for performance
- **Efficient Aggregations**: Pre-calculated aggregations in fact tables
- **Lazy Loading**: Analysis functions only process data when called

## Troubleshooting

### Common Issues

1. **No Data Loaded**
   - Check if `supply_chain_data.csv` exists in `data/raw/`
   - Verify dbt models have been run successfully
   - Check database connection

2. **Missing Columns**
   - Ensure raw data contains all required columns
   - Check staging model for column transformations

3. **Calculation Errors**
   - Verify no division by zero in calculations
   - Check for null values in required fields
   - Validate date formats

4. **dbt Model Failures**
   - Check dbt logs for specific error messages
   - Verify source data freshness
   - Run `dbt debug` for connection issues

### Debug Commands

```bash
# Check dbt connection
dbt debug

# Validate models without running
dbt parse

# Check source freshness
dbt source freshness

# Run specific model with verbose output
dbt run --select stg_supply_chain_data --verbose
```

## Monitoring and Maintenance

### Regular Tasks

1. **Data Freshness**: Monitor source data freshness with `dbt source freshness`
2. **Model Performance**: Check model run times and optimize as needed
3. **Data Quality**: Run tests regularly with `dbt test`
4. **Documentation**: Update documentation with `dbt docs generate`

### Alerts

Set up alerts for:
- Failed dbt runs
- Data quality test failures
- Source data freshness violations
- Performance degradation

## Future Enhancements

Potential improvements and additions:

1. **Real-time Data**: Integration with real-time supply chain systems
2. **Predictive Analytics**: Forecasting delivery times and quality issues
3. **Supplier Scoring**: Advanced supplier performance scoring algorithms
4. **Cost Optimization**: Automated cost optimization recommendations
5. **Sustainability Tracking**: Enhanced sustainability metrics and reporting
6. **Integration**: API endpoints for external system integration

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review dbt logs and error messages
3. Run the test script to identify specific issues
4. Consult the data architecture documentation

## Related Documentation

- [Data Architecture Overview](DATA_ARCHITECTURE.md)
- [dbt Project Configuration](dbt/README.md)
- [Streamlit App Guide](ecometrics/README.md)
- [Testing Guide](docs/TESTING_GUIDE.md) 