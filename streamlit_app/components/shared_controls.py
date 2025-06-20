"""
Shared controls for the EcoMetrics dashboard.
This module provides sidebar controls that are available across all pages.
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add the project root to the path to allow importing from 'streamlit_app'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from packagingco_insights.utils.data_loader import (
    load_esg_data, load_finance_data, load_sales_data,
    load_csv_data
)

def setup_sidebar_controls():
    """Renders the dashboard controls in the sidebar for all pages."""
    with st.sidebar:
        st.title("🎛️ Dashboard Controls")
        st.markdown("### Filters")

        esg_data = st.session_state.get('esg_data_full')
        finance_data = st.session_state.get('finance_data_full')
        sales_data = st.session_state.get('sales_data_full')

        if esg_data is not None and finance_data is not None and sales_data is not None:
            # Date range filter - restore from session state or use defaults
            min_date = esg_data['date'].min().date()
            max_date = esg_data['date'].max().date()
            
            # Get stored date range or use defaults
            stored_date_range = st.session_state.get('date_range', (min_date, max_date))
            
            date_range = st.date_input(
                "Date Range",
                value=stored_date_range,
                min_value=min_date,
                max_value=max_date,
                key="date_range_input"
            )
            
            # Store the selected date range in session state
            st.session_state.date_range = date_range

            if len(date_range) == 2:
                start_date = pd.to_datetime(date_range[0])
                end_date = pd.to_datetime(date_range[1])

                # Product line filter - use checkboxes to avoid flashing
                all_product_lines = sorted(esg_data['product_line'].unique())
                
                # Initialize product lines in session state if not present
                if 'selected_product_lines' not in st.session_state:
                    st.session_state.selected_product_lines = all_product_lines
                
                # Ensure stored product lines are still valid
                current_stored = st.session_state.selected_product_lines
                valid_stored_lines = [line for line in current_stored if line in all_product_lines]
                if not valid_stored_lines:
                    valid_stored_lines = all_product_lines
                    st.session_state.selected_product_lines = valid_stored_lines
                
                st.markdown("**Product Lines:**")
                
                # Use checkboxes instead of multiselect to avoid flashing
                selected_lines = []
                for product_line in all_product_lines:
                    is_selected = product_line in valid_stored_lines
                    if st.checkbox(
                        product_line, 
                        value=is_selected, 
                        key=f"checkbox_{product_line.replace(' ', '_')}"
                    ):
                        selected_lines.append(product_line)
                
                # Update session state if selection changed
                if set(selected_lines) != set(st.session_state.selected_product_lines):
                    st.session_state.selected_product_lines = selected_lines

                # Filter data based on selections
                filtered_esg = esg_data[
                    (esg_data['date'] >= start_date) &
                    (esg_data['date'] <= end_date) &
                    (esg_data['product_line'].isin(selected_lines))
                ].copy()
                
                filtered_finance = finance_data[
                    (finance_data['date'] >= start_date) &
                    (finance_data['date'] <= end_date) &
                    (finance_data['product_line'].isin(selected_lines))
                ].copy()
                
                filtered_sales = sales_data[
                    (sales_data['date'] >= start_date) &
                    (sales_data['date'] <= end_date) &
                    (sales_data['product_line'].isin(selected_lines))
                ].copy()
                
                # Ensure filtered data is PyArrow compatible
                for df in [filtered_esg, filtered_finance, filtered_sales]:
                    if df is not None and not df.empty:
                        df.reset_index(drop=True, inplace=True)
                        # Convert object columns to string
                        for col in df.columns:
                            if df[col].dtype == 'object':
                                df[col] = df[col].fillna('').astype(str)
                
                st.session_state.filtered_esg = filtered_esg
                st.session_state.filtered_finance = filtered_finance
                st.session_state.filtered_sales = filtered_sales
                
                # Store filter metadata for debugging/display
                st.session_state.active_filters = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'product_lines': selected_lines,
                    'total_records_esg': len(filtered_esg),
                    'total_records_finance': len(filtered_finance),
                    'total_records_sales': len(filtered_sales)
                }
            else:
                st.warning("Please select a valid start and end date.")
        else:
            st.warning("Data not fully loaded. Please check data sources.")
        
        # Display current filter status
        if 'active_filters' in st.session_state:
            st.markdown("### 🔍 Active Filters")
            filters = st.session_state.active_filters
            st.info(f"📅 Date Range: {filters['start_date'].strftime('%Y-%m-%d')} to {filters['end_date'].strftime('%Y-%m-%d')}")
            st.info(f"📦 Product Lines: {len(filters['product_lines'])} selected")
            st.info(f"📊 Records: ESG({filters['total_records_esg']}) | Finance({filters['total_records_finance']}) | Sales({filters['total_records_sales']})")
        
        st.success("Select a dashboard from the list above.")
        st.info("The filters on this sidebar control the data displayed on all pages.")
        
        # Add a reset filters button
        if st.button("🔄 Reset Filters", key="reset_filters"):
            # Clear stored filter state
            if 'date_range' in st.session_state:
                del st.session_state.date_range
            if 'selected_product_lines' in st.session_state:
                del st.session_state.selected_product_lines
            if 'active_filters' in st.session_state:
                del st.session_state.active_filters
            if 'filtered_esg' in st.session_state:
                del st.session_state.filtered_esg
            if 'filtered_finance' in st.session_state:
                del st.session_state.filtered_finance
            if 'filtered_sales' in st.session_state:
                del st.session_state.filtered_sales
            # Clear checkbox states
            for product_line in all_product_lines:
                checkbox_key = f"checkbox_{product_line.replace(' ', '_')}"
                if checkbox_key in st.session_state:
                    del st.session_state[checkbox_key]
            st.rerun() 