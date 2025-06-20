"""
Financial Analysis Page

This page provides detailed financial insights and analysis for PackagingCo.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add the project root to the path to allow importing from 'streamlit_app'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from packagingco_insights.analysis.finance_analysis import FinanceAnalyzer

# Import shared controls
from components.shared_controls import setup_sidebar_controls

def show_financial_analysis(finance_data):
    """Renders the financial analysis page."""
    st.markdown("## 💰 Financial Performance Analysis")
    st.markdown(
        "Analyze key financial metrics and trends. "
        "Use the filters in the sidebar to drill down into specific product lines or time periods."
    )

    analyzer = FinanceAnalyzer(finance_data)
    insights = analyzer.get_financial_insights()

    # Calculate summary metrics
    total_revenue = finance_data['total_revenue'].sum()
    total_profit = finance_data['total_profit_margin'].sum()
    avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Calculate revenue growth
    revenue_trends = finance_data.groupby('date')['total_revenue'].sum().reset_index()
    if len(revenue_trends) > 1:
        revenue_growth = ((revenue_trends['total_revenue'].iloc[-1] / revenue_trends['total_revenue'].iloc[0]) - 1) * 100
    else:
        revenue_growth = 0

    # Create simple columns for KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue", 
            f"${total_revenue:,.0f}"
        )
    with col2:
        st.metric(
            "Total Profit Margin", 
            f"${total_profit:,.0f}"
        )
    with col3:
        st.metric(
            "Avg Profit Margin (%)",
            f"{avg_margin:.2f}%"
        )
    with col4:
        st.metric(
            "Revenue Growth",
            f"{revenue_growth:.1f}%"
        )

    st.markdown("### 📈 Revenue Trends")

    # Create revenue trends chart
    revenue_fig = px.line(revenue_trends, x='date', y='total_revenue', 
                         title="Monthly Revenue Trends", line_shape='spline')
    st.plotly_chart(revenue_fig, use_container_width=True)
    
    st.markdown("### 💹 Profit Margin Analysis")
    
    # Create profit margin chart
    margin_data = finance_data.groupby('date')['total_profit_margin'].sum().reset_index()
    margin_fig = px.line(margin_data, x='date', y='total_profit_margin', 
                        title="Monthly Profit Margin Trends", line_shape='spline')
    st.plotly_chart(margin_fig, use_container_width=True)

    # Additional insights
    st.markdown("### 💡 Financial Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Performance Metrics")
        st.markdown(f"**Monthly Avg Revenue:** ${revenue_trends['total_revenue'].mean():,.0f}")
        st.markdown(f"**Best Month Revenue:** ${revenue_trends['total_revenue'].max():,.0f}")
        st.markdown(f"**Revenue Volatility:** {revenue_trends['total_revenue'].std():.2f}")
        
    with col2:
        st.markdown("#### 🎯 Key Findings")
        for key, insight in insights.items():
            st.markdown(f"**{key.title()}:** {insight}")

# Setup sidebar controls
setup_sidebar_controls()

# Wait for data to be filtered
if 'filtered_finance' not in st.session_state:
    st.warning("Data is being filtered, please wait...")
    st.stop()

# Page content
filtered_finance = st.session_state.filtered_finance
if filtered_finance.empty:
    st.warning("No financial data available for the selected filters.")
else:
    show_financial_analysis(filtered_finance) 