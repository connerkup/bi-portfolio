"""
PackagingCo ESG & Finance Insights Dashboard

Main Streamlit application for the BI portfolio dashboard.

Features:
- Overview: Executive summary with key ESG and financial KPIs
- ESG Insights: Sustainability metrics and impact analysis
- Financial Analysis: Sales forecasts and financial KPIs
- Forecasting: Advanced sales forecasting with scenario modeling
- Combined Insights: Integrated ESG-finance scenario analysis
- Data Browser: Interactive data exploration with filtering, search, and export capabilities

Responsive Design:
- Uses CSS media queries for automatic responsive behavior
- Mobile-first approach with breakpoint at 900px
- Charts and KPI cards automatically stack on mobile devices
- Manual override available in sidebar for testing purposes
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os
import io

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from packagingco_insights.analysis import ESGAnalyzer, FinanceAnalyzer, SalesForecaster
from packagingco_insights.utils import (
    load_esg_data, load_finance_data, load_sales_data,
    create_kpi_card, format_currency, format_percentage,
    create_dashboard_header, create_sidebar_filters, apply_filters,
    load_csv_data
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
    
    /* Responsive design - Very conservative approach, always stack unless clearly wide */
    
    /* Default mobile-first styles - always stack */
    .metric-card {
        min-width: 140px;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    
    /* Force everything to stack by default - target actual Streamlit column classes */
    .stColumns {
        flex-direction: column !important;
    }
    
    .stColumn {
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        margin-bottom: 1rem;
    }
    
    /* Also target the horizontal block containers */
    .stHorizontalBlock > div {
        flex-direction: column !important;
    }
    
    .stHorizontalBlock > div > div {
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        margin-bottom: 1rem;
    }
    
    .kpi-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    /* Only go horizontal on very wide screens (1400px+) to be safe */
    @media (min-width: 1400px) {
        .metric-card {
            min-width: 180px;
            font-size: 1rem;
            margin-bottom: 1rem;
        }
        
        .stColumns {
            flex-direction: row !important;
        }
        
        .stColumn {
            width: auto !important;
            min-width: auto !important;
            max-width: none !important;
            margin-bottom: 0;
        }
        
        .stHorizontalBlock > div {
            flex-direction: row !important;
        }
        
        .stHorizontalBlock > div > div {
            width: auto !important;
            min-width: auto !important;
            max-width: none !important;
            margin-bottom: 0;
        }
        
        .kpi-container {
            display: flex;
            flex-direction: row;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .kpi-container .metric-card {
            flex: 1 1 200px;
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

@st.cache_data
def load_raw_data():
    """Load raw CSV data with caching."""
    try:
        raw_esg = load_csv_data("data/raw/sample_esg_data.csv")
        raw_sales = load_csv_data("data/raw/sample_sales_data.csv")
        return raw_esg, raw_sales
    except Exception as e:
        st.error(f"Error loading raw data: {e}")
        return None, None

def should_use_responsive_layout():
    """Simple function to provide manual override for responsive layout testing."""
    # CSS handles the responsive behavior automatically
    # This function just provides a manual override for testing
    manual_override = st.sidebar.checkbox(
        "📱 Force Mobile Layout", 
        value=False,
        help="Manually override to force mobile layout for testing purposes"
    )
    
    return manual_override

def display_charts_responsive(charts_data, titles=None):
    """Display charts stacked vertically, full width."""
    for i, chart in enumerate(charts_data):
        if titles and i < len(titles):
            st.subheader(titles[i])
        st.plotly_chart(chart, use_container_width=True)

def main():
    """Main dashboard function."""
    
    # Header
    st.markdown('<h1 class="main-header">📊 PackagingCo ESG & Finance Insights</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Balancing Sustainability Goals with Financial Performance</p>', unsafe_allow_html=True)
    
    # Load data
    esg_data, finance_data, sales_data = load_data()
    raw_esg_data, raw_sales_data = load_raw_data()
    
    if esg_data is None or finance_data is None or sales_data is None:
        st.error("Unable to load data. Please ensure the database is properly set up.")
        st.info("Run 'dbt run' in the dbt directory to set up the database.")
        return
    
    # Sidebar filters
    st.sidebar.title("🎛️ Dashboard Controls")
    
    # Page selection
    page = st.sidebar.selectbox(
        "Select Dashboard",
        ["🏠 Overview", "🌱 ESG Insights", "💰 Financial Analysis", "📈 Forecasting", "🔄 Combined Insights", "📋 Data Browser"]
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
    elif page == "📋 Data Browser":
        show_data_browser(esg_data, finance_data, sales_data, raw_esg_data, raw_sales_data)

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
    # Render as stacked KPI cards
    for card in kpi_cards:
        st.markdown(card, unsafe_allow_html=True)
    # Business question reminder
    st.markdown("""
    <div class="insight-box">
        <h4>🎯 Business Question</h4>
        <p><strong>How can PackagingCo drive ESG goals without compromising financial health?</strong></p>
        <p>This dashboard provides insights to answer this critical question through data-driven analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    # Charts row - stacked
    st.subheader("📊 Key Trends")
    revenue_trends = finance_data.groupby('month')['total_revenue'].sum().reset_index()
    revenue_fig = px.line(revenue_trends, x='month', y='total_revenue', title="Monthly Revenue Trends")
    emissions_trends = esg_data.groupby('month')['total_emissions_kg_co2'].sum().reset_index()
    emissions_fig = px.line(emissions_trends, x='month', y='total_emissions_kg_co2', title="Monthly CO2 Emissions")
    display_charts_responsive([revenue_fig, emissions_fig], ["📈 Revenue Trends", "🌱 Emissions Trends"])
    # Key insights
    st.markdown("## 💡 Key Insights")
    st.markdown("### 🌱 ESG Performance")
    esg_analyzer = ESGAnalyzer(esg_data)
    insights = esg_analyzer.get_esg_insights()
    for key, insight in insights.items():
        st.markdown(f"**{key.title()}:** {insight}")
    st.markdown("### 💰 Financial Performance")
    finance_analyzer = FinanceAnalyzer(finance_data)
    insights = finance_analyzer.get_financial_insights()
    for key, insight in insights.items():
        st.markdown(f"**{key.title()}:** {insight}")

