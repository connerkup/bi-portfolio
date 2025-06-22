"""
Data connector for EcoMetrics Streamlit app.
Handles connections to dbt pipeline and provides easy access to transformed data.
"""

import streamlit as st
import pandas as pd
import duckdb
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBTDataConnector:
    """Connector class for accessing dbt pipeline data."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the DBT data connector.
        
        Args:
            db_path: Path to the DuckDB database file. If None, will try common paths.
        """
        if db_path is None:
            # Try multiple possible paths for different deployment scenarios
            possible_paths = [
                "ecometrics/portfolio.duckdb",          # For Streamlit Cloud & local after prep script
                "data/processed/portfolio.duckdb",      # Local development (dbt run output)
                "portfolio.duckdb",                     # If db is in root for some reason
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.db_path = path
                    break
            else:
                # Default to the most common path if none found
                self.db_path = "data/processed/portfolio.duckdb"
        else:
            self.db_path = db_path
            
        self.conn = None
        
    def connect(self) -> bool:
        """
        Connect to the DuckDB database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not os.path.exists(self.db_path):
                logger.warning(f"Database not found: {self.db_path}")
                return False
                
            self.conn = duckdb.connect(self.db_path)
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def get_available_tables(self) -> List[str]:
        """
        Get list of available tables in the database.
        
        Returns:
            List of table names
        """
        if not self.conn:
            if not self.connect():
                return []
        
        try:
            if self.conn is None:
                return []
            tables = self.conn.execute("SHOW TABLES").fetchdf()
            return tables['name'].tolist()
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            return []
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information about a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information
        """
        if not self.conn:
            if not self.connect():
                return {}
        
        try:
            if self.conn is None:
                return {}
            # Get table schema
            schema = self.conn.execute(f"DESCRIBE {table_name}").fetchdf()
            
            # Get row count
            count = self.conn.execute(f"SELECT COUNT(*) as count FROM {table_name}").fetchdf()
            
            # Get sample data
            sample = self.conn.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchdf()
            
            return {
                'schema': schema,
                'row_count': count['count'].iloc[0],
                'sample_data': sample,
                'columns': schema['column_name'].tolist()
            }
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            return {}
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query to execute
            
        Returns:
            DataFrame with query results
        """
        if not self.conn:
            if not self.connect():
                raise ConnectionError("Failed to connect to database")
        
        try:
            if self.conn is None:
                raise ConnectionError("Database connection is None")
            return self.conn.execute(query).fetchdf()
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise
    
    def load_esg_data(self) -> Tuple[pd.DataFrame, str]:
        """
        Load ESG data from dbt models.
        
        Returns:
            Tuple of (DataFrame, status_message)
        """
        try:
            # Try to load from fact_esg_monthly first
            query = """
            SELECT * FROM fact_esg_monthly 
            ORDER BY date DESC
            """
            df = self.execute_query(query)
            return df, "Loaded from fact_esg_monthly"
        except Exception as e:
            logger.warning(f"Failed to load from fact_esg_monthly: {e}")
            
            # Fallback to staging table
            try:
                query = """
                SELECT * FROM stg_esg_data 
                ORDER BY date DESC
                """
                df = self.execute_query(query)
                return df, "Loaded from stg_esg_data (fallback)"
            except Exception as e2:
                logger.error(f"Failed to load ESG data: {e2}")
                return pd.DataFrame(), f"Error loading ESG data: {e2}"
    
    def load_finance_data(self) -> Tuple[pd.DataFrame, str]:
        """
        Load financial data from dbt models.
        
        Returns:
            Tuple of (DataFrame, status_message)
        """
        try:
            # Try to load from fact_financial_monthly first
            query = """
            SELECT * FROM fact_financial_monthly 
            ORDER BY date DESC
            """
            df = self.execute_query(query)
            return df, "Loaded from fact_financial_monthly"
        except Exception as e:
            logger.warning(f"Failed to load from fact_financial_monthly: {e}")
            
            # Fallback to staging table
            try:
                query = """
                SELECT * FROM stg_sales_data 
                ORDER BY date DESC
                """
                df = self.execute_query(query)
                return df, "Loaded from stg_sales_data (fallback)"
            except Exception as e2:
                logger.error(f"Failed to load finance data: {e2}")
                return pd.DataFrame(), f"Error loading finance data: {e2}"
    
    def load_supply_chain_data(self) -> Tuple[pd.DataFrame, str]:
        """
        Load supply chain data from dbt models.
        
        Returns:
            Tuple of (DataFrame, status_message)
        """
        try:
            query = """
            SELECT * FROM stg_supply_chain_data 
            ORDER BY date DESC
            """
            df = self.execute_query(query)
            return df, "Loaded from stg_supply_chain_data"
        except Exception as e:
            logger.error(f"Failed to load supply chain data: {e}")
            return pd.DataFrame(), f"Error loading supply chain data: {e}"
    
    def get_data_quality_metrics(self) -> Dict[str, Any]:
        """
        Get data quality metrics for all tables.
        
        Returns:
            Dictionary with quality metrics
        """
        metrics = {}
        
        if not self.conn:
            if not self.connect():
                return metrics
        
        try:
            if self.conn is None:
                return metrics
            tables = self.get_available_tables()
            
            for table in tables:
                try:
                    # Get row count
                    count_query = f"SELECT COUNT(*) as count FROM {table}"
                    count = self.conn.execute(count_query).fetchdf()
                    
                    # Get null counts for each column
                    schema = self.conn.execute(f"DESCRIBE {table}").fetchdf()
                    null_counts = {}
                    
                    for col in schema['column_name']:
                        null_query = f"SELECT COUNT(*) as null_count FROM {table} WHERE {col} IS NULL"
                        null_count = self.conn.execute(null_query).fetchdf()
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


@st.cache_resource
def get_data_connector() -> DBTDataConnector:
    """
    Get a cached data connector instance.
    
    Returns:
        DBTDataConnector instance
    """
    return DBTDataConnector()


def check_dbt_availability() -> Dict[str, Any]:
    """
    Check if dbt data is available and provide status information.
    
    Returns:
        Dictionary with availability status and information
    """
    connector = get_data_connector()
    
    if not connector.connect():
        return {
            'available': False,
            'message': 'Database not found or cannot connect',
            'db_path': connector.db_path,
            'deployment_note': 'For Streamlit Cloud deployment, ensure the database file is included in the repository.'
        }
    
    try:
        tables = connector.get_available_tables()
        
        # Check for key dbt models
        key_models = ['fact_esg_monthly', 'fact_financial_monthly', 'stg_sales_data', 'stg_esg_data']
        available_models = [model for model in key_models if model in tables]
        
        return {
            'available': len(available_models) > 0,
            'message': f"Found {len(available_models)}/{len(key_models)} key models",
            'available_tables': tables,
            'key_models_found': available_models,
            'key_models_missing': [model for model in key_models if model not in tables],
            'db_path': connector.db_path,
            'deployment_note': 'Database connection successful!'
        }
    except Exception as e:
        return {
            'available': False,
            'message': f'Error checking availability: {e}',
            'db_path': connector.db_path,
            'deployment_note': 'Error occurred while checking database availability.'
        }
    finally:
        connector.disconnect()


def initialize_sample_data_if_needed():
    """
    Initialize sample data if dbt data is not available.
    This is useful for development and demonstration purposes.
    """
    connector = get_data_connector()
    
    if not connector.connect():
        logger.info("Database not available, skipping sample data initialization")
        return
    
    try:
        tables = connector.get_available_tables()
        
        # If no tables exist, we might need to run dbt
        if not tables:
            logger.info("No tables found in database. Please run 'dbt run' to populate the database.")
            return
            
    except Exception as e:
        logger.error(f"Error checking tables: {e}")
    finally:
        connector.disconnect() 