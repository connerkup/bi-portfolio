import streamlit as st
import pandas as pd
from data_connector import get_data_connector, check_dbt_availability

st.set_page_config(
    page_title="Data Browser - EcoMetrics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Data Browser")
st.markdown("---")

# Check dbt availability
availability = check_dbt_availability()

# Display connection status
if availability['available']:
    st.success(f"✅ {availability['message']}")
    st.info(f"Database: {availability['db_path']}")
else:
    st.error(f"❌ {availability['message']}")
    st.warning("Please ensure dbt pipeline has been run and database is available.")

# Get data connector
connector = get_data_connector()

# Main content
if availability['available']:
    # Create tabs for different data exploration features
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Available Tables", "🔍 Table Explorer", "📊 Data Quality", "🔧 Custom Queries"])
    
    with tab1:
        st.subheader("Available Tables")
        
        try:
            tables = connector.get_available_tables()
            
            if tables:
                # Display tables in a nice format
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**All Tables:**")
                    for table in tables:
                        st.write(f"• {table}")
                
                with col2:
                    st.write("**Key Models:**")
                    key_models = ['fact_esg_monthly', 'fact_financial_monthly', 'stg_sales_data', 'stg_esg_data']
                    for model in key_models:
                        if model in tables:
                            st.write(f"✅ {model}")
                        else:
                            st.write(f"❌ {model}")
            else:
                st.warning("No tables found in database.")
                
        except Exception as e:
            st.error(f"Error loading tables: {e}")
    
    with tab2:
        st.subheader("Table Explorer")
        
        try:
            tables = connector.get_available_tables()
            
            if tables:
                # Table selector
                selected_table = st.selectbox("Select a table to explore:", tables)
                
                if selected_table:
                    # Get table info
                    table_info = connector.get_table_info(selected_table)
                    
                    if table_info:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Table:** {selected_table}")
                            st.write(f"**Rows:** {table_info['row_count']:,}")
                            st.write(f"**Columns:** {len(table_info['columns'])}")
                        
                        with col2:
                            st.write("**Columns:**")
                            for col in table_info['columns']:
                                st.write(f"• {col}")
                        
                        # Show sample data
                        st.subheader("Sample Data")
                        st.dataframe(table_info['sample_data'], use_container_width=True)
                        
                        # Show schema
                        with st.expander("View Schema"):
                            st.dataframe(table_info['schema'], use_container_width=True)
                    else:
                        st.error(f"Could not load information for table: {selected_table}")
            else:
                st.warning("No tables available for exploration.")
                
        except Exception as e:
            st.error(f"Error exploring tables: {e}")
    
    with tab3:
        st.subheader("Data Quality Metrics")
        
        try:
            metrics = connector.get_data_quality_metrics()
            
            if metrics:
                for table_name, table_metrics in metrics.items():
                    with st.expander(f"📊 {table_name}"):
                        if 'error' in table_metrics:
                            st.error(f"Error: {table_metrics['error']}")
                        else:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Total Rows:** {table_metrics['row_count']:,}")
                                st.write(f"**Total Columns:** {len(table_metrics['columns'])}")
                            
                            with col2:
                                # Show null counts
                                null_data = []
                                for col, null_count in table_metrics['null_counts'].items():
                                    null_pct = (null_count / table_metrics['row_count']) * 100 if table_metrics['row_count'] > 0 else 0
                                    null_data.append({
                                        'Column': col,
                                        'Null Count': null_count,
                                        'Null %': f"{null_pct:.2f}%"
                                    })
                                
                                if null_data:
                                    st.write("**Null Values:**")
                                    null_df = pd.DataFrame(null_data)
                                    st.dataframe(null_df, use_container_width=True)
                                else:
                                    st.write("**Null Values:** None found")
            else:
                st.warning("No quality metrics available.")
                
        except Exception as e:
            st.error(f"Error loading quality metrics: {e}")
    
    with tab4:
        st.subheader("Custom Queries")
        
        # Query input
        query = st.text_area(
            "Enter your SQL query:",
            placeholder="SELECT * FROM fact_esg_monthly LIMIT 10",
            height=100
        )
        
        if st.button("Execute Query"):
            if query.strip():
                try:
                    result = connector.query(query)
                    st.success("Query executed successfully!")
                    st.dataframe(result, use_container_width=True)
                    
                    # Show query info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Rows returned:** {len(result):,}")
                    with col2:
                        st.write(f"**Columns:** {len(result.columns)}")
                        
                except Exception as e:
                    st.error(f"Query failed: {e}")
            else:
                st.warning("Please enter a query to execute.")

else:
    # Show helpful information when dbt is not available
    st.markdown("""
    ### Setup Instructions
    
    To connect to your dbt pipeline data, please ensure:
    
    1. **dbt Pipeline is Built**: Run the following commands in the `dbt` directory:
       ```bash
       cd dbt
       dbt deps
       dbt run
       ```
    
    2. **Database File Exists**: The database should be created at `data/processed/portfolio.duckdb`
    
    3. **Raw Data is Available**: Ensure sample data files are in `data/raw/`:
       - `sample_esg_data.csv`
       - `sample_sales_data.csv`
    
    ### Expected Data Structure
    
    After running dbt, you should have access to:
    
    - **Fact Tables**: `fact_esg_monthly`, `fact_financial_monthly`
    - **Staging Tables**: `stg_esg_data`, `stg_sales_data`, `stg_supply_chain_data`
    - **Mart Tables**: `mart_esg_summary`
    
    ### Alternative: Use the Deployment Script
    
    You can also use the automated deployment script:
    ```bash
    cd ecometrics
    python prepare_for_deployment.py
    ```
    """)

# Navigation back to home
if st.button("🏠 Back to Home"):
    st.switch_page("Home.py") 