def show_esg_insights(esg_data):
    """Show ESG insights dashboard."""
    st.markdown("## 🌱 ESG & Sustainability Insights")
    esg_analyzer = ESGAnalyzer(esg_data)
    st.subheader("📊 Key ESG Metrics")
    # Prepare KPI cards with responsive CSS
    total_emissions = esg_data['total_emissions_kg_co2'].sum()
    avg_recycled = esg_data['avg_recycled_material_pct'].mean()
    avg_recycling_rate = esg_data['avg_recycling_rate_pct'].mean()
    kpi_cards = []
    kpi_cards.append(create_kpi_card("Total CO2 Emissions", total_emissions, format_type="number", return_html=True))
    kpi_cards.append(create_kpi_card("Avg Recycled Material", avg_recycled, format_type="percentage", return_html=True))
    kpi_cards.append(create_kpi_card("Avg Recycling Rate", avg_recycling_rate, format_type="percentage", return_html=True))
    for card in kpi_cards:
        st.markdown(card, unsafe_allow_html=True)
    st.subheader("📊 ESG Performance Charts")
    emissions_fig = esg_analyzer.generate_emissions_chart('product_line', 'month')
    materials_fig = esg_analyzer.generate_materials_chart()
    display_charts_responsive([emissions_fig, materials_fig], ["📊 Emissions by Product Line", "♻️ Material Efficiency"])
    st.subheader("🏆 ESG Performance Score")
    esg_scores = esg_analyzer.calculate_esg_score()
    avg_esg_score = esg_scores['esg_score'].mean()
    st.metric("Average ESG Score", f"{avg_esg_score:.1f}/100")
    product_scores = esg_scores.groupby('product_line')['esg_score'].mean().sort_values(ascending=False)
    product_scores_fig = px.bar(x=product_scores.index, y=product_scores.values, title="ESG Score by Product Line")
    component_scores = {
        'Emissions': esg_scores['emissions_score'].mean(),
        'Energy': esg_scores['energy_score'].mean(),
        'Materials': esg_scores['materials_score'].mean(),
        'Waste': esg_scores['waste_score'].mean()
    }
    component_scores_fig = px.bar(x=list(component_scores.keys()), y=list(component_scores.values()), title="ESG Score Components")
    display_charts_responsive([product_scores_fig, component_scores_fig], ["ESG Score by Product Line", "ESG Score Components"])
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
    finance_analyzer = FinanceAnalyzer(finance_data)
    st.subheader("📊 Key Financial Metrics")
    kpi_values = [
        ("Total Revenue", float(finance_data['total_revenue'].sum() or 0), "currency"),
        ("Total Profit", float(finance_data['total_profit_margin'].sum() or 0), "currency"),
        ("Avg Profit Margin", float((finance_data['total_profit_margin'].sum() / finance_data['total_revenue'].sum()) * 100) if finance_data['total_revenue'].sum() else 0, "percentage"),
        ("Total Units Sold", int(finance_data['total_units_sold'].sum() or 0), "number"),
    ]
    for title, value, format_type in kpi_values:
        st.markdown(create_kpi_card(title, value, format_type=format_type, return_html=True), unsafe_allow_html=True)
    st.subheader("📊 Financial Performance Charts")
    revenue_fig = finance_analyzer.generate_revenue_chart('product_line', 'month')
    profitability_fig = finance_analyzer.generate_profitability_chart()
    display_charts_responsive([revenue_fig, profitability_fig], ["📈 Revenue Trends by Product Line", "📊 Profitability Analysis"])
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
    display_charts_responsive([revenue_by_region_fig, margin_by_region_fig], ["Revenue by Region", "Profit Margin by Region"])
    st.subheader("📈 Growth Analysis")
    growth_data = finance_analyzer.calculate_growth_rates('total_revenue', 1)
    if not growth_data.empty:
        fig = px.line(growth_data, x='month', y='total_revenue_growth_pct', color='product_line', title="Revenue Growth Trends")
        st.plotly_chart(fig, use_container_width=True)

