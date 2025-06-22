# Deployment Information

Generated on: 2025-06-22 10:11:03

## Database Information
- File: portfolio.duckdb
- Size: 40.26 MB
- Location: ecometrics/portfolio.duckdb

## dbt Models
This database contains the following dbt models:
- esg_transactions: 36,500 rows
- fact_esg_monthly: 180 rows
- fact_financial_monthly: 1,200 rows
- mart_esg_summary: 2 rows
- sales_transactions: 73,000 rows
- sample_esg_data: 180 rows
- sample_sales_data: 1,200 rows
- stg_esg_data: 180 rows
- stg_esg_transactions: 2,173 rows
- stg_sales_data: 1,200 rows
- stg_sales_transactions: 73,000 rows
- supply_chain_data: 326 rows

## Deployment Steps
1. Commit this database file to your repository
2. Deploy to Streamlit Cloud using ecometrics/Home.py as the main file
3. Verify connection in the Data Browser page

## Notes
- This database file should be included in version control for Streamlit Cloud deployment
- The file will be automatically detected by the data connector
- For production, consider using an external database
