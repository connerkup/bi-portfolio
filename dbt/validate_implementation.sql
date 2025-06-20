-- Validation script for transaction-level implementation
-- This script validates that our new transaction-level models are working correctly

-- Check transaction counts
SELECT 
    'Sales Transactions' as model_name,
    COUNT(*) as record_count
FROM {{ ref('stg_sales_transactions') }}

UNION ALL

SELECT 
    'ESG Transactions' as model_name,
    COUNT(*) as record_count
FROM {{ ref('stg_esg_transactions') }}

UNION ALL

SELECT 
    'Financial Fact Table' as model_name,
    COUNT(*) as record_count
FROM {{ ref('fact_financial_monthly') }}

UNION ALL

SELECT 
    'ESG Fact Table' as model_name,
    COUNT(*) as record_count
FROM {{ ref('fact_esg_monthly') }};

-- Check data quality metrics
SELECT 
    'Data Quality Check' as check_type,
    COUNT(*) as total_records,
    COUNT(CASE WHEN data_quality_flag = 'Valid' THEN 1 END) as valid_records,
    COUNT(CASE WHEN data_quality_flag != 'Valid' THEN 1 END) as invalid_records,
    ROUND(COUNT(CASE WHEN data_quality_flag = 'Valid' THEN 1 END) * 100.0 / COUNT(*), 2) as quality_percentage
FROM {{ ref('stg_sales_transactions') }};

-- Check sustainability performance distribution
SELECT 
    sustainability_performance,
    COUNT(*) as batch_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM {{ ref('stg_esg_transactions') }}
GROUP BY sustainability_performance
ORDER BY batch_count DESC;

-- Check transaction performance distribution
SELECT 
    performance_category,
    COUNT(*) as transaction_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM {{ ref('stg_sales_transactions') }}
GROUP BY performance_category
ORDER BY transaction_count DESC; 