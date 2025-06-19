"""
PackagingCo ESG & Finance Insights Dashboard

Main Streamlit application for the BI portfolio dashboard.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from packagingco_insights.analysis import ESGAnalyzer, FinanceAnalyzer, SalesForecaster
from packagingco_insights.utils import (
    load_esg_data, load_finance_data, load_sales_data,
    create_kpi_card, format_currency, format_percentage,
    create_dashboard_header, create_sidebar_filters, apply_filters
)

# Page configuration
st.set_page_config(
    page_title="PackagingCo BI Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #90caf9;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #b0bec5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #23272f;
        color: #fff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #90caf9;
        margin-bottom: 1rem;
        min-width: 180px;
        max-width: 100%;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        box-sizing: border-box;
    }
    .insight-box {
        background-color: #263238;
        color: #fff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffb300;
        margin: 1rem 0;
    }
    .stSidebar {
        background-color: #1a1d23 !important;
    }
    .stApp {
        background-color: #181a20;
    }
    /* Ensure KPI cards in columns have spacing and don't squish */
    .element-container:has(.metric-card) {
        min-width: 200px;
        flex: 1 1 200px;
        margin-right: 1rem;
    }
    @media (max-width: 900px) {
        .metric-card {
            min-width: 140px;
            font-size: 0.95rem;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load data from the database with caching."""
    try:
        esg_data = load_esg_data()
        finance_data = load_finance_data()
        sales_data = load_sales_data()
        return esg_data, finance_data, sales_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

def main():
    """Main dashboard function."""
    
    # Header
    st.markdown('<h1 class="main-header">📊 PackagingCo ESG & Finance Insights</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Balancing Sustainability Goals with Financial Performance</p>', unsafe_allow_html=True)
    
    # Load data
    esg_data, finance_data, sales_data = load_data()
    
    if esg_data is None or finance_data is None or sales_data is None:
        st.error("Unable to load data. Please ensure the database is properly set up.")
        st.info("Run 'dbt run' in the dbt directory to set up the database.")
        return
    
    # Sidebar filters
    st.sidebar.title("🎛️ Dashboard Controls")
    
    # Page selection
    page = st.sidebar.selectbox(
        "Select Dashboard",
        ["🏠 Overview", "🌱 ESG Insights", "💰 Financial Analysis", "📈 Forecasting", "🔄 Combined Insights"]
    )
    
    # Global filters
    st.sidebar.markdown("### Filters")
    
    # Date range filter
    if 'month' in esg_data.columns:
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(esg_data['month'].min(), esg_data['month'].max()),
            min_value=esg_data['month'].min(),
            max_value=esg_data['month'].max()
        )
    
    # Product line filter
    product_lines = st.sidebar.multiselect(
        "Product Lines",
        options=sorted(esg_data['product_line'].unique()),
        default=sorted(esg_data['product_line'].unique())
    )
    
    # Apply filters
    filtered_esg = esg_data[esg_data['product_line'].isin(product_lines)]
    filtered_finance = finance_data[finance_data['product_line'].isin(product_lines)]
    filtered_sales = sales_data[sales_data['product_line'].isin(product_lines)]
    
    # Guard: If no product lines are selected, show warning and return
    if len(product_lines) == 0 or filtered_esg.empty or filtered_finance.empty or filtered_sales.empty:
        st.warning("Please select at least one product line to view dashboard insights.")
        return

    # Page routing
    if page == "🏠 Overview":
        show_overview(filtered_esg, filtered_finance, filtered_sales)
    elif page == "🌱 ESG Insights":
        show_esg_insights(filtered_esg)
    elif page == "💰 Financial Analysis":
        show_financial_analysis(filtered_finance, filtered_sales)
    elif page == "📈 Forecasting":
        show_forecasting(filtered_sales)
    elif page == "🔄 Combined Insights":
        show_combined_insights(filtered_esg, filtered_finance)

