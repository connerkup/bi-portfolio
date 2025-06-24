import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from data_connector import load_supply_chain_data
from color_config import (
    CSS_COLORS, get_comparison_colors, get_performance_color, 
    get_heat_colors, get_monochrome_colors, get_financial_color, get_sustainability_color
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
    page_title="Supply Chain Insights - EcoMetrics",
    page_icon="🔄",
)

st.title("🔄 Supply Chain Insights")
st.markdown("---")

# Page description
st.markdown("""
## 🔄 Supply Chain Optimization Dashboard
Analyze supply chain performance, supplier metrics, and logistics optimization. 
Use the filters in the sidebar to drill down into specific suppliers, time periods, or performance categories.
""")

# Load supply chain data
@st.cache_data(ttl=3600)
def load_cached_supply_chain_data():
    return load_supply_chain_data()

def normalize_supply_chain_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to handle both fact and staging table formats.
    """
    if df.empty:
        return df
    
    # Create a copy to avoid modifying the original
    normalized_df = df.copy()
    
    # Map fact table columns to expected column names
    column_mapping = {
        'delivery_performance_category': 'delivery_performance',
        'quality_performance_category': 'quality_status',
        'total_quantity': 'order_quantity',
        'total_order_value': 'order_value',
        'avg_unit_cost': 'unit_cost',
        'on_time_delivery_rate_pct': 'on_time_delivery_rate',
        'quality_issue_rate_pct': 'quality_issue_rate',
        'avg_defect_rate': 'defect_rate_pct',
        'avg_supplier_reliability': 'supplier_reliability',
        'avg_sustainability_rating': 'sustainability_rating',
        'reliability_category': 'reliability_level',
        'sustainability_category': 'sustainability_category',
        'avg_delivery_variance': 'delivery_variance_days',
        'avg_actual_delivery_days': 'actual_delivery_days',
        'avg_expected_delivery_days': 'expected_delivery_days',
        'total_defect_quantity': 'defect_quantity'
    }
    
    # Rename columns that exist
    for old_name, new_name in column_mapping.items():
        if old_name in normalized_df.columns and new_name not in normalized_df.columns:
            normalized_df = normalized_df.rename(columns={old_name: new_name})
    
    # Create missing columns if they don't exist
    if 'delivery_performance' not in normalized_df.columns and 'on_time_delivery_rate' in normalized_df.columns:
        normalized_df['delivery_performance'] = normalized_df['on_time_delivery_rate'].apply(
            lambda x: 'On Time' if x >= 85 else 'Late'
        )
    
    if 'quality_status' not in normalized_df.columns and 'quality_issue_rate' in normalized_df.columns:
        normalized_df['quality_status'] = normalized_df['quality_issue_rate'].apply(
            lambda x: 'Quality Issues' if x > 5 else 'No Quality Issues'
        )
    
    if 'on_time_delivery' not in normalized_df.columns and 'on_time_delivery_rate' in normalized_df.columns:
        normalized_df['on_time_delivery'] = normalized_df['on_time_delivery_rate'] >= 85
    
    if 'quality_issues' not in normalized_df.columns and 'quality_issue_rate' in normalized_df.columns:
        normalized_df['quality_issues'] = normalized_df['quality_issue_rate'] > 5
    
    return normalized_df

with st.spinner("Loading supply chain data..."):
    supply_chain_data, status_message = load_cached_supply_chain_data()

if supply_chain_data.empty:
    st.error(f"No supply chain data available: {status_message}")
    st.stop()

# Normalize column names
supply_chain_data = normalize_supply_chain_columns(supply_chain_data)

# Display data status
st.sidebar.success(f"Data loaded: {status_message}")

# Sidebar filters
with st.sidebar:
    st.markdown("### 🔍 Filters")
    
    # Date range filter
    if not supply_chain_data.empty:
        min_date = supply_chain_data['date'].min()
        max_date = supply_chain_data['date'].max()
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Supplier filter
        suppliers = ['All'] + sorted(supply_chain_data['supplier'].unique().tolist())
        selected_supplier = st.selectbox("Supplier", suppliers)
        
        # Delivery performance filter
        if 'delivery_performance' in supply_chain_data.columns:
            delivery_performances = ['All'] + sorted(supply_chain_data['delivery_performance'].unique().tolist())
            selected_delivery = st.selectbox("Delivery Performance", delivery_performances)
        else:
            delivery_performances = ['All']
            selected_delivery = 'All'
        
        # Quality status filter
        if 'quality_status' in supply_chain_data.columns:
            quality_statuses = ['All'] + sorted(supply_chain_data['quality_status'].unique().tolist())
            selected_quality = st.selectbox("Quality Status", quality_statuses)
        else:
            quality_statuses = ['All']
            selected_quality = 'All'
        
        # Apply filters
        filtered_data = supply_chain_data.copy()
        if len(date_range) == 2:
            # Convert date objects to pandas datetime for comparison
            start_date = pd.to_datetime(date_range[0])
            end_date = pd.to_datetime(date_range[1])
            filtered_data = filtered_data[
                (filtered_data['date'] >= start_date) & 
                (filtered_data['date'] <= end_date)
            ]
        
        if selected_supplier != 'All':
            filtered_data = filtered_data[filtered_data['supplier'] == selected_supplier]
            
        if selected_delivery != 'All' and 'delivery_performance' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['delivery_performance'] == selected_delivery]
            
        if selected_quality != 'All' and 'quality_status' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['quality_status'] == selected_quality]
    else:
        filtered_data = supply_chain_data

# KPI Metrics Section
st.markdown("### 📊 Key Supply Chain Indicators")

# Create columns for KPIs
col1, col2, col3, col4 = st.columns(4)

if not filtered_data.empty:
    try:
        total_orders = len(filtered_data)
        total_order_value = filtered_data['order_value'].sum()
        on_time_delivery_rate = (filtered_data['on_time_delivery'].sum() / total_orders * 100) if total_orders > 0 else 0
        avg_supplier_reliability = filtered_data['supplier_reliability'].mean()
    except Exception as e:
        st.error(f"Error calculating KPIs: {e}")
        st.stop()
else:
    total_orders = 0
    total_order_value = 0
    on_time_delivery_rate = 0
    avg_supplier_reliability = 0

with col1:
    st.metric(
        label="📦 Orders",
        value=format_count(total_orders) if total_orders > 0 else "No data",
        help="Total number of orders placed"
    )

with col2:
    st.metric(
        label="💰 Order Value",
        value=format_large_number(total_order_value) if total_order_value > 0 else "No data",
        help="Total value of all orders"
    )

with col3:
    st.metric(
        label="⏰ On-Time Rate",
        value=f"{on_time_delivery_rate:.1f}%" if on_time_delivery_rate > 0 else "No data",
        help="Percentage of orders delivered on time"
    )

with col4:
    st.metric(
        label="🏭 Reliability",
        value=f"{avg_supplier_reliability:.2f}" if avg_supplier_reliability > 0 else "No data",
        help="Average supplier reliability score"
    )

# Inventory Management Section
st.markdown("---")
st.markdown("### 📦 Inventory Management")

if not filtered_data.empty:
    try:
        # Order quantity trends over time
        order_trends = filtered_data.groupby('date').agg({
            'order_quantity': 'sum',
            'order_value': 'sum',
            'unit_cost': 'mean'
        }).reset_index()
        
        # Create Plotly line chart with smooth lines and pastel colors
        fig_orders = px.line(
            order_trends,
            x='date',
            y='order_quantity',
            title='Order Quantity Trends Over Time',
            labels={
                'date': 'Date',
                'order_quantity': 'Order Quantity',
            },
            color_discrete_sequence=px.colors.qualitative.Pastel,
            line_shape='spline'
        )
        
        # Update layout for better styling
        fig_orders.update_layout(
            title_font_size=16,
            plot_bgcolor=None,
            paper_bgcolor=None,
            font=dict(size=12),
            hovermode='x unified',
            margin=dict(l=50, r=50, t=80, b=80)
        )
        
        # Update traces for better line styling
        fig_orders.update_traces(
            line=dict(width=3),
            mode='lines+markers',
            marker=dict(size=6, opacity=0.7)
        )
        
        # Update axes styling
        fig_orders.update_xaxes(
            gridcolor='#f0f0f0',
            showgrid=True,
            zeroline=False
        )
        fig_orders.update_yaxes(
            gridcolor='#f0f0f0',
            showgrid=True,
            zeroline=False
        )
        
        st.plotly_chart(fig_orders, use_container_width=True, theme="streamlit")
        
        # Order value vs quantity analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Order value trends
            value_chart = alt.Chart(order_trends).mark_line(
                color=get_financial_color('revenue'),
                strokeWidth=3,
                point=True
            ).encode(
                x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %Y')),
                y=alt.Y('order_value:Q', title='Order Value ($)'),
                tooltip=[
                    alt.Tooltip('date:T', title='Date', format='%B %Y'),
                    alt.Tooltip('order_value:Q', title='Order Value ($)', format=',.0f')
                ]
            ).properties(
                title='Order Value Trends Over Time',
                height=300
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(value_chart, use_container_width=True)
        
        with col2:
            # Unit cost trends
            cost_chart = alt.Chart(order_trends).mark_line(
                color=get_financial_color('cost'),
                strokeWidth=3,
                point=True
            ).encode(
                x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %Y')),
                y=alt.Y('unit_cost:Q', title='Unit Cost ($)'),
                tooltip=[
                    alt.Tooltip('date:T', title='Date', format='%B %Y'),
                    alt.Tooltip('unit_cost:Q', title='Unit Cost ($)', format='.2f')
                ]
            ).properties(
                title='Unit Cost Trends Over Time',
                height=300
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(cost_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating inventory charts: {e}")

# Supplier Performance Section
st.markdown("---")
st.markdown("### 🏭 Supplier Performance")

if not filtered_data.empty:
    try:
        # Supplier performance metrics
        supplier_performance = filtered_data.groupby('supplier').agg({
            'order_value': 'sum',
            'supplier_reliability': 'mean',
            'sustainability_rating': 'mean',
            'on_time_delivery': 'mean',
            'quality_issues': 'sum'
        }).reset_index()
        
        # Calculate on-time delivery percentage
        supplier_performance['on_time_delivery_pct'] = supplier_performance['on_time_delivery'] * 100
        
        # Calculate dynamic axis domains with 10% padding
        min_x = supplier_performance['supplier_reliability'].min()
        max_x = supplier_performance['supplier_reliability'].max()
        x_padding = (max_x - min_x) * 0.1 if max_x > min_x else 0.1
        x_domain = [max(0, min_x - x_padding), min(1, max_x + x_padding)]

        min_y = supplier_performance['on_time_delivery_pct'].min()
        max_y = supplier_performance['on_time_delivery_pct'].max()
        y_padding = (max_y - min_y) * 0.1 if max_y > min_y else 1
        y_domain = [max(0, min_y - y_padding), min(100, max_y + y_padding)]

        # Create supplier performance bubble chart with dynamic axis domains
        supplier_chart = alt.Chart(supplier_performance).mark_circle(
            opacity=0.8,
            stroke='#cccccc',
            strokeWidth=0.5
        ).encode(
            x=alt.X('supplier_reliability:Q', 
                    title='Supplier Reliability',
                    scale=alt.Scale(domain=x_domain),
                    axis=alt.Axis(labelAngle=0)),
            y=alt.Y('on_time_delivery_pct:Q', 
                    title='On-Time Delivery Rate (%)',
                    scale=alt.Scale(domain=y_domain)),
            size=alt.Size('order_value:Q',
                          title='Order Value ($)',
                          scale=alt.Scale(range=[300, 2500])),
            color=alt.Color('sustainability_rating:Q', 
                           title='Sustainability Rating',
                           scale=alt.Scale(scheme='viridis')),
            tooltip=[
                alt.Tooltip('supplier:N', title='Supplier'),
                alt.Tooltip('supplier_reliability:Q', title='Reliability', format='.3f'),
                alt.Tooltip('on_time_delivery_pct:Q', title='On-Time %', format='.1f'),
                alt.Tooltip('sustainability_rating:Q', title='Sustainability', format='.1f'),
                alt.Tooltip('order_value:Q', title='Order Value ($)', format=',.0f')
            ]
        ).properties(
            title='Supplier Performance: Reliability, Delivery & Sustainability',
            width=600,
            height=450
        ).configure_title(
            fontSize=18,
            anchor='start',
            dy=-5
        ).configure_axis(
            gridColor=CSS_COLORS['neutral-dark']
        ).configure_view(
            stroke=None
        )
        
        st.altair_chart(supplier_chart, use_container_width=True)
        
        # Supplier reliability and sustainability breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            # Reliability by supplier
            reliability_chart = alt.Chart(supplier_performance).mark_bar(
                color=get_performance_color('good')
            ).encode(
                x=alt.X('supplier_reliability:Q', title='Reliability Score'),
                y=alt.Y('supplier:N', title='Supplier', sort='-x'),
                tooltip=[
                    alt.Tooltip('supplier:N', title='Supplier'),
                    alt.Tooltip('supplier_reliability:Q', title='Reliability', format='.3f')
                ]
            ).properties(
                title='Supplier Reliability Scores',
                height=300
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(reliability_chart, use_container_width=True)
        
        with col2:
            # Sustainability by supplier (horizontal bar)
            sustainability_chart = alt.Chart(supplier_performance).mark_bar(
                color=get_sustainability_color('recycled')
            ).encode(
                x=alt.X('sustainability_rating:Q', title='Sustainability Rating'),
                y=alt.Y('supplier:N', title='Supplier', sort='-x'),
                tooltip=[
                    alt.Tooltip('supplier:N', title='Supplier'),
                    alt.Tooltip('sustainability_rating:Q', title='Sustainability', format='.1f')
                ]
            ).properties(
                title='Supplier Sustainability Ratings',
                height=300
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(sustainability_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating supplier performance charts: {e}")

# Logistics Optimization Section
st.markdown("---")
st.markdown("### 🚚 Logistics Optimization")

if not filtered_data.empty:
    try:
        # Delivery performance analysis
        if 'delivery_performance' in filtered_data.columns:
            delivery_performance = filtered_data.groupby('delivery_performance').agg({
                'order_value': 'sum',
                'order_quantity': 'sum',
                'delivery_variance_days': 'mean'
            }).reset_index()
            
            # Create delivery performance chart (horizontal bar)
            delivery_chart = alt.Chart(delivery_performance).mark_bar(
                color=get_performance_color('average')
            ).encode(
                y=alt.Y('delivery_performance:N', title='Delivery Performance'),
                x=alt.X('order_value:Q', title='Total Order Value ($)'),
                tooltip=[
                    alt.Tooltip('delivery_performance:N', title='Performance'),
                    alt.Tooltip('order_value:Q', title='Order Value ($)', format=',.0f'),
                    alt.Tooltip('delivery_variance_days:Q', title='Avg. Variance (days)', format='.1f')
                ]
            ).properties(
                title='Order Value by Delivery Performance',
                height=300
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-dark']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(delivery_chart, use_container_width=True)
        else:
            st.info("Delivery performance data not available in current dataset")
        
        # Delivery variance analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Delivery variance distribution
            if 'delivery_variance_days' in filtered_data.columns:
                variance_data = filtered_data[filtered_data['delivery_variance_days'].notna()]
                
                variance_chart = alt.Chart(variance_data).mark_bar(
                    color=get_performance_color('average')
                ).encode(
                    y=alt.Y('delivery_variance_days:Q', 
                            title='Delivery Variance (days)',
                            bin=alt.Bin(maxbins=20)),
                    x=alt.X('count():Q', title='Number of Orders'),
                    tooltip=[
                        alt.Tooltip('delivery_variance_days:Q', title='Variance (days)', format='.1f'),
                        alt.Tooltip('count():Q', title='Number of Orders')
                    ]
                ).properties(
                    title='Distribution of Delivery Variance',
                    height=300
                ).configure_axis(
                    gridColor=CSS_COLORS['neutral-medium']
                ).configure_view(
                    strokeWidth=0
                )
                
                st.altair_chart(variance_chart, use_container_width=True)
            else:
                st.info("Delivery variance data not available")
        
        with col2:
            # Expected vs actual delivery analysis
            if 'expected_delivery_days' in filtered_data.columns and 'actual_delivery_days' in filtered_data.columns:
                delivery_comparison = filtered_data.groupby('date').agg({
                    'expected_delivery_days': 'mean',
                    'actual_delivery_days': 'mean'
                }).reset_index()
                
                # Melt for comparison chart
                delivery_melted = delivery_comparison.melt(
                    id_vars=['date'],
                    value_vars=['expected_delivery_days', 'actual_delivery_days'],
                    var_name='delivery_type',
                    value_name='days'
                )
                
                # Map names
                delivery_names = {
                    'expected_delivery_days': 'Expected',
                    'actual_delivery_days': 'Actual'
                }
                delivery_melted['delivery_type'] = delivery_melted['delivery_type'].map(delivery_names)
                
                comparison_chart = alt.Chart(delivery_melted).mark_line(
                    strokeWidth=2,
                    point=True
                ).encode(
                    x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %Y')),
                    y=alt.Y('days:Q', title='Delivery Days'),
                    color=alt.Color('delivery_type:N', 
                                  title='Delivery Type',
                                  scale=alt.Scale(range=[get_performance_color('poor'), get_performance_color('excellent')])),
                    tooltip=[
                        alt.Tooltip('date:T', title='Date', format='%B %Y'),
                        alt.Tooltip('delivery_type:N', title='Type'),
                        alt.Tooltip('days:Q', title='Days', format='.1f')
                    ]
                ).properties(
                    title='Expected vs Actual Delivery Days',
                    height=300
                ).configure_axis(
                    gridColor=CSS_COLORS['neutral-medium']
                ).configure_view(
                    strokeWidth=0
                )
                
                st.altair_chart(comparison_chart, use_container_width=True)
            else:
                st.info("Expected vs actual delivery data not available")
        
    except Exception as e:
        st.error(f"Error creating logistics charts: {e}")

# Material Tracking Section
st.markdown("---")
st.markdown("### ♻️ Material Tracking & Quality")

if not filtered_data.empty:
    try:
        # Quality analysis
        if 'quality_status' in filtered_data.columns:
            quality_analysis = filtered_data.groupby('quality_status').agg({
                'order_value': 'sum',
                'defect_quantity': 'sum',
                'order_quantity': 'sum'
            }).reset_index()
            
            # Calculate defect rate
            quality_analysis['defect_rate_pct'] = (
                quality_analysis['defect_quantity'] / 
                quality_analysis['order_quantity'] * 100
            )
            
            # Create quality status chart (horizontal bar)
            quality_chart = alt.Chart(quality_analysis).mark_bar(
                color=get_performance_color('average')
            ).encode(
                y=alt.Y('quality_status:N', title='Quality Status'),
                x=alt.X('order_value:Q', title='Order Value ($)'),
                tooltip=[
                    alt.Tooltip('quality_status:N', title='Quality Status'),
                    alt.Tooltip('order_value:Q', title='Order Value ($)', format=',.0f'),
                    alt.Tooltip('defect_rate_pct:Q', title='Defect Rate %', format='.2f')
                ]
            ).properties(
                title='Order Value by Quality Status',
                height=300
            ).configure_axis(
                gridColor=CSS_COLORS['neutral-medium']
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(quality_chart, use_container_width=True)
        else:
            st.info("Quality status data not available in current dataset")
        
        # Defect analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Defect rate by supplier
            if 'defect_quantity' in filtered_data.columns:
                defect_by_supplier = filtered_data.groupby('supplier').agg({
                    'defect_quantity': 'sum',
                    'order_quantity': 'sum'
                }).reset_index()
                
                defect_by_supplier['defect_rate_pct'] = (
                    defect_by_supplier['defect_quantity'] / 
                    defect_by_supplier['order_quantity'] * 100
                )
                
                defect_chart = alt.Chart(defect_by_supplier).mark_bar(
                    color=get_performance_color('poor')
                ).encode(
                    x=alt.X('defect_rate_pct:Q', title='Defect Rate (%)'),
                    y=alt.Y('supplier:N', title='Supplier', sort='-x'),
                    tooltip=[
                        alt.Tooltip('supplier:N', title='Supplier'),
                        alt.Tooltip('defect_rate_pct:Q', title='Defect Rate %', format='.2f'),
                        alt.Tooltip('defect_quantity:Q', title='Defect Quantity', format=',.0f')
                    ]
                ).properties(
                    title='Defect Rate by Supplier',
                    height=300
                ).configure_axis(
                    gridColor=CSS_COLORS['neutral-medium']
                ).configure_view(
                    strokeWidth=0
                )
                
                st.altair_chart(defect_chart, use_container_width=True)
            else:
                st.info("Defect quantity data not available")
        
        with col2:
            # Sustainability rating distribution
            if 'sustainability_category' in filtered_data.columns:
                sustainability_dist = filtered_data.groupby('sustainability_category').agg({
                    'order_value': 'sum',
                    'supplier_reliability': 'mean'
                }).reset_index()
                
                sustainability_chart = alt.Chart(sustainability_dist).mark_bar(
                    color=get_sustainability_color('recycled')
                ).encode(
                    y=alt.Y('sustainability_category:N', title='Sustainability Category'),
                    x=alt.X('order_value:Q', title='Order Value ($)'),
                    tooltip=[
                        alt.Tooltip('sustainability_category:N', title='Category'),
                        alt.Tooltip('order_value:Q', title='Order Value ($)', format=',.0f'),
                        alt.Tooltip('supplier_reliability:Q', title='Avg. Reliability', format='.3f')
                    ]
                ).properties(
                    title='Order Value by Sustainability Category',
                    height=300
                ).configure_axis(
                    gridColor=CSS_COLORS['neutral-medium']
                ).configure_view(
                    strokeWidth=0
                )
                
                st.altair_chart(sustainability_chart, use_container_width=True)
            else:
                st.info("Sustainability category data not available")
        
    except Exception as e:
        st.error(f"Error creating material tracking charts: {e}")

# Data Summary Section
st.markdown("---")
st.markdown("### 📋 Supply Chain Data Summary")

if not filtered_data.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Data Coverage:**")
        st.write(f"- **Time Period:** {filtered_data['date'].min().strftime('%B %Y')} to {filtered_data['date'].max().strftime('%B %Y')}")
        st.write(f"- **Suppliers:** {len(filtered_data['supplier'].unique())}")
        st.write(f"- **Orders:** {len(filtered_data):,}")
        st.write(f"- **Total Order Value:** ${filtered_data['order_value'].sum():,.0f}")
    
    with col2:
        st.markdown("**Key Insights:**")
        st.write("- Supplier performance and reliability tracking")
        st.write("- Delivery performance optimization")
        st.write("- Quality control and defect management")
        st.write("- Sustainability rating analysis")

# Footer navigation
st.markdown("---")
if st.button("🏠 Back to Home"):
    st.switch_page("Home.py") 