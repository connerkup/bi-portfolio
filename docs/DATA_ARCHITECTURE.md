# Data Architecture & Validation Guide

## Overview

This document explains the data architecture, validation strategies, and real-world considerations for the PackagingCo BI portfolio. It addresses how data flows through the system, validation approaches, and how to handle different data granularities.

## Current Data Architecture

### Data Sources & Granularity

#### **Current State (Vertical Slice)**
```
Raw Data (Seeds):
├── sample_sales_data.csv     # Monthly aggregated sales data
└── sample_esg_data.csv       # Monthly aggregated ESG data

dbt Models:
├── stg_sales_data.sql        # Staging with calculated metrics
├── stg_esg_data.sql          # Staging with efficiency metrics
├── fact_financial_monthly.sql # Monthly financial facts
└── fact_esg_monthly.sql      # Monthly ESG facts
```

#### **Real-World Data Sources**
In a production environment, data would originate from:

```
Transaction-Level Sources:
├── ERP System:
│   ├── sales_orders (order_id, customer_id, sku_id, quantity, price, date)
│   ├── products (sku_id, product_name, material_type, weight, cost)
│   ├── customers (customer_id, name, region, segment)
│   └── facilities (facility_id, name, location, capacity)
│
├── Sustainability System:
│   ├── production_batches (batch_id, facility_id, sku_id, start_time, end_time)
│   ├── material_usage (batch_id, material_id, quantity, cost)
│   ├── energy_consumption (facility_id, meter_id, timestamp, kwh)
│   ├── emissions (facility_id, source, timestamp, co2_kg)
│   └── waste_tracking (facility_id, waste_type, timestamp, kg)
│
└── External Sources:
    ├── market_data (commodity prices, growth rates)
    ├── regulatory_data (compliance requirements)
    └── weather_data (impact on production efficiency)
```

### Data Flow Architecture

```
Raw Systems → ETL/ELT → Data Warehouse → dbt Transformations → Analytics
     ↓              ↓              ↓              ↓              ↓
Transaction    Staging        Raw Tables    Business      Dashboards
Level Data     Layer         (Bronze)      Logic         & Reports
                              ↓
                          Processed Tables
                          (Silver/Gold)
```

## Data Validation Strategy

### 1. Schema Validation (dbt Tests)

#### **Generic Tests**
- `not_null`: Ensures required fields are populated
- `unique`: Validates unique constraints
- `accepted_values`: Validates categorical fields
- `positive_values`: Custom test for numeric fields
- `range`: Validates percentage fields (0-100)

#### **Custom Business Logic Tests**
- `material_percentages_sum_to_100`: Validates recycled + virgin = 100%
- `profit_margin_calculation`: Validates profit = revenue - costs
- `revenue_consistency`: Validates revenue = price × quantity

### 2. Data Quality Monitoring

#### **Automated Checks**
```sql
-- Example: Check for data freshness
SELECT 
    MAX(date) as latest_date,
    CURRENT_DATE - MAX(date) as days_since_update
FROM {{ ref('stg_sales_data') }}
WHERE CURRENT_DATE - MAX(date) > 7  -- Alert if > 7 days old
```

#### **Anomaly Detection**
```sql
-- Example: Detect unusual revenue patterns
WITH revenue_stats AS (
    SELECT 
        AVG(revenue) as avg_revenue,
        STDDEV(revenue) as revenue_std
    FROM {{ ref('stg_sales_data') }}
)
SELECT 
    date,
    revenue,
    (revenue - avg_revenue) / revenue_std as z_score
FROM {{ ref('stg_sales_data') }}, revenue_stats
WHERE ABS((revenue - avg_revenue) / revenue_std) > 3  -- 3-sigma rule
```

### 3. Data Lineage & Documentation

#### **dbt Documentation**
- Model descriptions and column definitions
- Data lineage graphs
- Business context and usage notes
- Data dictionary with field definitions

#### **Data Catalog**
- Source system information
- Update frequencies
- Data owners and stewards
- Business definitions and rules

## Handling Different Data Granularities

### Current Approach: Pre-Aggregated Data

**Advantages:**
- Simple to implement and understand
- Fast query performance
- Reduced storage requirements
- Suitable for executive dashboards

**Disadvantages:**
- Limited drill-down capabilities
- Cannot perform detailed analysis
- Difficult to validate at transaction level
- Less flexible for ad-hoc analysis

### Recommended Approach: Transaction-Level + Aggregation

#### **1. Transaction-Level Models**
```sql
-- models/staging/stg_sales_transactions.sql
SELECT 
    transaction_id,
    date,
    customer_id,
    product_sku,
    quantity,
    unit_price,
    unit_cost,
    -- ... other fields
FROM {{ source('erp', 'sales_orders') }}
```

#### **2. Aggregated Models**
```sql
-- models/marts/fact_sales_monthly.sql
SELECT 
    date_trunc('month', date) as month,
    product_line,
    region,
    customer_segment,
    SUM(quantity) as total_units,
    SUM(revenue) as total_revenue,
    -- ... aggregations
FROM {{ ref('stg_sales_transactions') }}
GROUP BY 1, 2, 3, 4
```