def show_overview(esg_data, finance_data, sales_data):
    """Show the overview dashboard."""
    
    st.markdown("## 📊 Executive Summary")

    # Prepare KPI card HTMLs
    kpi_cards = []
    total_revenue = finance_data['total_revenue'].sum()
    kpi_cards.append(create_kpi_card("Total Revenue", total_revenue, format_type="currency", return_html=True))
    total_emissions = esg_data['total_emissions_kg_co2'].sum()
    kpi_cards.append(create_kpi_card("Total CO2 Emissions", total_emissions, format_type="number", return_html=True))
    avg_recycled = esg_data['avg_recycled_material_pct'].mean()
    kpi_cards.append(create_kpi_card("Avg Recycled Material", avg_recycled, format_type="percentage", return_html=True))
    avg_margin = (finance_data['total_profit_margin'].sum() / finance_data['total_revenue'].sum()) * 100
    kpi_cards.append(create_kpi_card("Avg Profit Margin", avg_margin, format_type="percentage", return_html=True))

    # Render as responsive flexbox
    kpi_cards_html = f'''<div style="display: flex; flex-wrap: wrap; gap: 1rem; justify-content: flex-start;">{''.join(kpi_cards)}</div>'''
    st.markdown(kpi_cards_html, unsafe_allow_html=True)

    # Business question reminder
    st.markdown("""
    <div class="insight-box">
        <h4>🎯 Business Question</h4>
        <p><strong>How can PackagingCo drive ESG goals without compromising financial health?</strong></p>
        <p>This dashboard provides insights to answer this critical question through data-driven analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trends")
        revenue_trends = finance_data.groupby('month')['total_revenue'].sum().reset_index()
        fig = px.line(revenue_trends, x='month', y='total_revenue', 
                     title="Monthly Revenue Trends")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌱 Emissions Trends")
        emissions_trends = esg_data.groupby('month')['total_emissions_kg_co2'].sum().reset_index()
        fig = px.line(emissions_trends, x='month', y='total_emissions_kg_co2',
                     title="Monthly CO2 Emissions")
        st.plotly_chart(fig, use_container_width=True)
    
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

def show_esg_insights(esg_data):
    """Show ESG insights dashboard."""
    
    st.markdown("## 🌱 ESG & Sustainability Insights")
    
    # Initialize ESG analyzer
    esg_analyzer = ESGAnalyzer(esg_data)
    
    # Key ESG metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_emissions = esg_data['total_emissions_kg_co2'].sum()
        create_kpi_card("Total CO2 Emissions", total_emissions, format_type="number")
    
    with col2:
        avg_recycled = esg_data['avg_recycled_material_pct'].mean()
        create_kpi_card("Avg Recycled Material", avg_recycled, format_type="percentage")
    
    with col3:
        avg_recycling_rate = esg_data['avg_recycling_rate_pct'].mean()
        create_kpi_card("Avg Recycling Rate", avg_recycling_rate, format_type="percentage")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Emissions by Product Line")
        fig = esg_analyzer.generate_emissions_chart('product_line', 'month')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("♻️ Material Efficiency")
        fig = esg_analyzer.generate_materials_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    # ESG Score Analysis
    st.subheader("🏆 ESG Performance Score")
    
    esg_scores = esg_analyzer.calculate_esg_score()
    
    col1, col2 = st.columns(2)
    
    with col1:
        avg_esg_score = esg_scores['esg_score'].mean()
        st.metric("Average ESG Score", f"{avg_esg_score:.1f}/100")
        
        # ESG score by product line
        product_scores = esg_scores.groupby('product_line')['esg_score'].mean().sort_values(ascending=False)
        fig = px.bar(x=product_scores.index, y=product_scores.values,
                    title="ESG Score by Product Line")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ESG score components
        component_scores = {
            'Emissions': esg_scores['emissions_score'].mean(),
            'Energy': esg_scores['energy_score'].mean(),
            'Materials': esg_scores['materials_score'].mean(),
            'Waste': esg_scores['waste_score'].mean()
        }
        
        fig = px.bar(x=list(component_scores.keys()), y=list(component_scores.values()),
                    title="ESG Score Components")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.markdown("## 💡 ESG Recommendations")
    
    st.markdown("""
    <div class="insight-box">
        <h4>🎯 Key Recommendations</h4>
        <ul>
            <li><strong>Focus on Glass Bottles:</strong> Highest emissions, consider alternative materials</li>
            <li><strong>Increase Recycled Content:</strong> Target 70%+ recycled material usage</li>
            <li><strong>Energy Efficiency:</strong> Implement energy-saving measures in production</li>
            <li><strong>Waste Reduction:</strong> Improve recycling rates across all facilities</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_financial_analysis(finance_data, sales_data):
    """Show financial analysis dashboard."""
    
    st.markdown("## 💰 Financial Performance Analysis")
    
    # Initialize finance analyzer
    finance_analyzer = FinanceAnalyzer(finance_data)
    
    # Key financial metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = finance_data['total_revenue'].sum()
        create_kpi_card("Total Revenue", total_revenue, format_type="currency")
    
    with col2:
        total_profit = finance_data['total_profit_margin'].sum()
        create_kpi_card("Total Profit", total_profit, format_type="currency")
    
    with col3:
        avg_margin = (total_profit / total_revenue) * 100
        create_kpi_card("Avg Profit Margin", avg_margin, format_type="percentage")
    
    with col4:
        total_units = finance_data['total_units_sold'].sum()
        create_kpi_card("Total Units Sold", total_units, format_type="number")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trends by Product Line")
        fig = finance_analyzer.generate_revenue_chart('product_line', 'month')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Profitability Analysis")
        fig = finance_analyzer.generate_profitability_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    # Cost breakdown
    st.subheader("💰 Cost Structure Analysis")
    fig = finance_analyzer.generate_cost_breakdown_chart()
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional analysis
    st.subheader("🌍 Regional Performance")
    
    regional_metrics = finance_data.groupby('region').agg({
        'total_revenue': 'sum',
        'total_profit_margin': 'sum',
        'total_units_sold': 'sum'
    }).reset_index()
    
    regional_metrics['profit_margin_pct'] = (
        regional_metrics['total_profit_margin'] / regional_metrics['total_revenue'] * 100
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(regional_metrics, x='region', y='total_revenue',
                    title="Revenue by Region")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(regional_metrics, x='region', y='profit_margin_pct',
                    title="Profit Margin by Region")
        st.plotly_chart(fig, use_container_width=True)
    
    # Growth analysis
    st.subheader("📈 Growth Analysis")
    
    growth_data = finance_analyzer.calculate_growth_rates('total_revenue', 1)
    if not growth_data.empty:
        fig = px.line(growth_data, x='month', y='total_revenue_growth_pct', color='product_line',
                     title="Revenue Growth Trends")
        st.plotly_chart(fig, use_container_width=True)

def show_forecasting(sales_data):
    """Show forecasting dashboard."""
    
    st.markdown("## 📈 Sales Forecasting & Projections")
    
    # Initialize forecaster
    forecaster = SalesForecaster(sales_data)
    
    # Forecasting controls
    col1, col2 = st.columns(2)
    
    with col1:
        forecast_periods = st.slider("Forecast Periods", 3, 12, 6)
    
    with col2:
        forecast_method = st.selectbox("Forecast Method", ["Linear", "Moving Average"])
    
    # Generate forecasts
    if forecast_method == "Linear":
        forecast_data = forecaster.simple_linear_forecast(forecast_periods, 'product_line')
    else:
        forecast_data = forecaster.moving_average_forecast(forecast_periods, 3, 'product_line')
    
    # Display forecast
    st.subheader("🔮 Sales Forecast")
    
    fig = forecaster.generate_forecast_chart(forecast_data, sales_data, 'product_line')
    st.plotly_chart(fig, use_container_width=True)
    
    # Forecast insights
    insights = forecaster.get_forecast_insights(forecast_data)
    
    st.markdown("## 💡 Forecast Insights")
    
    for key, insight in insights.items():
        st.markdown(f"**{key.replace('_', ' ').title()}:** {insight}")
    
    # Trend analysis
    st.subheader("📊 Trend Analysis")
    
    trends = forecaster.trend_analysis('revenue', 'product_line')
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(trends, x='product_line', y='percent_change',
                    title="Revenue Growth by Product Line")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(trends, x='product_line', y='avg_monthly_growth',
                    title="Average Monthly Growth")
        st.plotly_chart(fig, use_container_width=True)
    
    # Historical trends
    st.subheader("📈 Historical Trends")
    fig = forecaster.generate_trend_chart('revenue', 'product_line')
    st.plotly_chart(fig, use_container_width=True)

def show_combined_insights(esg_data, finance_data):
    """Show combined ESG and Finance insights."""
    
    st.markdown("## 🔄 ESG-Finance Combined Insights")
    
    st.markdown("""
    <div class="insight-box">
        <h4>🎯 Integrated Analysis</h4>
        <p>This section explores the relationship between ESG performance and financial outcomes, 
        helping identify win-win opportunities for sustainability and profitability.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Merge ESG and Finance data
    merged_data = pd.merge(
        esg_data.groupby('product_line').agg({
            'total_emissions_kg_co2': 'sum',
            'avg_recycled_material_pct': 'mean',
            'avg_recycling_rate_pct': 'mean'
        }).reset_index(),
        finance_data.groupby('product_line').agg({
            'total_revenue': 'sum',
            'total_profit_margin': 'sum',
            'avg_gross_margin_pct': 'mean'
        }).reset_index(),
        on='product_line'
    )
    
    # ESG vs Financial Performance
    st.subheader("🌱 ESG vs Financial Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Emissions vs Revenue
        fig = px.scatter(merged_data, x='total_emissions_kg_co2', y='total_revenue',
                        size='total_profit_margin', color='product_line',
                        title="Emissions vs Revenue",
                        labels={'total_emissions_kg_co2': 'Total CO2 Emissions (kg)',
                               'total_revenue': 'Total Revenue ($)'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Recycled Material vs Profit Margin
        fig = px.scatter(merged_data, x='avg_recycled_material_pct', y='avg_gross_margin_pct',
                        size='total_revenue', color='product_line',
                        title="Recycled Material % vs Gross Margin %",
                        labels={'avg_recycled_material_pct': 'Recycled Material %',
                               'avg_gross_margin_pct': 'Gross Margin %'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation analysis
    st.subheader("📊 Correlation Analysis")
    
    # Calculate correlations
    correlations = merged_data[['total_emissions_kg_co2', 'avg_recycled_material_pct', 
                               'avg_recycling_rate_pct', 'total_revenue', 
                               'total_profit_margin', 'avg_gross_margin_pct']].corr()
    
    fig = px.imshow(correlations, 
                    title="Correlation Matrix: ESG vs Financial Metrics",
                    color_continuous_scale='RdBu',
                    aspect='auto')
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.markdown("## 💡 Key Insights")
    
    # Find best and worst performers
    best_esg = merged_data.loc[merged_data['avg_recycled_material_pct'].idxmax()]
    worst_emissions = merged_data.loc[merged_data['total_emissions_kg_co2'].idxmax()]
    best_profit = merged_data.loc[merged_data['total_profit_margin'].idxmax()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌟 Best Performers")
        st.markdown(f"**Best ESG Performance:** {best_esg['product_line']} "
                   f"({best_esg['avg_recycled_material_pct']:.1f}% recycled)")
        st.markdown(f"**Best Financial Performance:** {best_profit['product_line']} "
                   f"(${best_profit['total_profit_margin']:,.0f} profit)")
    
    with col2:
        st.markdown("### ⚠️ Areas for Improvement")
        st.markdown(f"**Highest Emissions:** {worst_emissions['product_line']} "
                   f"({worst_emissions['total_emissions_kg_co2']:,.0f} kg CO2)")
    
    # Recommendations
    st.markdown("## 🎯 Strategic Recommendations")
    
    st.markdown("""
    <div class="insight-box">
        <h4>💡 Win-Win Opportunities</h4>
        <ul>
            <li><strong>Invest in Paper Packaging:</strong> High recycled content, good margins</li>
            <li><strong>Optimize Glass Production:</strong> Reduce emissions while maintaining quality</li>
            <li><strong>Scale Plastic Recycling:</strong> Increase recycled content in plastic containers</li>
            <li><strong>Regional Strategy:</strong> Focus on high-margin regions with ESG initiatives</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 