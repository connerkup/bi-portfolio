import streamlit as st
import pandas as pd
from data_connector import get_data_connector, check_dbt_availability

st.set_page_config(
    page_title="Data Browser - EcoMetrics",
    page_icon="📊"
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
    
    # Show debug information even when models aren't found
    try:
        connector = get_data_connector()
        tables = connector.get_available_tables()
        if tables:
            st.info(f"**Debug Info:** Found {len(tables)} tables in database:")
            for table in tables:
                st.write(f"  - {table}")
        else:
            st.warning("**Debug Info:** No tables found in database.")
    except Exception as e:
        st.error(f"**Debug Error:** {e}")

# Get data connector
connector = get_data_connector()

# Sidebar for table selection and info
if availability['available']:
    with st.sidebar:
        st.subheader("📋 Table Selection")
        
        try:
            tables = connector.get_available_tables()
            
            if tables:
                # Table selector in sidebar
                selected_table = st.selectbox("Select a table to explore:", tables, key="sidebar_table_select")
                
                if selected_table:
                    # Get table info for sidebar display
                    table_info = connector.get_table_info(selected_table)
                    
                    if table_info:
                        st.markdown("---")
                        st.subheader("📊 Table Info")
                        
                        # Table stats
                        st.metric("Rows", f"{table_info['row_count']:,}")
                        st.metric("Columns", len(table_info['columns']))
                        
                        # Key models status
                        st.markdown("---")
                        st.subheader("🔑 Key Models")
                        key_models = ['fact_esg_monthly', 'fact_financial_monthly', 'stg_sales_data', 'stg_esg_data']
                        for model in key_models:
                            if model in tables:
                                st.write(f"✅ {model}")
                            else:
                                st.write(f"❌ {model}")
                        
                        # All tables list (collapsed)
                        with st.expander("📋 All Available Tables"):
                            for table in tables:
                                if table == selected_table:
                                    st.write(f"**▶ {table}** (current)")
                                else:
                                    st.write(f"• {table}")
                    else:
                        st.error(f"Could not load information for table: {selected_table}")
                        selected_table = None
            else:
                st.warning("No tables found in database.")
                selected_table = None
                
        except Exception as e:
            st.error(f"Error loading tables: {e}")
            selected_table = None

# Main content
if availability['available'] and selected_table:
    # Create tabs for different data exploration features (removed Available Tables tab)
    tab1, tab2, tab3 = st.tabs(["🔍 Table Explorer", "📊 Data Quality", "🔧 Custom Queries"])
    
    with tab1:
        st.subheader("Table Explorer")
        
        try:
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
                            st.write(f"**Columns ({len(table_info['columns'])}):**")
                            
                            # Show first few columns, with option to see all
                            show_all_cols = st.checkbox("Show all columns", key=f"show_all_cols_{selected_table}")
                            
                            if show_all_cols or len(table_info['columns']) <= 6:
                                # Show all columns in compact format
                                cols_text = " • ".join(table_info['columns'])
                                st.markdown(f"<small>{cols_text}</small>", unsafe_allow_html=True)
                            else:
                                # Show first 6 columns
                                first_cols = table_info['columns'][:6]
                                remaining_count = len(table_info['columns']) - 6
                                cols_text = " • ".join(first_cols)
                                st.markdown(f"<small>{cols_text} • ... and {remaining_count} more</small>", unsafe_allow_html=True)
                        
                        # Show sample data with dynamic row control
                        st.subheader("Sample Data")
                        
                        # Slider to control number of rows displayed
                        actual_table_rows = table_info['row_count']  # Actual table size
                        available_sample_rows = len(table_info['sample_data'])  # Available sample data
                        max_rows = min(available_sample_rows, 100)  # Cap at 100 for performance
                        
                        if available_sample_rows <= 5:
                            # For small samples, just show all available
                            num_rows = available_sample_rows
                            st.info(f"Showing all {available_sample_rows} available sample rows (table has {actual_table_rows:,} rows total)")
                        else:
                            # For larger samples, use slider
                            num_rows = st.slider(
                                "Number of rows to display:",
                                min_value=min(5, available_sample_rows),
                                max_value=max_rows,
                                value=min(10, max_rows),
                                step=5,
                                key=f"rows_slider_{selected_table}"
                            )
                            st.caption(f"Showing sample from table with {actual_table_rows:,} total rows")
                        
                        st.dataframe(table_info['sample_data'].head(num_rows), use_container_width=True)
                        
                        # Full Data Explorer
                        st.subheader("📊 Full Data Explorer")
                        
                        # Clean 3-stack layout
                        with st.container():
                            # Stack 1: Search
                            search_term = st.text_input(
                                "🔍 Search across all columns:",
                                placeholder="Type to search for text in any column...",
                                key=f"search_{selected_table}",
                                help="Search is case-insensitive and searches all columns"
                            )
                            
                            # Stack 2: Advanced Filters
                            with st.expander("🔍 Advanced Filters", expanded=False):
                                # Get sample data to analyze column types and values
                                sample_for_filters = table_info['sample_data']
                                
                                # Create filters for each column
                                active_filters = {}
                                
                                # Create tabs for different filter types
                                filter_tab1, filter_tab2 = st.tabs(["🎯 Column Filters", "📊 Display Options"])
                                
                                with filter_tab1:
                                    st.caption("Filter data by specific column values:")
                                    
                                    # Create dynamic filters based on column types
                                    filter_cols = st.columns(2)
                                    
                                    for idx, col in enumerate(table_info['columns'][:8]):  # Limit to first 8 columns
                                        with filter_cols[idx % 2]:
                                            col_data = sample_for_filters[col].dropna()
                                            
                                            if len(col_data) > 0:
                                                # Detect column type and create appropriate filter
                                                if col_data.dtype == 'object' or col_data.dtype == 'string':
                                                    # Categorical filter
                                                    unique_vals = sorted(col_data.unique())
                                                    if len(unique_vals) <= 20:  # Only show if reasonable number of options
                                                        selected_vals = st.multiselect(
                                                            f"🏷️ {col}:",
                                                            options=unique_vals,
                                                            key=f"filter_{col}_{selected_table}",
                                                            help=f"Filter by {col} values"
                                                        )
                                                        if selected_vals:
                                                            active_filters[col] = ('IN', selected_vals)
                                                
                                                elif col_data.dtype in ['int64', 'float64', 'int32', 'float32']:
                                                    # Numeric filter
                                                    min_val = float(col_data.min())
                                                    max_val = float(col_data.max())
                                                    
                                                    if min_val != max_val:
                                                        range_vals = st.slider(
                                                            f"📊 {col}:",
                                                            min_value=min_val,
                                                            max_value=max_val,
                                                            value=(min_val, max_val),
                                                            key=f"range_{col}_{selected_table}",
                                                            help=f"Filter {col} by range"
                                                        )
                                                        if range_vals != (min_val, max_val):
                                                            active_filters[col] = ('RANGE', range_vals)
                                                
                                                elif 'date' in col.lower() or 'time' in col.lower():
                                                    # Date filter (simplified)
                                                    try:
                                                        date_col = pd.to_datetime(col_data)
                                                        min_date = date_col.min().date()
                                                        max_date = date_col.max().date()
                                                        
                                                        date_range = st.date_input(
                                                            f"📅 {col}:",
                                                            value=(min_date, max_date),
                                                            key=f"date_{col}_{selected_table}",
                                                            help=f"Filter {col} by date range"
                                                        )
                                                        if len(date_range) == 2 and date_range != (min_date, max_date):
                                                            active_filters[col] = ('DATE_RANGE', date_range)
                                                    except:
                                                        pass  # Skip if date parsing fails
                                    
                                    # Show active filters summary
                                    if active_filters:
                                        st.success(f"🎯 {len(active_filters)} filters active")
                                    else:
                                        st.info("No filters applied - showing all data")
                                
                                with filter_tab2:
                                    st.caption("Choose which columns to display:")
                                    
                                    col_select_all = st.checkbox("Select All Columns", key=f"select_all_{selected_table}")
                                    
                                    if col_select_all:
                                        selected_columns = table_info['columns']
                                    else:
                                        selected_columns = st.multiselect(
                                            "Choose columns:",
                                            options=table_info['columns'],
                                            default=table_info['columns'][:6],  # Show first 6 by default
                                            key=f"cols_{selected_table}",
                                            help="Select which columns to display in the table"
                                        )
                                    
                                    st.caption(f"Selected: {len(selected_columns)} of {len(table_info['columns'])} columns")
                            
                            # Stack 3: Page controls - two column layout
                            control_col1, control_col2 = st.columns(2)
                            
                            with control_col2:
                                rows_per_page = st.selectbox(
                                    "📄 Rows per page:",
                                    options=[10, 25, 50, 100],
                                    index=1,  # Default to 25
                                    key=f"rows_per_page_{selected_table}"
                                )
                        
                        # Get full data with pagination
                        try:
                            # Calculate pagination - ensure we're working with Python ints
                            actual_table_rows = int(actual_table_rows)
                            rows_per_page = int(rows_per_page)
                            total_pages = max(1, (actual_table_rows + rows_per_page - 1) // rows_per_page)
                            
                            # Page selector in first column of stack 3
                            with control_col1:
                                if total_pages > 1:
                                    current_page = st.number_input(
                                        f"📖 Page (1-{total_pages:,}):",
                                        min_value=1,
                                        max_value=total_pages,
                                        value=1,
                                        key=f"page_{selected_table}",
                                        help=f"Navigate through {total_pages:,} pages of data"
                                    )
                                else:
                                    current_page = 1
                                    st.info("📖 Single page of data")
                            
                            # Calculate offset
                            offset = (current_page - 1) * rows_per_page
                            
                            # Build query for full data
                            query_parts = []
                            query_parts.append(f"SELECT")
                            
                            if selected_columns:
                                query_parts.append(", ".join([f'"{col}"' for col in selected_columns]))
                            else:
                                query_parts.append("*")
                            
                            query_parts.append(f'FROM "{selected_table}"')
                            
                            # Build WHERE clause with both search and advanced filters
                            where_conditions = []
                            
                            # Add search filter if provided
                            if search_term:
                                search_conditions = []
                                for col in table_info['columns']:
                                    search_conditions.append(f'CAST("{col}" AS VARCHAR) ILIKE \'%{search_term}%\'')
                                where_conditions.append(f"({' OR '.join(search_conditions)})")
                            
                            # Add advanced filters
                            for col, (filter_type, filter_value) in active_filters.items():
                                if filter_type == 'IN':
                                    # Categorical filter
                                    quoted_values = [f"'{val}'" for val in filter_value]
                                    where_conditions.append(f'"{col}" IN ({", ".join(quoted_values)})')
                                
                                elif filter_type == 'RANGE':
                                    # Numeric range filter
                                    min_val, max_val = filter_value
                                    where_conditions.append(f'"{col}" BETWEEN {min_val} AND {max_val}')
                                
                                elif filter_type == 'DATE_RANGE':
                                    # Date range filter
                                    start_date, end_date = filter_value
                                    where_conditions.append(f'"{col}" BETWEEN \'{start_date}\' AND \'{end_date}\'')
                            
                            # Add WHERE clause if any conditions exist
                            if where_conditions:
                                query_parts.append(f"WHERE {' AND '.join(where_conditions)}")
                            
                            query_parts.append(f"LIMIT {rows_per_page} OFFSET {offset}")
                            
                            full_query = " ".join(query_parts)
                            
                            # Execute query
                            full_data = connector.query(full_query)
                            
                            # Show results info
                            result_count = len(full_data)
                            if search_term:
                                # Get total matching results for search
                                count_query = full_query.replace(
                                    f"LIMIT {rows_per_page} OFFSET {offset}", 
                                    ""
                                ).replace(
                                    ", ".join([f'"{col}"' for col in selected_columns]) if selected_columns else "*",
                                    "COUNT(*) as total"
                                )
                                try:
                                    total_matching = connector.query(count_query).iloc[0]['total']
                                    st.info(f"📊 Showing {result_count} of {total_matching:,} matching rows (page {current_page} of {max(1, (total_matching + rows_per_page - 1) // rows_per_page)})")
                                except:
                                    st.info(f"📊 Showing {result_count} results for '{search_term}' (page {current_page})")
                            else:
                                start_row = offset + 1
                                end_row = min(offset + result_count, actual_table_rows)
                                st.info(f"📊 Showing rows {start_row:,}-{end_row:,} of {actual_table_rows:,} total (page {current_page} of {total_pages})")
                            
                            # Display the data
                            if not full_data.empty:
                                st.dataframe(
                                    full_data, 
                                    use_container_width=True,
                                    height=400  # Fixed height for better scrolling
                                )
                                
                                # Simple navigation info - no buttons to avoid session state conflicts
                                if total_pages > 1:
                                    nav_info_col1, nav_info_col2, nav_info_col3 = st.columns([1, 2, 1])
                                    
                                    with nav_info_col1:
                                        if current_page > 1:
                                            st.caption("⬅️ Use page input above to navigate")
                                    
                                    with nav_info_col2:
                                        st.caption(f"📖 Page {current_page:,} of {total_pages:,}")
                                    
                                    with nav_info_col3:
                                        if current_page < total_pages:
                                            st.caption("Use page input above to navigate ➡️")
                                
                            else:
                                st.warning("No data found matching your criteria.")
                                
                        except Exception as e:
                            st.error(f"Error loading full data: {e}")
                            st.code(full_query)  # Show the query for debugging
                        
                        # Show schema
                        with st.expander("View Schema"):
                            st.dataframe(table_info['schema'], use_container_width=True)
                    else:
                        st.error(f"Could not load information for table: {selected_table}")
            else:
                st.warning("No tables available for exploration.")
                
        except Exception as e:
            st.error(f"Error exploring tables: {e}")
    
    with tab2:
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
    
    with tab3:
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