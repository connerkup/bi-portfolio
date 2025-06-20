import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os
import io

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from packagingco_insights.analysis import ESGAnalyzer, FinanceAnalyzer
from packagingco_insights.utils import (
    create_kpi_card,
    display_charts_responsive
)

def show_overview(esg_data, finance_data, sales_data):
    """Show the overview dashboard."""
    st.markdown("## 📊 Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_revenue = finance_data['total_revenue'].sum()
        create_kpi_card("Total Revenue", total_revenue, format_type="currency")
    
    with col2:
        total_emissions = esg_data['total_emissions_kg_co2'].sum()
        create_kpi_card("Total CO2 Emissions", total_emissions, format_type="number")
        
    with col3:
        avg_recycled = esg_data['avg_recycled_material_pct'].mean()
        create_kpi_card("Avg Recycled Material", avg_recycled, format_type="percentage")

    with col4:
        total_revenue_for_margin = finance_data['total_revenue'].sum()
        if total_revenue_for_margin > 0:
            avg_margin = (finance_data['total_profit_margin'].sum() / total_revenue_for_margin) * 100
        else:
            avg_margin = 0
        create_kpi_card("Avg Profit Margin", avg_margin, format_type="percentage")

    st.markdown("""
    <div class="insight-box" style="margin-top: 2rem;">
        <h4>🎯 Business Question</h4>
        <p><strong>How can PackagingCo drive ESG goals without compromising financial health?</strong></p>
        <p>This dashboard provides insights to answer this critical question through data-driven analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📊 Key Trends")
    
    # Prepare data for charts
    revenue_trends = finance_data.groupby('date')['total_revenue'].sum().reset_index()
    emissions_trends = esg_data.groupby('date')['total_emissions_kg_co2'].sum().reset_index()

    # Create charts
    revenue_fig = px.line(revenue_trends, x='date', y='total_revenue', title="Monthly Revenue Trends", line_shape='spline')
    emissions_fig = px.line(emissions_trends, x='date', y='total_emissions_kg_co2', title="Monthly CO2 Emissions", line_shape='spline')
    
    # Display charts
    display_charts_responsive([revenue_fig, emissions_fig], ["📈 Revenue Trends", "🌱 Emissions Trends"])
    
    # Key insights
    st.markdown("## 💡 Key Insights")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🌱 ESG Performance")
        esg_analyzer = ESGAnalyzer(esg_data)
        insights = esg_analyzer.get_esg_insights()
        for key, insight in insights.items():
            st.markdown(f"**{key.title()}:** {insight}")
            
    with col2:
        st.markdown("### 💰 Financial Performance")
        finance_analyzer = FinanceAnalyzer(finance_data)
        insights = finance_analyzer.get_financial_insights()
        for key, insight in insights.items():
            st.markdown(f"**{key.title()}:** {insight}")

# Page title
st.title("Dashboard Overview")

# You can access the filtered data from session state
if 'filtered_esg' in st.session_state:
    filtered_esg = st.session_state.filtered_esg
    filtered_finance = st.session_state.filtered_finance
    filtered_sales = st.session_state.filtered_sales
    
    if filtered_esg.empty or filtered_finance.empty or filtered_sales.empty:
        st.warning("Please select at least one product line in the main sidebar to view dashboard insights.")
    else:
        show_overview(filtered_esg, filtered_finance, filtered_sales)
else:
    st.warning("Data not loaded. Please go to the main app page and select filters.") 