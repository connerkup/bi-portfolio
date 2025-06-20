"""
Data loading utilities for the BI portfolio.
"""

import pandas as pd
import duckdb
import sqlite3
from typing import Optional, Dict, Any
import os
from pathlib import Path
import numpy as np


def connect_to_database(db_path: str = "data/processed/portfolio.duckdb") -> duckdb.DuckDBPyConnection:
    """
    Connect to the DuckDB database.
    
    Args:
        db_path: Path to the DuckDB database file
    
    Returns:
        DuckDB connection object
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to DuckDB
    conn = duckdb.connect(db_path)
    return conn


def load_data(query: str, 
              db_path: str = "data/processed/portfolio.duckdb",
              **kwargs: Any) -> pd.DataFrame:
    """
    Load data from the database using a SQL query.
    
    Args:
        query: SQL query to execute
        db_path: Path to the database file
        **kwargs: Additional arguments to pass to pandas.read_sql
    
    Returns:
        DataFrame with the query results
    """
    conn = connect_to_database(db_path)
    
    try:
        # Use DuckDB's execute method instead of pandas read_sql
        df = conn.execute(query).fetchdf()
        return df
    finally:
        conn.close()


def load_csv_data(file_path: str, **kwargs: Any) -> pd.DataFrame:
    """
    Load data from a CSV file.
    
    Args:
        file_path: Path to the CSV file
        **kwargs: Additional arguments to pass to pandas.read_csv
    
    Returns:
        DataFrame with the CSV data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return pd.read_csv(file_path, **kwargs)


def load_esg_data(db_path: str = "data/processed/portfolio.duckdb") -> pd.DataFrame:
    """
    Load ESG data from the database.
    
    Args:
        db_path: Path to the database file
    
    Returns:
        DataFrame with ESG data
    """
    query = """
    SELECT * FROM fact_esg_monthly
    ORDER BY month
    """
    return load_data(query, db_path)


def load_finance_data(db_path: str = "data/processed/portfolio.duckdb") -> pd.DataFrame:
    """
    Load financial data from the database.
    
    Args:
        db_path: Path to the database file
    
    Returns:
        DataFrame with financial data
    """
    query = """
    SELECT * FROM fact_financial_monthly
    ORDER BY month
    """
    return load_data(query, db_path)


def load_sales_data(db_path: str = "data/processed/portfolio.duckdb") -> pd.DataFrame:
    """
    Load sales data from the database.
    
    Args:
        db_path: Path to the database file
    
    Returns:
        DataFrame with sales data
    """
    query = """
    SELECT * FROM stg_sales_data
    ORDER BY date
    """
    return load_data(query, db_path)


def get_database_info(db_path: str = "data/processed/portfolio.duckdb") -> Dict[str, Any]:
    """
    Get information about the database and its tables.
    
    Args:
        db_path: Path to the database file
    
    Returns:
        Dictionary with database information
    """
    conn = connect_to_database(db_path)
    
    try:
        # Get list of tables
        tables_query = "SHOW TABLES"
        tables = conn.execute(tables_query).fetchdf()
        
        # Get table schemas
        schemas = {}
        for table in tables['name']:
            schema_query = f"DESCRIBE {table}"
            schema = conn.execute(schema_query).fetchdf()
            schemas[table] = schema
        
        # Get row counts
        row_counts = {}
        for table in tables['name']:
            count_query = f"SELECT COUNT(*) as count FROM {table}"
            count = conn.execute(count_query).fetchdf()
            row_counts[table] = count['count'].iloc[0]
        
        return {
            'tables': tables['name'].tolist(),
            'schemas': schemas,
            'row_counts': row_counts
        }
    finally:
        conn.close()


def check_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform basic data quality checks on a DataFrame.
    
    Args:
        df: DataFrame to check
    
    Returns:
        Dictionary with data quality metrics
    """
    quality_report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'data_types': df.dtypes.to_dict()
    }
    
    # Check for numeric columns and their ranges
    # Include boolean columns as they are numeric in pandas
    numeric_columns = df.select_dtypes(include=[np.number, 'bool']).columns
    numeric_stats = {}
    for col in numeric_columns:
        numeric_stats[col] = {
            'min': df[col].min(),
            'max': df[col].max(),
            'mean': df[col].mean(),
            'std': df[col].std()
        }
    
    quality_report['numeric_stats'] = numeric_stats
    
    return quality_report 