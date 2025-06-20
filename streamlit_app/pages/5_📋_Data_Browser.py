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

# Add the project root to the path to allow importing from 'streamlit_app'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import shared controls
from components.shared_controls import setup_sidebar_controls

# Setup sidebar controls
setup_sidebar_controls()

# Check for data availability
if 'filtered_esg' not in st.session_state or 'filtered_finance' not in st.session_state or 'filtered_sales' not in st.session_state:
    st.warning("Data is being filtered, please wait...")
    st.info("Please return to the main page to load and filter data.")
else:
    # Page content
    esg_data = st.session_state.filtered_esg
    finance_data = st.session_state.filtered_finance
    sales_data = st.session_state.filtered_sales
    
    if esg_data.empty and finance_data.empty and sales_data.empty:
        st.warning("No data available for the selected filters.")
        st.info("Please adjust the filters in the sidebar.")
    else:
        # Data browser content
        st.markdown("## 📋 Data Browser")
        st.markdown("Explore the underlying data used in the dashboard with filtering and sorting capabilities.")

        # Dataset selection
        datasets = {
            "ESG Data": esg_data if not esg_data.empty else None,
            "Financial Data": finance_data if not finance_data.empty else None,
            "Sales Data": sales_data if not sales_data.empty else None
        }
        
        # Filter out empty datasets
        available_datasets = {k: v for k, v in datasets.items() if v is not None}
        
        if not available_datasets:
            st.warning("No datasets available for the selected filters.")
        else:
            selected_dataset = st.selectbox("Select Dataset", list(available_datasets.keys()))
            current_data = available_datasets[selected_dataset]
            
            st.markdown(f"### {selected_dataset}")
            
            # Basic data info
            st.markdown("#### Data Overview")
            st.write(f"**Shape:** {current_data.shape[0]} rows × {current_data.shape[1]} columns")
            st.write(f"**Date Range:** {current_data['date'].min().strftime('%Y-%m-%d')} to {current_data['date'].max().strftime('%Y-%m-%d')}")
            
            st.markdown("**First 10 rows of data:**")
            st.dataframe(current_data.head(10), use_container_width=True)
            
            # Numeric statistics
            numeric_cols = current_data.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                st.markdown("**Numeric Column Statistics:**")
                st.dataframe(current_data[numeric_cols].describe(), use_container_width=True)
            
            # Dataset info
            st.markdown("**Dataset Information:**")
            st.dataframe(current_data.info(), use_container_width=True)
            
            # Column selection
            st.markdown("#### Column Selection")
            selected_columns = st.multiselect(
                "Select columns to display",
                current_data.columns.tolist(),
                default=current_data.columns.tolist()
            )
            
            if selected_columns:
                display_data = current_data[selected_columns]
                
                # Search functionality
                st.markdown("#### Search & Filter")
                search_term = st.text_input("Search in data (searches all columns)", "")
                
                if search_term:
                    # Create a mask for rows containing the search term
                    mask = display_data.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                    display_data = display_data[mask]
                
                # Column filters
                st.markdown("#### Column Filters")
                filter_cols = st.multiselect("Select columns to filter by", selected_columns)
                
                for col in filter_cols:
                    if col in display_data.columns:
                        unique_vals = sorted(display_data[col].unique())
                        if len(unique_vals) <= 20:  # Only show filter if reasonable number of options
                            selected_vals = st.multiselect(f"Filter {col}", unique_vals, default=unique_vals)
                            if selected_vals:
                                display_data = display_data[display_data[col].isin(selected_vals)]
                
                # Pagination
                st.markdown("#### Pagination")
                rows_per_page = st.selectbox("Rows per page", [10, 25, 50, 100], index=0)
                
                total_rows = len(display_data)
                total_pages = (total_rows + rows_per_page - 1) // rows_per_page
                
                if total_pages > 1:
                    page = st.selectbox("Page", range(1, total_pages + 1), index=0)
                    start_idx = (page - 1) * rows_per_page
                    end_idx = start_idx + rows_per_page
                else:
                    start_idx = 0
                    end_idx = total_rows
                
                # Display data
                st.markdown("#### Data Table")
                st.markdown(f"Showing rows {start_idx + 1}-{min(end_idx, len(display_data))} of {len(display_data)} total rows")
                
                st.dataframe(display_data.iloc[start_idx:end_idx], use_container_width=True)
                
                # Export functionality
                st.markdown("#### Export Data")
                csv = display_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{selected_dataset.lower().replace(' ', '_')}_data.csv",
                    mime="text/csv"
                )
                
                # Data quality insights
                st.markdown("#### Data Quality Insights")
                
                # Missing values
                st.markdown("**Missing Values by Column:**")
                missing_data = display_data.isnull().sum()
                if missing_data.sum() > 0:
                    st.dataframe(missing_data[missing_data > 0], use_container_width=True)
                else:
                    st.success("No missing values found!")
                
                # Data types
                st.markdown("**Data Types:**")
                dtype_data = display_data.dtypes.to_frame('Data Type')
                st.dataframe(dtype_data, use_container_width=True) 