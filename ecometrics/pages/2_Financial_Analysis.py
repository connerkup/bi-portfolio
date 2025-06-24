import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from data_connector import load_finance_data
from color_config import (
    CSS_COLORS, get_comparison_colors, get_financial_color, 
    get_heat_colors, get_monochrome_colors
)

# Helper functions for formatting
def format_large_number(value):
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}"

def format_count(value):
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.0f}K"
    else:
        return f"{value:,.0f}"

st.set_page_config(
    page_title="Financial Analysis - EcoMetrics",
    page_icon="💰",
)

st.title("💰 Financial Analysis")
st.markdown("---")

# Page description
st.markdown("""
## 💰 Financial Performance Dashboard
Analyze key financial metrics and performance indicators. 
Use the filters in the sidebar to drill down into specific product lines, regions, or time periods.
""")

# Load financial data
@st.cache_data(ttl=3600)
def load_cached_finance_data():
    return load_finance_data()

with st.spinner("Loading financial data..."):
    finance_data, status_message = load_cached_finance_data()

if finance_data.empty:
    st.error(f"No financial data available: {status_message}")
    st.stop()

# Display data status
st.sidebar.success(f"Data loaded: {status_message}")

# Sidebar filters
with st.sidebar:
    st.markdown("### 🔍 Filters")
    
    # Date range filter
    if not finance_data.empty:
        min_date = finance_data['date'].min()
        max_date = finance_data['date'].max()
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Product line filter
        product_lines = ['All'] + sorted(finance_data['product_line'].unique().tolist())
        selected_product = st.selectbox("Product Line", product_lines)
        
        # Region filter
        regions = ['All'] + sorted(finance_data['region'].unique().tolist())
        selected_region = st.selectbox("Region", regions)
        
        # Customer segment filter
        customer_segments = ['All'] + sorted(finance_data['customer_segment'].unique().tolist())
        selected_customer = st.selectbox("Customer Segment", customer_segments)
        
        # Apply filters
        filtered_data = finance_data.copy()
        if len(date_range) == 2:
            # Convert date objects to pandas datetime for comparison
            start_date = pd.to_datetime(date_range[0])
            end_date = pd.to_datetime(date_range[1])
            filtered_data = filtered_data[
                (filtered_data['date'] >= start_date) & 
                (filtered_data['date'] <= end_date)
            ]
        
        if selected_product != 'All':
            filtered_data = filtered_data[filtered_data['product_line'] == selected_product]
            
        if selected_region != 'All':
            filtered_data = filtered_data[filtered_data['region'] == selected_region]
            
        if selected_customer != 'All':
            filtered_data = filtered_data[filtered_data['customer_segment'] == selected_customer]
    else:
        filtered_data = finance_data

# KPI Metrics Section
st.markdown("### 📊 Key Financial Indicators")

# Create columns for KPIs
col1, col2, col3, col4 = st.columns(4)

if not filtered_data.empty:
    try:
        total_revenue = filtered_data['total_revenue'].sum()
        total_profit_margin = filtered_data['total_profit_margin'].sum()
        avg_profit_margin_pct = filtered_data['avg_profit_margin_pct'].mean()
        total_transactions = filtered_data['total_transactions'].sum()
    except Exception as e:
        st.error(f"Error calculating KPIs: {e}")
        st.stop()
else:
    total_revenue = 0
    total_profit_margin = 0
    avg_profit_margin_pct = 0
    total_transactions = 0

with col1:
    st.metric(
        label="💰 Revenue",
        value=format_large_number(total_revenue) if total_revenue > 0 else "No data",
        help="Total revenue across all operations"
    )

with col2:
    st.metric(
        label="💵 Profit Margin",
        value=format_large_number(total_profit_margin) if total_profit_margin > 0 else "No data",
        help="Total profit margin across all operations"
    )

with col3:
    st.metric(
        label="📈 Margin %",
        value=f"{avg_profit_margin_pct:.1f}%" if avg_profit_margin_pct > 0 else "No data",
        help="Average profit margin percentage"
    )

with col4:
    st.metric(
        label="🔢 Transactions",
        value=format_count(total_transactions) if total_transactions > 0 else "No data",
        help="Total number of transactions"
    )

# Revenue Analysis Section
st.markdown("---")
st.markdown("### 📈 Revenue Analysis")

