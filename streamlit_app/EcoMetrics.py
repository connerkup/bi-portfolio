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
import warnings
import plotly.express as px

# Suppress PyArrow warnings
warnings.filterwarnings('ignore', category=UserWarning, module='pyarrow')

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from packagingco_insights.utils import (
    load_esg_data, load_finance_data, load_sales_data,
    load_csv_data
)

# Import shared controls
from components.shared_controls import setup_sidebar_controls

def safe_dataframe_display(df, **kwargs):
    """Safely display a DataFrame with PyArrow compatibility fixes."""
    if df is None or df.empty:
        st.warning("No data to display")
        return
    
    try:
        # Create a copy to avoid modifying the original
        display_df = df.copy()
        
        # Reset index to avoid index-related issues
        display_df.reset_index(drop=True, inplace=True)
        
        # Convert object columns to string
        for col in display_df.columns:
            if display_df[col].dtype == 'object':
                display_df[col] = display_df[col].fillna('').astype(str)
        
        # Display the cleaned DataFrame
        st.dataframe(display_df, **kwargs)
        
    except Exception as e:
        st.error(f"Error displaying data: {e}")
        # Fallback: display basic info
        st.write(f"DataFrame shape: {df.shape}")
        st.write(f"Columns: {list(df.columns)}")

# Page configuration - simplified to fix sidebar issues
st.set_page_config(
    page_title="EcoMetrics",
    page_icon="🌱",
    layout="wide"
)

@st.cache_data
def load_all_data():
    """Load all required data from dbt models and raw CSVs with caching."""
    try:
        # Use the correct database path - point to the main project's data directory
        db_path = "../data/processed/portfolio.duckdb"
        
        # Load data with source indicators
        esg_data, esg_source = load_esg_data(db_path)
        finance_data, finance_source = load_finance_data(db_path)
        sales_data, sales_source = load_sales_data(db_path)
        raw_esg = load_csv_data("../data/raw/sample_esg_data.csv")
        raw_sales = load_csv_data("../data/raw/sample_sales_data.csv")
        
        # Enhanced data cleaning to prevent pyarrow issues
        for df in [esg_data, finance_data, sales_data, raw_esg, raw_sales]:
            if df is not None:
                # Reset index to avoid index-related issues
                df.reset_index(drop=True, inplace=True)
                
                # Convert all date/datetime columns to a consistent type
                for col in df.columns:
                    if 'date' in col.lower():
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                
                # Convert object columns to string to avoid PyArrow issues
                for col in df.columns:
                    if df[col].dtype == 'object':
                        # Try to convert to string, but handle mixed types carefully
                        try:
                            df[col] = df[col].astype(str)
                        except:
                            # If conversion fails, replace problematic values
                            df[col] = df[col].fillna('').astype(str)
                
                # Ensure numeric columns are properly typed
                for col in df.columns:
                    if df[col].dtype in ['int64', 'float64']:
                        # Convert to float64 for better compatibility
                        df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return esg_data, finance_data, sales_data, raw_esg, raw_sales, esg_source, finance_source, sales_source
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.session_state.raw_esg_data = None
        st.session_state.raw_sales_data = None
        return None, None, None, None, None, "error", "error", "error"

# Load data once and store in session state
if 'esg_data_full' not in st.session_state:
    (
        st.session_state.esg_data_full,
        st.session_state.finance_data_full,
        st.session_state.sales_data_full,
        st.session_state.raw_esg_data,
        st.session_state.raw_sales_data,
        st.session_state.esg_source,
        st.session_state.finance_source,
        st.session_state.sales_source,
    ) = load_all_data()

# Check if data is loaded successfully
if st.session_state.get('esg_data_full') is None:
    st.error("Failed to load core dashboard data.")
    st.info("The app will attempt to use sample data instead.")
    st.stop()

# Setup sidebar controls globally for all pages
setup_sidebar_controls()

# Main page content
st.title("🌱 EcoMetrics")
st.markdown("ESG & Financial Intelligence Platform")

# Display data source indicators
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Sources")

# Create data source indicators with appropriate styling
if st.session_state.get('esg_source') == 'dbt_models':
    st.sidebar.success("🌱 ESG Data: dbt Models")
elif st.session_state.get('esg_source') == 'sample_csv':
    st.sidebar.info("🌱 ESG Data: Sample CSV")