#### **3. Flexible Analysis Models**
```sql
-- models/marts/mart_sales_flexible.sql
{{ config(materialized='table') }}

WITH daily_sales AS (
    SELECT * FROM {{ ref('stg_sales_transactions') }}
),

monthly_sales AS (
    SELECT * FROM {{ ref('fact_sales_monthly') }}
),

quarterly_sales AS (
    SELECT * FROM {{ ref('fact_sales_quarterly') }}
)

SELECT 
    'daily' as granularity,
    date,
    product_line,
    region,
    customer_segment,
    quantity,
    revenue
FROM daily_sales

UNION ALL

SELECT 
    'monthly' as granularity,
    month as date,
    product_line,
    region,
    customer_segment,
    total_units as quantity,
    total_revenue as revenue
FROM monthly_sales

-- ... quarterly data
```

## Data Generation & Testing

### Mock Data Generator

The `data_generator.py` module provides:

#### **Features:**
- **Realistic Data**: Based on actual business rules and relationships
- **Multiple Granularities**: Transaction-level and aggregated data
- **Configurable Parameters**: Product costs, facility efficiency, market conditions
- **Time Series Patterns**: Seasonal variations, growth trends, sustainability improvements
- **Business Logic**: Valid relationships between costs, prices, and margins

#### **Usage:**
```python
from packagingco_insights.utils.data_generator import generate_mock_data

# Generate monthly aggregated data (current approach)
files = generate_mock_data(transaction_level=False)

# Generate transaction-level + aggregated data (recommended)
files = generate_mock_data(transaction_level=True)
```

#### **Generated Data Types:**
- **Sales Transactions**: Individual orders with customer, product, pricing details
- **ESG Transactions**: Production batches with emissions, energy, material usage
- **Monthly Aggregations**: Summarized data for dashboard consumption
- **Validation Data**: Test cases for data quality checks

### Data Refresh Strategy

#### **Incremental Models**
```sql
-- models/staging/stg_sales_incremental.sql
{{ config(materialized='incremental') }}

SELECT * FROM {{ source('erp', 'sales_orders') }}

{% if is_incremental() %}
WHERE date > (SELECT MAX(date) FROM {{ this }})
{% endif %}
```

#### **Snapshot Models**
```sql
-- snapshots/snapshot_customer_segments.sql
{% snapshot customer_segments_snapshot %}

{{
    config(
      target_schema='snapshots',
      strategy='timestamp',
      unique_key='customer_id',
      updated_at='updated_at',
    )
}}

SELECT * FROM {{ ref('stg_customers') }}

{% endsnapshot %}
```

## Real-World Implementation Considerations

### 1. Data Source Integration

#### **ETL/ELT Pipeline**
```python
# Example: Airflow DAG for data ingestion
def extract_sales_data():
    """Extract sales data from ERP system."""
    # Connect to ERP API/database
    # Extract incremental data
    # Load to staging area
    
def extract_esg_data():
    """Extract ESG data from sustainability systems."""
    # Connect to IoT sensors, meters
    # Extract real-time data
    # Load to staging area
```

#### **Data Quality Gates**
```python
def validate_data_quality():
    """Validate data before processing."""
    # Check for missing values
    # Validate business rules
    # Check for anomalies
    # Alert on failures
```

### 2. Performance Optimization

#### **Partitioning Strategy**
```sql
-- Partition by date for large tables
{{ config(
    materialized='table',
    partition_by={
        "field": "date",
        "data_type": "date",
        "granularity": "month"
    }
) }}
```

#### **Clustering Strategy**
```sql
-- Cluster by frequently filtered columns
{{ config(
    materialized='table',
    cluster_by=["product_line", "region"]
) }}
```

### 3. Security & Governance

#### **Data Access Control**
- Role-based access to different data granularities
- Sensitive data masking in development environments
- Audit logging for data access and changes

#### **Data Lineage Tracking**
- Track data transformations and dependencies
- Document business logic and calculations
- Maintain data dictionary and definitions

## Migration Path: From Aggregated to Transaction-Level

### Phase 1: Enhanced Validation (Current)
- Add comprehensive dbt tests
- Implement data quality monitoring
- Create detailed documentation

### Phase 2: Transaction-Level Foundation
- Create transaction-level staging models
- Implement incremental processing
- Add data lineage tracking

### Phase 3: Flexible Analytics
- Create multi-granularity marts
- Implement drill-down capabilities
- Add advanced analytics features

### Phase 4: Real-Time Integration
- Connect to live data sources
- Implement streaming data processing
- Add real-time dashboards

## Best Practices

### 1. Data Modeling
- Use consistent naming conventions
- Implement proper data types and constraints
- Document business logic and calculations
- Version control all data transformations

### 2. Testing Strategy
- Test at multiple levels (unit, integration, end-to-end)
- Implement automated data quality checks
- Monitor for data drift and anomalies
- Maintain test coverage for critical business logic

### 3. Documentation
- Document data sources and update frequencies
- Maintain data dictionary with field definitions
- Create data lineage diagrams
- Document business rules and calculations

### 4. Performance
- Use appropriate materializations (table, view, incremental)
- Implement partitioning and clustering strategies
- Monitor query performance and optimize as needed
- Consider caching strategies for frequently accessed data

## Conclusion

The current vertical slice approach with pre-aggregated data provides a solid foundation for demonstrating value quickly. However, the recommended path forward includes:

1. **Enhanced Validation**: Comprehensive testing and monitoring
2. **Transaction-Level Data**: More granular data for detailed analysis
3. **Flexible Architecture**: Support for multiple granularities
4. **Real-World Integration**: Connection to actual data sources

This architecture supports both current needs (executive dashboards) and future requirements (detailed analysis, drill-down capabilities, real-time insights) while maintaining data quality and governance standards. 