if not filtered_data.empty:
    try:
        # Revenue trends over time by product line
        revenue_by_product = filtered_data.groupby(['date', 'product_line'])['total_revenue'].sum().reset_index()
        
        # Create Plotly line chart with smooth lines and distinct comparison colors
        fig_revenue = px.line(
            revenue_by_product,
            x='date',
            y='total_revenue',
            color='product_line',
            title='Revenue Trends Over Time by Product Line',
            labels={
                'date': 'Date',
                'total_revenue': 'Revenue ($)',
                'product_line': 'Product Line'
            },
            color_discrete_sequence=get_comparison_colors(len(revenue_by_product['product_line'].unique())),
            line_shape='spline'
        )
        
        # Update layout for better styling
        fig_revenue.update_layout(
            title_font_size=16,
            plot_bgcolor=None,
            paper_bgcolor=None,
            font=dict(size=12),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=50, r=50, t=80, b=80)
        )
        
        # Update traces for better line styling
        fig_revenue.update_traces(
            line=dict(width=3),
            mode='lines+markers',
            marker=dict(size=6, opacity=0.7)
        )
        
        # Update axes styling
        fig_revenue.update_xaxes(
            gridcolor=CSS_COLORS['neutral-medium'],
            showgrid=True,
            zeroline=False
        )
        fig_revenue.update_yaxes(
            gridcolor=CSS_COLORS['neutral-medium'],
            showgrid=True,
            zeroline=False
        )
        
        st.plotly_chart(fig_revenue, use_container_width=True, theme="streamlit")
        
        # Revenue by region (full-width horizontal bar chart)
        revenue_by_region = filtered_data.groupby('region')['total_revenue'].sum().reset_index()
        revenue_by_region = revenue_by_region.sort_values('total_revenue', ascending=False)
        
        # Create full-width horizontal bar chart for revenue by region
        region_chart = alt.Chart(revenue_by_region).mark_bar(
            color=get_financial_color('revenue')  # Green for revenue
        ).encode(
            x=alt.X('total_revenue:Q', 
                    title='Revenue ($)',
                    axis=alt.Axis(format=',.0f')),
            y=alt.Y('region:N', 
                    title='Region', 
                    sort='-x',
                    axis=alt.Axis(labelFontSize=12)),
            tooltip=[
                alt.Tooltip('region:N', title='Region'),
                alt.Tooltip('total_revenue:Q', title='Revenue ($)', format=',.0f')
            ]
        ).properties(
            title={
                'text': 'Revenue by Region - Global Distribution',
                'fontSize': 18,
                'fontWeight': 'bold'
            },
            height=400,
            width='container'
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium'],
            labelFontSize=12,
            titleFontSize=14
        ).configure_view(
            strokeWidth=0
        ).configure_title(
            fontSize=18,
            anchor='start',
            dy=-10
        )
        
        st.altair_chart(region_chart, use_container_width=True)
        
        # Revenue by customer segment (standalone chart)
        revenue_by_customer = filtered_data.groupby('customer_segment')['total_revenue'].sum().reset_index()
        revenue_by_customer = revenue_by_customer.sort_values('total_revenue', ascending=False)
        
        customer_chart = alt.Chart(revenue_by_customer).mark_bar(
            color=get_financial_color('profit')  # Blue for profit-related metrics
        ).encode(
            x=alt.X('total_revenue:Q', title='Revenue ($)'),
            y=alt.Y('customer_segment:N', title='Customer Segment', sort='-x'),
            tooltip=[
                alt.Tooltip('customer_segment:N', title='Customer Segment'),
                alt.Tooltip('total_revenue:Q', title='Revenue ($)', format=',.0f')
            ]
        ).properties(
            title='Revenue by Customer Segment',
            height=300
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(customer_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating revenue charts: {e}")

# Profitability Metrics Section
st.markdown("---")
st.markdown("### 💰 Profitability Metrics")

if not filtered_data.empty:
    try:
        # Profit margin trends over time
        profit_trends = filtered_data.groupby('date').agg({
            'avg_profit_margin_pct': 'mean',
            'overall_profit_margin_pct': 'mean',
            'avg_cost_of_goods_pct': 'mean',
            'avg_operating_cost_pct': 'mean'
        }).reset_index()
        
        # Create profit margin trend chart
        profit_chart = alt.Chart(profit_trends).mark_line(
            color=get_financial_color('margin'),  # Yellow for margin metrics
            strokeWidth=3,
            point=True
        ).encode(
            x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %Y')),
            y=alt.Y('avg_profit_margin_pct:Q', title='Profit Margin (%)'),
            tooltip=[
                alt.Tooltip('date:T', title='Date', format='%B %Y'),
                alt.Tooltip('avg_profit_margin_pct:Q', title='Profit Margin %', format='.1f')
            ]
        ).properties(
            title='Profit Margin Trends Over Time',
            height=300
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(profit_chart, use_container_width=True)
        
        # Cost structure breakdown
        # Cost structure by product line
        cost_structure = filtered_data.groupby('product_line').agg({
            'avg_cost_of_goods_pct': 'mean',
            'avg_operating_cost_pct': 'mean',
            'avg_profit_margin_pct': 'mean'
        }).reset_index()
        
        # Melt the data for stacked bar chart
        cost_melted = cost_structure.melt(
            id_vars=['product_line'],
            value_vars=['avg_cost_of_goods_pct', 'avg_operating_cost_pct', 'avg_profit_margin_pct'],
            var_name='cost_component',
            value_name='percentage'
        )
        
        # Map legend names for readability
        legend_names = {
            'avg_cost_of_goods_pct': 'Cost of Goods (%)',
            'avg_operating_cost_pct': 'Operating Cost (%)',
            'avg_profit_margin_pct': 'Profit Margin (%)'
        }
        cost_melted['cost_component'] = cost_melted['cost_component'].map(legend_names)
        
        # Create stacked bar chart (horizontal)
        cost_chart = alt.Chart(cost_melted).mark_bar().encode(
            y=alt.Y('product_line:N', title='Product Line', sort='-x'),
            x=alt.X('percentage:Q', title='Percentage (%)', stack='zero'),
            color=alt.Color('cost_component:N', 
                          title='Cost Component',
                          scale=alt.Scale(range=[
                              get_financial_color('cost'),      # Red for costs
                              get_financial_color('margin'),    # Yellow for operating costs
                              get_financial_color('profit')     # Blue for profit margin
                          ])),
            tooltip=[
                alt.Tooltip('product_line:N', title='Product Line'),
                alt.Tooltip('cost_component:N', title='Cost Component'),
                alt.Tooltip('percentage:Q', title='Percentage', format='.1f')
            ]
        ).properties(
            title='Cost Structure by Product Line',
            height=400
        ).configure_title(
            fontSize=16
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(cost_chart, use_container_width=True)
        
        # Revenue efficiency by product line (revenue per transaction)
        revenue_efficiency = filtered_data.groupby('product_line').agg({
            'total_revenue': 'sum',
            'total_transactions': 'sum',
            'avg_profit_margin_pct': 'mean'
        }).reset_index()
        
        # Calculate revenue per transaction
        revenue_efficiency['revenue_per_transaction'] = (
            revenue_efficiency['total_revenue'] / 
            revenue_efficiency['total_transactions']
        )
        
        efficiency_chart = alt.Chart(revenue_efficiency).mark_bar(
            color=get_financial_color('growth')  # Teal for growth/efficiency metrics
        ).encode(
            x=alt.X('revenue_per_transaction:Q', title='Revenue per Transaction ($)'),
            y=alt.Y('product_line:N', title='Product Line', sort='-x'),
            tooltip=[
                alt.Tooltip('product_line:N', title='Product Line'),
                alt.Tooltip('revenue_per_transaction:Q', title='Revenue per Transaction ($)', format='.2f'),
                alt.Tooltip('total_revenue:Q', title='Total Revenue ($)', format=',.0f'),
                alt.Tooltip('total_transactions:Q', title='Total Transactions', format=',.0f'),
                alt.Tooltip('avg_profit_margin_pct:Q', title='Avg Profit Margin %', format='.1f')
            ]
        ).properties(
            title='Revenue Efficiency by Product Line',
            height=400
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(efficiency_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating profitability charts: {e}")

# Financial Ratios Section
st.markdown("---")
st.markdown("### 📊 Financial Ratios")

if not filtered_data.empty:
    try:
        # Efficiency ratios over time
        efficiency_trends = filtered_data.groupby('date').agg({
            'avg_revenue_per_kg': 'mean',
            'avg_profit_per_kg': 'mean',
            'avg_revenue_per_liter': 'mean',
            'avg_profit_per_liter': 'mean'
        }).reset_index()
        
        # Create efficiency metrics chart
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue per kg trend
            revenue_per_kg_chart = alt.Chart(efficiency_trends).mark_line(
                color=get_financial_color('revenue'),  # Green for revenue metrics
                strokeWidth=3,
                point=True
            ).encode(
                x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %Y')),
                y=alt.Y('avg_revenue_per_kg:Q', title='Revenue per kg ($)'),
                tooltip=[
                    alt.Tooltip('date:T', title='Date', format='%B %Y'),
                    alt.Tooltip('avg_revenue_per_kg:Q', title='Revenue per kg', format='.2f')
                ]
            ).properties(
                title='Revenue per kg Over Time',
                height=250
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(revenue_per_kg_chart, use_container_width=True)
        
        with col2:
            # Profit per kg trend
            profit_per_kg_chart = alt.Chart(efficiency_trends).mark_line(
                color=get_financial_color('profit'),  # Blue for profit metrics
                strokeWidth=3,
                point=True
            ).encode(
                x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %Y')),
                y=alt.Y('avg_profit_per_kg:Q', title='Profit per kg ($)'),
                tooltip=[
                    alt.Tooltip('date:T', title='Date', format='%B %Y'),
                    alt.Tooltip('avg_profit_per_kg:Q', title='Profit per kg', format='.2f')
                ]
            ).properties(
                title='Profit per kg Over Time',
                height=250
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(profit_per_kg_chart, use_container_width=True)
        
        # Performance categories analysis
        performance_summary = filtered_data.groupby('performance_category').agg({
            'total_revenue': 'sum',
            'total_profit_margin': 'sum',
            'total_transactions': 'sum'
        }).reset_index()
        
        # Calculate profit margin percentage
        performance_summary['profit_margin_pct'] = (
            performance_summary['total_profit_margin'] / 
            performance_summary['total_revenue'] * 100
        )
        
        # Calculate dynamic axis domains with 10% padding
        min_x = performance_summary['total_revenue'].min()
        max_x = performance_summary['total_revenue'].max()
        x_padding = (max_x - min_x) * 0.1 if max_x > min_x else 1
        x_domain = [max(0, min_x - x_padding), max_x + x_padding]

        min_y = performance_summary['profit_margin_pct'].min()
        max_y = performance_summary['profit_margin_pct'].max()
        y_padding = (max_y - min_y) * 0.1 if max_y > min_y else 1
        y_domain = [min_y - y_padding, max_y + y_padding]

        # Create performance bubble chart
        performance_chart = alt.Chart(performance_summary).mark_circle(
            opacity=0.8,
            stroke='#cccccc',
            strokeWidth=0.5
        ).encode(
            x=alt.X('total_revenue:Q', 
                    title='Total Revenue ($)',
                    scale=alt.Scale(domain=x_domain),
                    axis=alt.Axis(labelAngle=0)),
            y=alt.Y('profit_margin_pct:Q', 
                    title='Profit Margin (%)',
                    scale=alt.Scale(domain=y_domain)),
            size=alt.Size('total_transactions:Q',
                          title='Number of Transactions',
                          scale=alt.Scale(range=[300, 2500])),
            color=alt.Color('performance_category:N', 
                           title='Performance Category',
                           scale=alt.Scale(scheme='pastel1')),
            tooltip=[
                alt.Tooltip('performance_category:N', title='Performance Category'),
                alt.Tooltip('total_revenue:Q', title='Total Revenue ($)', format=',.0f'),
                alt.Tooltip('profit_margin_pct:Q', title='Profit Margin (%)', format='.1f'),
                alt.Tooltip('total_transactions:Q', title='Transactions', format=',.0f')
            ]
        ).properties(
            title='Performance Categories: Revenue, Profit Margin & Transaction Volume',
            width=600,
            height=450
        ).configure_title(
            fontSize=18,
            anchor='start',
            dy=-5
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            stroke=None
        ).configure_legend(
            orient='right',
            titleFontSize=12,
            labelFontSize=11,
            padding=5
        )
        
        st.altair_chart(performance_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating financial ratio charts: {e}")

# Cash Flow Analysis Section
st.markdown("---")
st.markdown("### 💸 Cash Flow Analysis")

if not filtered_data.empty:
    try:
        # Cash flow metrics (using available data as proxy)
        cash_flow_data = filtered_data.groupby('date').agg({
            'total_revenue': 'sum',
            'total_cost_of_goods': 'sum',
            'total_operating_cost': 'sum',
            'total_profit_margin': 'sum'
        }).reset_index()
        
        # Calculate operating cash flow (revenue - costs)
        cash_flow_data['operating_cash_flow'] = (
            cash_flow_data['total_revenue'] - 
            cash_flow_data['total_cost_of_goods'] - 
            cash_flow_data['total_operating_cost']
        )
        
        # Create cash flow trend chart
        cash_flow_chart = alt.Chart(cash_flow_data).mark_line(
            color=get_financial_color('growth'),  # Teal for growth metrics
            strokeWidth=3,
            point=True
        ).encode(
            x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %Y')),
            y=alt.Y('operating_cash_flow:Q', title='Operating Cash Flow ($)'),
            tooltip=[
                alt.Tooltip('date:T', title='Date', format='%B %Y'),
                alt.Tooltip('operating_cash_flow:Q', title='Operating Cash Flow ($)', format=',.0f'),
                alt.Tooltip('total_revenue:Q', title='Total Revenue ($)', format=',.0f')
            ]
        ).properties(
            title='Operating Cash Flow Trends',
            height=300
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(cash_flow_chart, use_container_width=True)
        
        # Cash flow components breakdown
        # Revenue vs Costs breakdown
        cash_components = cash_flow_data.melt(
            id_vars=['date'],
            value_vars=['total_revenue', 'total_cost_of_goods', 'total_operating_cost'],
            var_name='component',
            value_name='amount'
        )
        
        # Map component names
        component_names = {
            'total_revenue': 'Revenue',
            'total_cost_of_goods': 'Cost of Goods',
            'total_operating_cost': 'Operating Cost'
        }
        cash_components['component'] = cash_components['component'].map(component_names)
        
        components_chart = alt.Chart(cash_components).mark_line(
            strokeWidth=2,
            point=True
        ).encode(
            x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %Y')),
            y=alt.Y('amount:Q', title='Amount ($)'),
            color=alt.Color('component:N', 
                          title='Cash Flow Component',
                          scale=alt.Scale(range=[
                              get_financial_color('revenue'),  # Green for revenue
                              get_financial_color('cost'),     # Red for costs
                              get_financial_color('margin')    # Yellow for operating costs
                          ])),
            tooltip=[
                alt.Tooltip('date:T', title='Date', format='%B %Y'),
                alt.Tooltip('component:N', title='Component'),
                alt.Tooltip('amount:Q', title='Amount ($)', format=',.0f')
            ]
        ).properties(
            title='Cash Flow Components Over Time',
            height=300
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(components_chart, use_container_width=True)
        
        # Cash flow efficiency by region
        regional_cash_flow = filtered_data.groupby('region').agg({
            'total_revenue': 'sum',
            'total_cost_of_goods': 'sum',
            'total_operating_cost': 'sum'
        }).reset_index()
        
        regional_cash_flow['operating_cash_flow'] = (
            regional_cash_flow['total_revenue'] - 
            regional_cash_flow['total_cost_of_goods'] - 
            regional_cash_flow['total_operating_cost']
        )
        
        regional_cash_flow['cash_flow_margin'] = (
            regional_cash_flow['operating_cash_flow'] / 
            regional_cash_flow['total_revenue'] * 100
        )
        
        regional_chart = alt.Chart(regional_cash_flow).mark_bar(
            color=get_financial_color('margin')  # Yellow for margin metrics
        ).encode(
            x=alt.X('region:N', title='Region'),
            y=alt.Y('cash_flow_margin:Q', title='Cash Flow Margin (%)'),
            tooltip=[
                alt.Tooltip('region:N', title='Region'),
                alt.Tooltip('cash_flow_margin:Q', title='Cash Flow Margin %', format='.1f'),
                alt.Tooltip('operating_cash_flow:Q', title='Operating Cash Flow ($)', format=',.0f')
            ]
        ).properties(
            title='Cash Flow Margin by Region',
            height=300
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(regional_chart, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating cash flow charts: {e}")

# Data Summary Section
st.markdown("---")
st.markdown("### 📋 Financial Data Summary")

if not filtered_data.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Data Coverage:**")
        st.write(f"- **Time Period:** {filtered_data['date'].min().strftime('%B %Y')} to {filtered_data['date'].max().strftime('%B %Y')}")
        st.write(f"- **Product Lines:** {len(filtered_data['product_line'].unique())}")
        st.write(f"- **Regions:** {len(filtered_data['region'].unique())}")
        st.write(f"- **Customer Segments:** {len(filtered_data['customer_segment'].unique())}")
        st.write(f"- **Data Points:** {len(filtered_data):,}")
    
    with col2:
        st.markdown("**Key Insights:**")
        st.write("- Revenue trends and growth patterns")
        st.write("- Profitability analysis by segment")
        st.write("- Cost structure optimization")
        st.write("- Financial efficiency metrics")

# Footer navigation
st.markdown("---")
if st.button("🏠 Back to Home"):
    st.switch_page("Home.py") 