else:
    st.sidebar.warning("🌱 ESG Data: Generated Sample")

if st.session_state.get('finance_source') == 'dbt_models':
    st.sidebar.success("💰 Finance Data: dbt Models")
elif st.session_state.get('finance_source') == 'sample_csv':
    st.sidebar.info("💰 Finance Data: Sample CSV")
else:
    st.sidebar.warning("💰 Finance Data: Generated Sample")

if st.session_state.get('sales_source') == 'dbt_models':
    st.sidebar.success("📈 Sales Data: dbt Models")
elif st.session_state.get('sales_source') == 'sample_csv':
    st.sidebar.info("📈 Sales Data: Sample CSV")
else:
    st.sidebar.warning("📈 Sales Data: Generated Sample")

# Show comprehensive overview content
st.markdown("## 📊 Executive Summary")
st.markdown("Welcome to EcoMetrics - your comprehensive ESG & Financial Intelligence Platform.")

# Display basic metrics if data is available
if 'filtered_esg' in st.session_state and 'filtered_finance' in st.session_state:
    esg_data = st.session_state.filtered_esg
    finance_data = st.session_state.filtered_finance
    
    if not esg_data.empty and not finance_data.empty:
        # Create metrics data
        total_revenue = finance_data['total_revenue'].sum()
        total_emissions = esg_data['total_emissions_kg_co2'].sum()
        avg_recycled = esg_data['avg_recycled_material_pct'].mean()
        
        if total_revenue > 0:
            avg_margin = (finance_data['total_profit_margin'].sum() / total_revenue) * 100
        else:
            avg_margin = 0
        
        # Display metrics using simple columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Revenue", f"${total_revenue:,.0f}")
        with col2:
            st.metric("Total CO2 Emissions", f"{total_emissions:,.0f} kg")
        with col3:
            st.metric("Avg Recycled Material", f"{avg_recycled:.1f}%")
        with col4:
            st.metric("Avg Profit Margin", f"{avg_margin:.1f}%")

        st.markdown("""
        ### 🎯 Business Question
        **How can PackagingCo drive ESG goals without compromising financial health?**
        
        This dashboard provides insights to answer this critical question through data-driven analysis.
        """)
        
        st.subheader("📊 Key Trends")
        
        # Prepare data for charts
        revenue_trends = finance_data.groupby('date')['total_revenue'].sum().reset_index()
        emissions_trends = esg_data.groupby('date')['total_emissions_kg_co2'].sum().reset_index()

        # Create charts
        revenue_fig = px.line(revenue_trends, x='date', y='total_revenue', title="Monthly Revenue Trends", line_shape='spline')
        st.plotly_chart(revenue_fig, use_container_width=True)
        
        emissions_fig = px.line(emissions_trends, x='date', y='total_emissions_kg_co2', title="Monthly CO2 Emissions", line_shape='spline')
        st.plotly_chart(emissions_fig, use_container_width=True)
        
        # Key insights
        st.markdown("## 💡 Key Insights")
        
        # Use simple columns for insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌱 ESG Performance")
            # Simple ESG insights
            st.markdown(f"**Total Emissions:** {total_emissions:,.0f} kg CO2")
            st.markdown(f"**Avg Recycled Material:** {avg_recycled:.1f}%")
            st.markdown(f"**Avg Energy Efficiency:** {esg_data['avg_efficiency_rating'].mean():.1f}/10")
            st.markdown(f"**Avg Quality Score:** {esg_data['avg_quality_score'].mean():.1f}/10")
            
        with col2:
            st.markdown("### 💰 Financial Performance")
            # Simple financial insights
            st.markdown(f"**Total Revenue:** ${total_revenue:,.0f}")
            st.markdown(f"**Avg Profit Margin:** {avg_margin:.1f}%")
            st.markdown(f"**Revenue Growth:** {((revenue_trends['total_revenue'].iloc[-1] / revenue_trends['total_revenue'].iloc[0]) - 1) * 100:.1f}%")
            st.markdown(f"**Avg Monthly Revenue:** ${revenue_trends['total_revenue'].mean():,.0f}")
    else:
        st.warning("Please select filters in the sidebar to view dashboard insights.")
else:
    st.info("Data is being loaded. Please wait...") 