def show_forecasting(sales_data):
    """Show forecasting dashboard."""
    st.markdown("## 📈 Sales Forecasting & Projections")
    forecaster = SalesForecaster(sales_data)
    st.subheader("⚙️ Forecasting Controls")
    forecast_periods = st.slider("Forecast Periods", 3, 12, 6)
    forecast_method = st.selectbox("Forecast Method", ["Linear", "Moving Average"])
    if forecast_method == "Linear":
        forecast_data = forecaster.simple_linear_forecast(forecast_periods, 'product_line')
    else:
        forecast_data = forecaster.moving_average_forecast(forecast_periods, 3, 'product_line')
    st.subheader("🔮 Sales Forecast")
    fig = forecaster.generate_forecast_chart(forecast_data, sales_data, 'product_line')
    st.plotly_chart(fig, use_container_width=True)
    insights = forecaster.get_forecast_insights(forecast_data)
    st.markdown("## 💡 Forecast Insights")
    for key, insight in insights.items():
        st.markdown(f"**{key.replace('_', ' ').title()}:** {insight}")
    st.subheader("📊 Trend Analysis")
    trends = forecaster.trend_analysis('revenue', 'product_line')
    growth_by_product_fig = px.bar(trends, x='product_line', y='percent_change', title="Revenue Growth by Product Line")
    avg_growth_fig = px.bar(trends, x='product_line', y='avg_monthly_growth', title="Average Monthly Growth")
    display_charts_responsive([growth_by_product_fig, avg_growth_fig], ["Revenue Growth by Product Line", "Average Monthly Growth"])
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
    st.subheader("🌱 ESG vs Financial Performance")
    emissions_vs_revenue_fig = px.scatter(merged_data, x='total_emissions_kg_co2', y='total_revenue', size='total_profit_margin', color='product_line', title="Emissions vs Revenue", labels={'total_emissions_kg_co2': 'Total CO2 Emissions (kg)', 'total_revenue': 'Total Revenue ($)'})
    recycled_vs_margin_fig = px.scatter(merged_data, x='avg_recycled_material_pct', y='avg_gross_margin_pct', size='total_revenue', color='product_line', title="Recycled Material % vs Gross Margin %", labels={'avg_recycled_material_pct': 'Recycled Material %', 'avg_gross_margin_pct': 'Gross Margin %'})
    display_charts_responsive([emissions_vs_revenue_fig, recycled_vs_margin_fig], ["Emissions vs Revenue", "Recycled Material % vs Gross Margin %"])
    st.subheader("📊 Correlation Analysis")
    correlations = merged_data[['total_emissions_kg_co2', 'avg_recycled_material_pct', 'avg_recycling_rate_pct', 'total_revenue', 'total_profit_margin', 'avg_gross_margin_pct']].corr()
    fig = px.imshow(correlations, title="Correlation Matrix: ESG vs Financial Metrics", color_continuous_scale='RdBu', aspect='auto')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("## 💡 Key Insights")
    best_esg = merged_data.loc[merged_data['avg_recycled_material_pct'].idxmax()]
    worst_emissions = merged_data.loc[merged_data['total_emissions_kg_co2'].idxmax()]
    best_profit = merged_data.loc[merged_data['total_profit_margin'].idxmax()]
    st.markdown("### 🌟 Best Performers")
    st.markdown(f"**Best ESG Performance:** {best_esg['product_line']} (" f"{best_esg['avg_recycled_material_pct']:.1f}% recycled)")
    st.markdown(f"**Best Financial Performance:** {best_profit['product_line']} (" f"${best_profit['total_profit_margin']:,.0f} profit)")
    st.markdown("### ⚠️ Areas for Improvement")
    st.markdown(f"**Highest Emissions:** {worst_emissions['product_line']} (" f"{worst_emissions['total_emissions_kg_co2']:,.0f} kg CO2)")
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

def show_data_browser(esg_data, finance_data, sales_data, raw_esg_data, raw_sales_data):
    """Show data browser dashboard."""
    st.markdown("## 📋 Data Browser")
    st.markdown("Explore the underlying data used in the dashboard with filtering and sorting capabilities.")
    datasets = {
        "🌱 ESG Data (Processed)": esg_data,
        "💰 Financial Data (Processed)": finance_data,
        "📈 Sales Data (Processed)": sales_data,
        "📄 Raw ESG Data": raw_esg_data,
        "📄 Raw Sales Data": raw_sales_data
    }
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
        selected_columns = st.multiselect("Select columns to display", df.columns.tolist(), default=df.columns.tolist()[:min(8, len(df.columns))])
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
                        range_vals = st.slider(f"Range {col}", min_value=float(min_val), max_value=float(max_val), value=(float(min_val), float(max_val)))
                        display_df = display_df[(display_df[col] >= range_vals[0]) & (display_df[col] <= range_vals[1])]
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
            st.download_button(label="Download filtered data as CSV", data=csv_data, file_name=f"{selected_dataset.replace(' ', '_').lower()}_filtered.csv", mime="text/csv")
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