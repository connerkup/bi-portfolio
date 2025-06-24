import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from data_connector import load_finance_data
from color_config import (
    CSS_COLORS, get_comparison_colors, get_financial_color, 
    get_heat_colors, get_monochrome_colors, get_performance_color
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
    page_title="Customer Insights - EcoMetrics",
    page_icon="👥",
)

st.title("👥 Customer Insights")
st.markdown("---")

# Page description
st.markdown("""
## 👥 Customer Analytics Dashboard
Analyze customer behavior, segmentation, and value across different segments and regions. 
Use the filters in the sidebar to drill down into specific customer segments, regions, or time periods.
""")

# Load customer data (using finance data which contains customer information)
@st.cache_data(ttl=3600)
def load_cached_customer_data():
    return load_finance_data()

with st.spinner("Loading customer data..."):
    customer_data, status_message = load_cached_customer_data()

if customer_data.empty:
    st.error(f"No customer data available: {status_message}")
    st.stop()

# Display data status
st.sidebar.success(f"Data loaded: {status_message}")

# Sidebar filters
with st.sidebar:
    st.markdown("### 🔍 Filters")
    
    # Date range filter
    if not customer_data.empty:
        min_date = customer_data['date'].min()
        max_date = customer_data['date'].max()
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Customer segment filter
        customer_segments = ['All'] + sorted(customer_data['customer_segment'].unique().tolist())
        selected_customer = st.selectbox("Customer Segment", customer_segments)
        
        # Customer tier filter
        customer_tiers = ['All'] + sorted(customer_data['customer_tier'].unique().tolist())
        selected_tier = st.selectbox("Customer Tier", customer_tiers)
        
        # Region filter
        regions = ['All'] + sorted(customer_data['region'].unique().tolist())
        selected_region = st.selectbox("Region", regions)
        
        # Apply filters
        filtered_data = customer_data.copy()
        if len(date_range) == 2:
            # Convert date objects to pandas datetime for comparison
            start_date = pd.to_datetime(date_range[0])
            end_date = pd.to_datetime(date_range[1])
            filtered_data = filtered_data[
                (filtered_data['date'] >= start_date) & 
                (filtered_data['date'] <= end_date)
            ]
        
        if selected_customer != 'All':
            filtered_data = filtered_data[filtered_data['customer_segment'] == selected_customer]
            
        if selected_tier != 'All':
            filtered_data = filtered_data[filtered_data['customer_tier'] == selected_tier]
            
        if selected_region != 'All':
            filtered_data = filtered_data[filtered_data['region'] == selected_region]
    else:
        filtered_data = customer_data

# KPI Metrics Section
st.markdown("### 📊 Key Customer Indicators")

# Create columns for KPIs
col1, col2, col3, col4 = st.columns(4)

if not filtered_data.empty:
    try:
        total_customers = len(filtered_data['customer_segment'].unique())
        total_revenue = filtered_data['total_revenue'].sum()
        avg_profit_margin_pct = filtered_data['avg_profit_margin_pct'].mean()
        total_transactions = filtered_data['total_transactions'].sum()
    except Exception as e:
        st.error(f"Error calculating KPIs: {e}")
        st.stop()
else:
    total_customers = 0
    total_revenue = 0
    avg_profit_margin_pct = 0
    total_transactions = 0

with col1:
    st.metric(
        label="👥 Segments",
        value=f"{total_customers}" if total_customers > 0 else "No data",
        help="Number of unique customer segments"
    )

with col2:
    st.metric(
        label="💰 Revenue",
        value=format_large_number(total_revenue) if total_revenue > 0 else "No data",
        help="Total revenue from all customer segments"
    )

with col3:
    st.metric(
        label="📈 Margin %",
        value=f"{avg_profit_margin_pct:.1f}%" if avg_profit_margin_pct > 0 else "No data",
        help="Average profit margin across all segments"
    )

