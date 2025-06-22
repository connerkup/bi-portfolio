"""
Data connector for EcoMetrics Streamlit app.
Handles connections to dbt pipeline and provides easy access to transformed data.
"""

import streamlit as st
from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_data
import pandas as pd
import duckdb
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DuckDBConnection(ExperimentalBaseConnection[duckdb.DuckDBPyConnection]):
    """Streamlit connection for DuckDB database"""
    
    def _connect(self, **kwargs) -> duckdb.DuckDBPyConnection:
        # Try to get database path from secrets or kwargs
        if 'database' in kwargs:
            db_path = kwargs.pop('database')
            logger.info(f"Using database path from kwargs: {db_path}")
        elif 'database' in self._secrets:
            db_path = self._secrets['database']
            logger.info(f"Using database path from secrets: {db_path}")
        else:
            # Fallback to searching for database file
            possible_paths = [
                "portfolio.duckdb",                     # Current directory
                "data/processed/portfolio.duckdb",      # Local development
                "../data/processed/portfolio.duckdb",   # From ecometrics directory
            ]
            
            logger.info(f"Searching for database in paths: {possible_paths}")
            logger.info(f"Current working directory: {os.getcwd()}")
            
            for path in possible_paths:
                logger.info(f"Checking if path exists: {path}")
                if os.path.exists(path):
                    db_path = path
                    logger.info(f"Found database at: {db_path}")
                    break
            else:
                # Default to current directory
                db_path = "portfolio.duckdb"
                logger.warning(f"No database found in search paths, defaulting to: {db_path}")
        
        logger.info(f"Attempting to connect to database: {db_path}")
        try:
            conn = duckdb.connect(database=db_path, **kwargs)
            logger.info(f"Successfully connected to database: {db_path}")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database {db_path}: {e}")
            raise
    
    def cursor(self) -> duckdb.DuckDBPyConnection:
        logger.info("Getting cursor from connection...")
        try:
            cursor = self._instance.cursor()
            logger.info("Cursor obtained successfully")
            return cursor
        except Exception as e:
            logger.error(f"Error getting cursor: {e}")
            raise
    
    def query(self, query: str, ttl: int = 3600, **kwargs) -> pd.DataFrame:
        @cache_data(ttl=ttl)
        def _query(query: str, **kwargs) -> pd.DataFrame:
            cursor = self.cursor()
            cursor.execute(query, **kwargs)
            return cursor.df()
        
        return _query(query, **kwargs)
    
    def get_available_tables(self, ttl: int = 3600) -> List[str]:
        """Get list of available tables in the database."""
        @cache_data(ttl=ttl)
        def _get_tables() -> List[str]:
            logger.info("Getting available tables from database...")
            try:
                cursor = self.cursor()
                logger.info("Cursor obtained successfully")
                
                logger.info("Executing SHOW TABLES query...")
                tables = cursor.execute("SHOW TABLES").fetchdf()
                logger.info(f"SHOW TABLES query result: {tables}")
                
                table_list = tables['name'].tolist()
                logger.info(f"Found {len(table_list)} tables: {table_list}")
                return table_list
            except Exception as e:
                logger.error(f"Error getting tables: {e}")
                logger.error(f"Error type: {type(e)}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return []
        
        return _get_tables()
    
    def get_table_info(self, table_name: str, ttl: int = 3600) -> Dict[str, Any]:
        """Get information about a specific table."""
        @cache_data(ttl=ttl)
        def _get_table_info(table_name: str) -> Dict[str, Any]:
            cursor = self.cursor()
            
            # Get table schema
            schema = cursor.execute(f"DESCRIBE {table_name}").fetchdf()
            
            # Get row count
            count = cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}").fetchdf()
            
            # Get sample data
            sample = cursor.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchdf()
            
            return {
                'schema': schema,
                'row_count': count['count'].iloc[0],
                'sample_data': sample,
                'columns': schema['column_name'].tolist()
            }
        
        return _get_table_info(table_name)
    
    def get_data_quality_metrics(self, ttl: int = 3600) -> Dict[str, Any]:
        """Get data quality metrics for all tables."""
        @cache_data(ttl=ttl)
        def _get_metrics() -> Dict[str, Any]:
            cursor = self.cursor()
            metrics = {}
            
            try:
                tables = cursor.execute("SHOW TABLES").fetchdf()
                
                for table in tables['name']:
                    try:
                        # Get row count
                        count_query = f"SELECT COUNT(*) as count FROM {table}"
                        count = cursor.execute(count_query).fetchdf()
                        
                        # Get null counts for each column
                        schema = cursor.execute(f"DESCRIBE {table}").fetchdf()
                        null_counts = {}
                        
                        for col in schema['column_name']:
                            null_query = f"SELECT COUNT(*) as null_count FROM {table} WHERE {col} IS NULL"
                            null_count = cursor.execute(null_query).fetchdf()
                            null_counts[col] = null_count['null_count'].iloc[0]
                        
                        metrics[table] = {
                            'row_count': count['count'].iloc[0],
                            'null_counts': null_counts,
                            'columns': schema['column_name'].tolist()
                        }
                    except Exception as e:
                        logger.warning(f"Failed to get metrics for {table}: {e}")
                        metrics[table] = {'error': str(e)}
                        
            except Exception as e:
                logger.error(f"Failed to get data quality metrics: {e}")
            
            return metrics
        
        return _get_metrics()


