"""
Financial Analysis Page

This page provides detailed financial performance analysis for PackagingCo.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from packagingco_insights.analysis import FinanceAnalyzer
from packagingco_insights.utils import create_kpi_card, display_charts_responsive

def main():
    """Financial Analysis page main function."""
    
    st.title("💰 Financial Performance Analysis")

    # Check if data is available in session state
    if 'filtered_finance' not in st.session_state or 'filtered_sales' not in st.session_state:
        st.error("No financial data available. Please return to the main page to load data.")
        st.info("The main page loads and filters the data for all pages.")
        return
    
    finance_data = st.session_state.filtered_finance
    sales_data = st.session_state.filtered_sales
    
    if finance_data.empty or sales_data.empty:
        st.warning("No financial data available for the selected filters.")
        return
    
    finance_analyzer = FinanceAnalyzer(finance_data)
    
    st.subheader("📊 Key Financial Metrics")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_revenue = finance_data['total_revenue'].sum()
        create_kpi_card("Total Revenue", total_revenue, format_type="currency")

    with col2:
        total_profit = finance_data['total_profit_margin'].sum()
        create_kpi_card("Total Profit", total_profit, format_type="currency")

    with col3:
        if total_revenue > 0:
            avg_margin = (total_profit / total_revenue) * 100
        else:
            avg_margin = 0
        create_kpi_card("Avg Profit Margin", avg_margin, format_type="percentage")

    with col4:
        total_units_sold = finance_data['total_units_sold'].sum()
        create_kpi_card("Total Units Sold", total_units_sold, format_type="number")
    
    st.subheader("📊 Financial Performance Charts")
    
    revenue_fig = finance_analyzer.generate_revenue_chart('product_line', 'date')
    profitability_fig = finance_analyzer.generate_profitability_chart()
    
    display_charts_responsive([revenue_fig, profitability_fig])
    
    st.subheader("💰 Cost Structure Analysis")
    
    fig = finance_analyzer.generate_cost_breakdown_chart()
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🌍 Regional Performance")
    
    regional_metrics = finance_data.groupby('region').agg({
        'total_revenue': 'sum',
        'total_profit_margin': 'sum',
        'total_units_sold': 'sum'
    }).reset_index()
    
    regional_metrics['profit_margin_pct'] = (
        regional_metrics['total_profit_margin'] / regional_metrics['total_revenue'] * 100
    )
    
    revenue_by_region_fig = px.bar(regional_metrics, x='region', y='total_revenue', title="Revenue by Region")
    margin_by_region_fig = px.bar(regional_metrics, x='region', y='profit_margin_pct', title="Profit Margin by Region")
    
    display_charts_responsive([revenue_by_region_fig, margin_by_region_fig])
    
    st.subheader("📈 Growth Analysis")
    
    # Add a slider to control the smoothing window
    smoothing_window = st.slider(
        "Smoothing Window (Months)", 
        min_value=1, 
        max_value=12, 
        value=3, 
        help="Adjust the window for the moving average to smooth the growth trend line. 1 means no smoothing."
    )
    
    growth_data = finance_analyzer.calculate_growth_rates('total_revenue', 1, smoothing_window=smoothing_window)
    
    if not growth_data.empty:
        # Ensure date column is datetime for proper plotting
        growth_data['date'] = pd.to_datetime(growth_data['date'])
        
        # Filter data based on session state visibility
        if 'visible_product_lines' in st.session_state:
            growth_data_filtered = growth_data[growth_data['product_line'].isin(st.session_state.visible_product_lines)]
        else:
            growth_data_filtered = growth_data

        # Check if the smoothed column exists, if not use the regular growth column
        if 'total_revenue_growth_pct_smoothed' in growth_data_filtered.columns:
            y_column = 'total_revenue_growth_pct_smoothed'
            title = "Smoothed Revenue Growth Trends"
        elif 'total_revenue_growth_pct' in growth_data_filtered.columns:
            y_column = 'total_revenue_growth_pct'
            title = "Revenue Growth Trends"
            st.warning("Smoothed growth data not available, using raw growth data instead.")
        else:
            st.error("No growth data columns found. Available columns: " + str(list(growth_data_filtered.columns)))
            return
            
        fig = px.line(growth_data_filtered, x='date', y=y_column, color='product_line', title=title, line_shape='spline')

        # This part is a bit of a hack since we can't get direct callbacks
        # We can't perfectly preserve the state, but we can avoid a full reset.
        # The legend selections will still reset, but this lays the groundwork.
        st.info("Note: Adjusting the slider will currently reset legend selections. This is a known limitation.")

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No growth data available. This might be due to insufficient historical data.")

if __name__ == "__main__":
    main() 