with col4:
    st.metric(
        label="🔢 Transactions",
        value=format_count(total_transactions) if total_transactions > 0 else "No data",
        help="Total number of transactions"
    )

# Customer Segmentation Section
st.markdown("---")
st.markdown("### 👥 Customer Segmentation")

if not filtered_data.empty:
    try:
        # Customer segment analysis
        segment_analysis = filtered_data.groupby('customer_segment').agg({
            'total_revenue': 'sum',
            'total_profit_margin': 'sum',
            'total_transactions': 'sum',
            'avg_profit_margin_pct': 'mean'
        }).reset_index()
        
        # Calculate profit margin percentage
        segment_analysis['profit_margin_pct'] = (
            segment_analysis['total_profit_margin'] / 
            segment_analysis['total_revenue'] * 100
        )
        
        # Calculate dynamic axis domains with 10% padding
        min_x = segment_analysis['total_revenue'].min()
        max_x = segment_analysis['total_revenue'].max()
        x_padding = (max_x - min_x) * 0.1 if max_x > min_x else 1
        x_domain = [max(0, min_x - x_padding), max_x + x_padding]

        min_y = segment_analysis['profit_margin_pct'].min()
        max_y = segment_analysis['profit_margin_pct'].max()
        y_padding = (max_y - min_y) * 0.1 if max_y > min_y else 1
        y_domain = [min_y - y_padding, max_y + y_padding]

        # Create customer segment bubble chart
        segment_chart = alt.Chart(segment_analysis).mark_circle(
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
            color=alt.Color('customer_segment:N', 
                           title='Customer Segment',
                           scale=alt.Scale(scheme='pastel1')),
            tooltip=[
                alt.Tooltip('customer_segment:N', title='Customer Segment'),
                alt.Tooltip('total_revenue:Q', title='Total Revenue ($)', format=',.0f'),
                alt.Tooltip('profit_margin_pct:Q', title='Profit Margin %', format='.1f'),
                alt.Tooltip('total_transactions:Q', title='Transactions', format=',.0f')
            ]
        ).properties(
            title='Customer Segments: Revenue, Profit Margin & Transaction Volume',
            width=600,
            height=450
        ).configure_title(
            fontSize=18,
            anchor='start',
            dy=-5
        ).configure_axis(
            gridColor='#666'
        ).configure_view(
            stroke=None
        ).configure_legend(
            orient='right',
            titleFontSize=12,
            labelFontSize=11,
            padding=5
        )
        
        st.altair_chart(segment_chart, use_container_width=True)
        
        # Customer tier analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue by customer tier (horizontal bar)
            tier_revenue = filtered_data.groupby('customer_tier')['total_revenue'].sum().reset_index()
            tier_revenue = tier_revenue.sort_values('total_revenue', ascending=False)
            
            tier_chart = alt.Chart(tier_revenue).mark_bar(
                color=get_financial_color('revenue')  # Green for revenue metrics
            ).encode(
                x=alt.X('total_revenue:Q', title='Total Revenue ($)'),
                y=alt.Y('customer_tier:N', title='Customer Tier', sort='-x'),
                tooltip=[
                    alt.Tooltip('customer_tier:N', title='Customer Tier'),
                    alt.Tooltip('total_revenue:Q', title='Revenue ($)', format=',.0f')
                ]
            ).properties(
                title='Revenue by Customer Tier',
                height=300
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(tier_chart, use_container_width=True)
        
        with col2:
            # Profit margin by customer tier (horizontal bar)
            tier_profit = filtered_data.groupby('customer_tier').agg({
                'total_revenue': 'sum',
                'total_profit_margin': 'sum'
            }).reset_index()
            
            tier_profit['profit_margin_pct'] = (
                tier_profit['total_profit_margin'] / 
                tier_profit['total_revenue'] * 100
            )
            
            profit_chart = alt.Chart(tier_profit).mark_bar(
                color=get_financial_color('profit')  # Blue for profit metrics
            ).encode(
                x=alt.X('profit_margin_pct:Q', title='Profit Margin (%)'),
                y=alt.Y('customer_tier:N', title='Customer Tier', sort='-x'),
                tooltip=[
                    alt.Tooltip('customer_tier:N', title='Customer Tier'),
                    alt.Tooltip('profit_margin_pct:Q', title='Profit Margin %', format='.1f')
                ]
            ).properties(
                title='Profit Margin by Customer Tier',
                height=300
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(profit_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating customer segmentation charts: {e}")

# Customer Behavior Analysis Section
st.markdown("---")
st.markdown("### 📊 Customer Behavior Analysis")

if not filtered_data.empty:
    try:
        # Purchase patterns over time by customer segment
        behavior_trends = filtered_data.groupby(['date', 'customer_segment']).agg({
            'total_revenue': 'sum',
            'total_transactions': 'sum',
            'avg_unit_price': 'mean'
        }).reset_index()
        
        # Create Plotly line chart with smooth lines and distinct comparison colors
        fig_revenue = px.line(
            behavior_trends,
            x='date',
            y='total_revenue',
            height=800,
            color='customer_segment',
            title='Revenue Trends by Customer Segment',
            labels={
                'date': 'Date',
                'total_revenue': 'Revenue ($)',
                'customer_segment': 'Customer Segment'
            },
            color_discrete_sequence=get_comparison_colors(len(behavior_trends['customer_segment'].unique())),
            line_shape='spline'  # Smooth lines
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
        
        # Product preferences and transaction analysis
        # Remove columns, stack charts vertically
        # Revenue by product line for different customer segments
        product_preferences = filtered_data.groupby(['product_line', 'customer_segment'])['total_revenue'].sum().reset_index()
        
        product_chart = alt.Chart(product_preferences).mark_bar().encode(
            x=alt.X('total_revenue:Q', title='Revenue ($)'),
            y=alt.Y('product_line:N', title='Product Line'),
            color=alt.Color(
                'customer_segment:N', 
                title='Customer Segment',
                scale=alt.Scale(range=get_comparison_colors(4)),  # Use comparison colors for segments
                legend=alt.Legend(orient='right')
            ),
            tooltip=[
                alt.Tooltip('product_line:N', title='Product Line'),
                alt.Tooltip('customer_segment:N', title='Customer Segment'),
                alt.Tooltip('total_revenue:Q', title='Revenue ($)', format=',.0f')
            ]
        ).properties(
            title='Product Preferences by Customer Segment',
            height=450
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(product_chart, use_container_width=True)

        # Transaction size analysis
        transaction_analysis = filtered_data.groupby('customer_segment').agg({
            'total_transactions': 'sum',
            'avg_unit_price': 'mean',
            'total_revenue': 'sum'
        }).reset_index()
        
        transaction_analysis['avg_transaction_value'] = (
            transaction_analysis['total_revenue'] / 
            transaction_analysis['total_transactions']
        )
        
        # Average transaction value by segment
        avg_transaction_chart = alt.Chart(transaction_analysis).mark_bar(
            color=get_financial_color('revenue')  # Green for revenue metrics
        ).encode(
            x=alt.X('avg_transaction_value:Q', title='Average Transaction Value ($)'),
            y=alt.Y('customer_segment:N', title='Customer Segment', sort='-x'),
            tooltip=[
                alt.Tooltip('customer_segment:N', title='Customer Segment'),
                alt.Tooltip('avg_transaction_value:Q', title='Avg Transaction Value ($)', format='.2f')
            ]
        ).properties(
            title='Average Transaction Value by Customer Segment',
            height=350
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(avg_transaction_chart, use_container_width=True)
        
        # Transaction frequency by segment
        frequency_chart = alt.Chart(transaction_analysis).mark_bar(
            color=get_financial_color('profit')  # Blue for profit-related metrics
        ).encode(
            x=alt.X('total_transactions:Q', title='Total Transactions'),
            y=alt.Y('customer_segment:N', title='Customer Segment', sort='-x'),
            tooltip=[
                alt.Tooltip('customer_segment:N', title='Customer Segment'),
                alt.Tooltip('total_transactions:Q', title='Total Transactions', format=',.0f')
            ]
        ).properties(
            title='Transaction Frequency by Customer Segment',
            height=350
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(frequency_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating customer behavior charts: {e}")

# Customer Lifetime Value Section
st.markdown("---")
st.markdown("### 💰 Customer Value Analysis")

if not filtered_data.empty:
    try:
        # Customer value metrics over time
        value_trends = filtered_data.groupby('date').agg({
            'avg_profit_margin_pct': 'mean',
            'avg_revenue_per_kg': 'mean',
            'avg_profit_per_kg': 'mean',
            'total_revenue': 'sum'
        }).reset_index()
        
        # Create customer value trend chart
        value_chart = alt.Chart(value_trends).mark_line(
            color=get_financial_color('margin'),  # Yellow for margin metrics
            strokeWidth=3,
            point=True
        ).encode(
            x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %Y')),
            y=alt.Y('avg_profit_margin_pct:Q', title='Profit Margin (%)'),
            tooltip=[
                alt.Tooltip('date:T', title='Date', format='%B %Y'),
                alt.Tooltip('avg_profit_margin_pct:Q', title='Profit Margin %', format='.1f'),
                alt.Tooltip('total_revenue:Q', title='Total Revenue ($)', format=',.0f')
            ]
        ).properties(
            title='Customer Profitability Trends Over Time',
            height=300
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(value_chart, use_container_width=True)
        
        # Regional customer analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue by region (horizontal bar)
            regional_revenue = filtered_data.groupby('region')['total_revenue'].sum().reset_index()
            regional_revenue = regional_revenue.sort_values('total_revenue', ascending=False)
            
            regional_chart = alt.Chart(regional_revenue).mark_bar(
                color=get_financial_color('growth')  # Teal for growth metrics
            ).encode(
                x=alt.X('total_revenue:Q', title='Total Revenue ($)'),
                y=alt.Y('region:N', title='Region', sort='-x'),
                tooltip=[
                    alt.Tooltip('region:N', title='Region'),
                    alt.Tooltip('total_revenue:Q', title='Revenue ($)', format=',.0f')
                ]
            ).properties(
                title='Revenue by Region',
                height=300
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(regional_chart, use_container_width=True)
        
        with col2:
            # Market type analysis
            market_analysis = filtered_data.groupby('market_type').agg({
                'total_revenue': 'sum',
                'avg_profit_margin_pct': 'mean',
                'total_transactions': 'sum'
            }).reset_index()
            
            market_chart = alt.Chart(market_analysis).mark_bar(
                color=get_financial_color('profit')  # Blue for profit metrics
            ).encode(
                x=alt.X('avg_profit_margin_pct:Q', title='Profit Margin (%)'),
                y=alt.Y('market_type:N', title='Market Type'),
                tooltip=[
                    alt.Tooltip('market_type:N', title='Market Type'),
                    alt.Tooltip('avg_profit_margin_pct:Q', title='Profit Margin %', format='.1f'),
                    alt.Tooltip('total_revenue:Q', title='Total Revenue ($)', format=',.0f')
                ]
            ).properties(
                title='Profit Margin by Market Type',
                height=300
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(market_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating customer value charts: {e}")

# Customer Satisfaction & Performance Section
st.markdown("---")
st.markdown("### 😊 Customer Performance Metrics")

if not filtered_data.empty:
    try:
        # Performance categories analysis
        performance_analysis = filtered_data.groupby('performance_category').agg({
            'total_revenue': 'sum',
            'total_profit_margin': 'sum',
            'total_transactions': 'sum'
        }).reset_index()
        
        # Calculate profit margin percentage
        performance_analysis['profit_margin_pct'] = (
            performance_analysis['total_profit_margin'] / 
            performance_analysis['total_revenue'] * 100
        )
        
        # Create performance chart
        performance_chart = alt.Chart(performance_analysis).mark_bar(
            color=get_performance_color('excellent')  # Green for excellent performance
        ).encode(
            x=alt.X('profit_margin_pct:Q', title='Profit Margin (%)'),
            y=alt.Y('performance_category:N', title='Performance Category'),
            tooltip=[
                alt.Tooltip('performance_category:N', title='Performance Category'),
                alt.Tooltip('profit_margin_pct:Q', title='Profit Margin %', format='.1f'),
                alt.Tooltip('total_revenue:Q', title='Total Revenue ($)', format=',.0f')
            ]
        ).properties(
            title='Profit Margin by Performance Category',
            height=500
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-medium']
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(performance_chart, use_container_width=True)
        
        # Strategic segment analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Star performer analysis
            star_performer_data = filtered_data.groupby('customer_segment').agg({
                'star_performer_transactions': 'sum',
                'total_transactions': 'sum'
            }).reset_index()
            
            star_performer_data['star_performer_rate'] = (
                star_performer_data['star_performer_transactions'] / 
                star_performer_data['total_transactions'] * 100
            )
            
            star_chart = alt.Chart(star_performer_data).mark_bar(
                color=get_performance_color('good')  # Blue for good performance
            ).encode(
                x=alt.X('star_performer_rate:Q', title='Star Performer Rate (%)'),
                y=alt.Y('customer_segment:N', title='Customer Segment'),
                tooltip=[
                    alt.Tooltip('customer_segment:N', title='Customer Segment'),
                    alt.Tooltip('star_performer_rate:Q', title='Star Performer Rate %', format='.1f')
                ]
            ).properties(
                title='Star Performer Rate by Customer Segment',
                height=450
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(star_chart, use_container_width=True)
        
        with col2:
            # Premium high value analysis
            premium_data = filtered_data.groupby('customer_segment').agg({
                'premium_high_value_transactions': 'sum',
                'total_transactions': 'sum'
            }).reset_index()
            
            premium_data['premium_rate'] = (
                premium_data['premium_high_value_transactions'] / 
                premium_data['total_transactions'] * 100
            )
            
            premium_chart = alt.Chart(premium_data).mark_bar(
                color=get_financial_color('revenue')  # Green for revenue metrics
            ).encode(
                x=alt.X('premium_rate:Q', title='Premium High Value Rate (%)'),
                y=alt.Y('customer_segment:N', title='Customer Segment'),
                tooltip=[
                    alt.Tooltip('customer_segment:N', title='Customer Segment'),
                    alt.Tooltip('premium_rate:Q', title='Premium Rate %', format='.1f')
                ]
            ).properties(
                title='Premium High Value Rate by Customer Segment',
                height=450
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(premium_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating customer performance charts: {e}")

# Data Summary Section
st.markdown("---")
st.markdown("### 📋 Customer Data Summary")

if not filtered_data.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Data Coverage:**")
        st.write(f"- **Time Period:** {filtered_data['date'].min().strftime('%B %Y')} to {filtered_data['date'].max().strftime('%B %Y')}")
        st.write(f"- **Customer Segments:** {len(filtered_data['customer_segment'].unique())}")
        st.write(f"- **Customer Tiers:** {len(filtered_data['customer_tier'].unique())}")
        st.write(f"- **Regions:** {len(filtered_data['region'].unique())}")
        st.write(f"- **Data Points:** {len(filtered_data):,}")
    
    with col2:
        st.markdown("**Key Insights:**")
        st.write("- Customer segment profitability analysis")
        st.write("- Purchase behavior patterns")
        st.write("- Regional customer performance")
        st.write("- Customer value optimization")

# Footer navigation
st.markdown("---")
if st.button("🏠 Back to Home"):
    st.switch_page("Home.py")