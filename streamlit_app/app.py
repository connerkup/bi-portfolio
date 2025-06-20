"""
PackagingCo ESG & Finance Insights Dashboard - Main App

This is the main entry point for the Streamlit application.
It handles page configuration, data loading, and sidebar filters.
The actual pages are located in the `pages/` directory.
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from packagingco_insights.utils import (
    load_esg_data, load_finance_data, load_sales_data,
    load_csv_data
)

# Page configuration
st.set_page_config(
    page_title="EcoMetrics",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a cleaner, responsive look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #fafafa;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #b0bec5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .kpi-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        justify-content: center;
    }
    .metric-card {
        background-color: #23272f;
        color: #fff;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 5px solid #90caf9;
        flex: 1 1 200px; /* Flex-grow, flex-shrink, flex-basis */
        min-width: 200px;
        max-width: 300px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .insight-box {
        background-color: #263238;
        color: #fff;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 5px solid #ffb300;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stApp {
        background-color: #181a20;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_all_data():
    """Load all required data from dbt models and raw CSVs with caching."""
    try:
        esg_data = load_esg_data()
        finance_data = load_finance_data()
        sales_data = load_sales_data()
        raw_esg = load_csv_data("data/raw/sample_esg_data.csv")
        raw_sales = load_csv_data("data/raw/sample_sales_data.csv")
        
        # Minor data cleaning to prevent pyarrow issues
        if sales_data.index.name is None:
            sales_data.index.name = "index"
        
        # Convert all date/datetime columns to a consistent type
        for df in [esg_data, finance_data, sales_data, raw_esg, raw_sales]:
             if df is not None:
                for col in df.columns:
                    if 'date' in col.lower():
                        df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return esg_data, finance_data, sales_data, raw_esg, raw_sales
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None

def main():
    """
    Main app function.
    - Sets up sidebar filters.
    - Loads and filters data.
    - Stores filtered data in session state for pages to use.
    """
    st.sidebar.title("🎛️ Dashboard Controls")
    
    esg_data, finance_data, sales_data, raw_esg_data, raw_sales_data = load_all_data()
    
    if esg_data is None or finance_data is None or sales_data is None:
        st.error("Failed to load core dashboard data. Please ensure dbt models have been run.")
        st.info("To set up the database, run `dbt run` from the `dbt/` directory.")
        return

    st.sidebar.markdown("### Filters")
    
    # Date range filter
    min_date = esg_data['date'].min().date()
    max_date = esg_data['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    
    # Ensure a valid date range is selected
    if len(date_range) != 2:
        st.warning("Please select a valid start and end date.")
        st.stop()
        
    # Convert date_range to datetime for filtering
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    # Product line filter
    all_product_lines = sorted(esg_data['product_line'].unique())
    
    product_lines = st.sidebar.multiselect(
        "Product Lines",
        options=all_product_lines,
        default=all_product_lines
    )
    
    # Filter data based on selections
    esg_filtered = esg_data[
        (esg_data['date'] >= start_date) & 
        (esg_data['date'] <= end_date) &
        (esg_data['product_line'].isin(product_lines))
    ].copy()

    finance_filtered = finance_data[
        (finance_data['date'] >= start_date) &
        (finance_data['date'] <= end_date) &
        (finance_data['product_line'].isin(product_lines))
    ].copy()

    sales_filtered = sales_data[
        (sales_data['date'] >= start_date) &
        (sales_data['date'] <= end_date) &
        (sales_data['product_line'].isin(product_lines))
    ].copy()

    # Store filtered data in session state for other pages
    st.session_state.filtered_esg = esg_filtered
    st.session_state.filtered_finance = finance_filtered
    st.session_state.filtered_sales = sales_filtered
    st.session_state.raw_esg_data = raw_esg_data
    st.session_state.raw_sales_data = raw_sales_data
    
    st.sidebar.success("Select a dashboard from the list above.")
    st.sidebar.info("The filters on this sidebar control the data displayed on all pages.")

    # Main header
    st.markdown('<h1 class="main-header">🌱 EcoMetrics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">ESG & Financial Intelligence Platform</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 