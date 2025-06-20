"""
Data Browser Page

This page provides interactive data exploration capabilities for all datasets.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
import io

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def main():
    """Data Browser page main function."""
    
    # Check if data is available in session state
    if 'filtered_esg' not in st.session_state or 'filtered_finance' not in st.session_state or 'filtered_sales' not in st.session_state:
        st.error("No data available. Please return to the main page to load data.")
        st.info("The main page loads and filters the data for all pages.")
        return
    
    esg_data = st.session_state.filtered_esg
    finance_data = st.session_state.filtered_finance
    sales_data = st.session_state.filtered_sales
    raw_esg_data = st.session_state.get('raw_esg_data', None)
    raw_sales_data = st.session_state.get('raw_sales_data', None)
    
    st.markdown("## 📋 Data Browser")
    st.markdown("Explore the underlying data used in the dashboard with filtering and sorting capabilities.")
    
    datasets = {
        "🌱 ESG Data (Processed)": esg_data,
        "💰 Financial Data (Processed)": finance_data,
        "📈 Sales Data (Processed)": sales_data,
    }
    
    # Add raw data if available
    if raw_esg_data is not None:
        datasets["📄 Raw ESG Data"] = raw_esg_data
    if raw_sales_data is not None:
        datasets["📄 Raw Sales Data"] = raw_sales_data
    
    selected_dataset = st.selectbox("Select Dataset to Browse", list(datasets.keys()))
    df = datasets[selected_dataset]
    
    if df is not None and not df.empty:
        st.markdown(f"### {selected_dataset}")
        
        st.subheader("📊 Dataset Information")
        st.metric("Total Rows", len(df))
        st.metric("Total Columns", len(df.columns))
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        st.metric("Missing Data %", f"{missing_pct:.1f}%")
        st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        st.markdown("#### Data Overview")
        tab1, tab2, tab3 = st.tabs(["📊 Sample Data", "📈 Statistics", "🔍 Data Info"])
        
        with tab1:
            st.markdown("**First 10 rows of data:**")
            st.dataframe(df.head(10), use_container_width=True)
        
        with tab2:
            st.markdown("**Numeric Column Statistics:**")
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                st.dataframe(df[numeric_cols].describe(), use_container_width=True)
            else:
                st.info("No numeric columns found in this dataset.")
        
        with tab3:
            st.markdown("**Dataset Information:**")
            buffer = io.StringIO()
            df.info(buf=buffer, max_cols=None, memory_usage=True, show_counts=True)
            st.text(buffer.getvalue())
        
        st.markdown("#### Column Selection")
        selected_columns = st.multiselect(
            "Select columns to display", 
            df.columns.tolist(), 
            default=df.columns.tolist()[:min(8, len(df.columns))]
        )
        
        if selected_columns:
            display_df = df[selected_columns].copy()
            
            st.markdown("#### Search & Filter")
            search_term = st.text_input("Search across all columns (case-insensitive)", placeholder="Enter search term...")
            if search_term:
                mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                display_df = display_df[mask]
                st.info(f"Found {len(display_df)} rows matching '{search_term}'")
            
            st.markdown("#### Column Filters")
            for col in selected_columns:
                if display_df[col].dtype in ['object', 'string']:
                    unique_vals = display_df[col].dropna().unique()
                    if len(unique_vals) <= 20:
                        selected_vals = st.multiselect(f"Filter {col}", options=sorted(unique_vals), default=sorted(unique_vals))
                        if selected_vals:
                            display_df = display_df[display_df[col].isin(selected_vals)]
                elif display_df[col].dtype in ['int64', 'float64']:
                    min_val = display_df[col].min()
                    max_val = display_df[col].max()
                    if pd.notna(min_val) and pd.notna(max_val):
                        # Check if min and max are different to avoid slider error
                        if min_val < max_val:
                            range_vals = st.slider(f"Range {col}", min_value=float(min_val), max_value=float(max_val), value=(float(min_val), float(max_val)))
                            display_df = display_df[(display_df[col] >= range_vals[0]) & (display_df[col] <= range_vals[1])]
                        else:
                            # If all values are the same, show the value and skip filtering
                            st.info(f"Column '{col}' has only one value: {min_val}")
            
            st.markdown("#### Pagination")
            rows_per_page = st.selectbox("Rows per page", [10, 25, 50, 100, 500])
            total_pages = (len(display_df) + rows_per_page - 1) // rows_per_page
            current_page = st.selectbox("Page", range(1, total_pages + 1), index=0)
            start_idx = (current_page - 1) * rows_per_page
            end_idx = start_idx + rows_per_page
            
            st.markdown("#### Data Table")
            st.markdown(f"Showing rows {start_idx + 1}-{min(end_idx, len(display_df))} of {len(display_df)} total rows")
            st.dataframe(display_df.iloc[start_idx:end_idx], use_container_width=True, height=400)
            
            st.markdown("#### Export Data")
            csv_data = display_df.to_csv(index=False)
            st.download_button(
                label="Download filtered data as CSV", 
                data=csv_data, 
                file_name=f"{selected_dataset.replace(' ', '_').lower()}_filtered.csv", 
                mime="text/csv"
            )
            
            st.markdown("#### Data Quality Insights")
            st.markdown("**Missing Values by Column:**")
            missing_data = display_df.isnull().sum()
            missing_data = missing_data[missing_data > 0]
            if not missing_data.empty:
                st.write(missing_data)
            else:
                st.write("No missing values found!")
            
            st.markdown("**Data Types:**")
            dtype_info = display_df.dtypes.value_counts()
            st.write(dtype_info)
        else:
            st.warning("Please select at least one column to display.")
    else:
        st.error(f"No data available for {selected_dataset}")
        st.info("Please ensure the database is properly set up by running 'dbt run' in the dbt directory.")

if __name__ == "__main__":
    main() 