def get_data_connector() -> DuckDBConnection:
    """
    Get a Streamlit connection to the DuckDB database.
    
    Returns:
        DuckDBConnection instance
    """
    return st.connection("duckdb", type=DuckDBConnection)


def check_dbt_availability() -> Dict[str, Any]:
    """
    Check if dbt data is available and provide status information.
    
    Returns:
        Dictionary with availability status and information
    """
    logger.info("Starting dbt availability check...")
    try:
        connector = get_data_connector()
        logger.info("Data connector created successfully")
        
        # Try to get tables to test connection
        logger.info("Attempting to get available tables...")
        tables = connector.get_available_tables(ttl=60)  # Short TTL for status check
        logger.info(f"Retrieved {len(tables)} tables: {tables}")
        
        # Check for key dbt models
        key_models = ['fact_esg_monthly', 'fact_financial_monthly', 'stg_sales_data', 'stg_esg_data']
        available_models = [model for model in key_models if model in tables]
        logger.info(f"Found {len(available_models)}/{len(key_models)} key models: {available_models}")
        
        result = {
            'available': len(available_models) > 0,
            'message': f"Found {len(available_models)}/{len(key_models)} key models",
            'available_tables': tables,
            'key_models_found': available_models,
            'key_models_missing': [model for model in key_models if model not in tables],
            'db_path': 'portfolio.duckdb',  # This will be resolved by the connection
            'deployment_note': 'Database connection successful!'
        }
        logger.info(f"Availability check result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error during availability check: {e}")
        return {
            'available': False,
            'message': f'Error checking availability: {e}',
            'db_path': 'portfolio.duckdb',
            'deployment_note': 'Error occurred while checking database availability.'
        }


def load_esg_data() -> Tuple[pd.DataFrame, str]:
    """
    Load ESG data from dbt models.
    
    Returns:
        Tuple of (DataFrame, status_message)
    """
    try:
        connector = get_data_connector()
        
        # Try to load from fact_esg_monthly first
        query = """
        SELECT * FROM fact_esg_monthly 
        ORDER BY date DESC
        """
        df = connector.query(query)
        return df, "Loaded from fact_esg_monthly"
    except Exception as e:
        logger.warning(f"Failed to load from fact_esg_monthly: {e}")
        
        # Fallback to staging table
        try:
            query = """
            SELECT * FROM stg_esg_data 
            ORDER BY date DESC
            """
            df = connector.query(query)
            return df, "Loaded from stg_esg_data (fallback)"
        except Exception as e2:
            logger.error(f"Failed to load ESG data: {e2}")
            return pd.DataFrame(), f"Error loading ESG data: {e2}"


def load_finance_data() -> Tuple[pd.DataFrame, str]:
    """
    Load financial data from dbt models.
    
    Returns:
        Tuple of (DataFrame, status_message)
    """
    try:
        connector = get_data_connector()
        
        # Try to load from fact_financial_monthly first
        query = """
        SELECT * FROM fact_financial_monthly 
        ORDER BY date DESC
        """
        df = connector.query(query)
        return df, "Loaded from fact_financial_monthly"
    except Exception as e:
        logger.warning(f"Failed to load from fact_financial_monthly: {e}")
        
        # Fallback to staging table
        try:
            query = """
            SELECT * FROM stg_sales_data 
            ORDER BY date DESC
            """
            df = connector.query(query)
            return df, "Loaded from stg_sales_data (fallback)"
        except Exception as e2:
            logger.error(f"Failed to load finance data: {e2}")
            return pd.DataFrame(), f"Error loading finance data: {e2}"


def load_supply_chain_data() -> Tuple[pd.DataFrame, str]:
    """
    Load supply chain data from dbt models.
    
    Returns:
        Tuple of (DataFrame, status_message)
    """
    try:
        connector = get_data_connector()
        query = """
        SELECT * FROM stg_supply_chain_data 
        ORDER BY date DESC
        """
        df = connector.query(query)
        return df, "Loaded from stg_supply_chain_data"
    except Exception as e:
        logger.error(f"Failed to load supply chain data: {e}")
        return pd.DataFrame(), f"Error loading supply chain data: {e}"


def initialize_sample_data_if_needed():
    """
    Initialize sample data if dbt data is not available.
    This is useful for development and demonstration purposes.
    """
    try:
        connector = get_data_connector()
        tables = connector.get_available_tables(ttl=60)
        
        # If no tables exist, we might need to run dbt
        if not tables:
            logger.info("No tables found in database. Please run 'dbt run' to populate the database.")
            return
            
    except Exception as e:
        logger.error(f"Error checking tables: {e}") 