import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from data_connector import load_esg_data

st.set_page_config(
    page_title="ESG Insights - EcoMetrics",
    page_icon="🌱",
)

st.title("🌱 ESG Insights")
st.markdown("---")

# Page description
st.markdown("""
## 🌱 ESG Performance Insights
Analyze key environmental, social, and governance metrics. 
Use the filters in the sidebar to drill down into specific product lines or time periods.
""")

# Load ESG data
@st.cache_data(ttl=3600)
def load_cached_esg_data():
    return load_esg_data()

with st.spinner("Loading ESG data..."):
    esg_data, status_message = load_cached_esg_data()

if esg_data.empty:
    st.error(f"No ESG data available: {status_message}")
    st.stop()

# Display data status
st.sidebar.success(f"Data loaded: {status_message}")

# Sidebar filters
with st.sidebar:
    st.markdown("### 🔍 Filters")
    
    # Date range filter
    if not esg_data.empty:
        min_date = esg_data['date'].min()
        max_date = esg_data['date'].max()
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Product line filter
        product_lines = ['All'] + sorted(esg_data['product_line'].unique().tolist())
        selected_product = st.selectbox("Product Line", product_lines)
        
        # Facility filter
        facilities = ['All'] + sorted(esg_data['facility'].unique().tolist())
        selected_facility = st.selectbox("Facility", facilities)
        
        # Apply filters
        filtered_data = esg_data.copy()
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
            
        if selected_facility != 'All':
            filtered_data = filtered_data[filtered_data['facility'] == selected_facility]
    else:
        filtered_data = esg_data

# KPI Metrics Section
st.markdown("### 📊 Key Performance Indicators")

# Create columns for KPIs
col1, col2, col3, col4 = st.columns(4)

if not filtered_data.empty:
    try:
        total_emissions = filtered_data['total_emissions_kg_co2'].sum()
        avg_recycled = filtered_data['avg_recycled_material_pct'].mean()
        total_waste = filtered_data['total_waste_generated_kg'].sum()
        avg_renewable = filtered_data['avg_renewable_energy_pct'].mean()
    except Exception as e:
        st.error(f"Error calculating KPIs: {e}")
        st.stop()
else:
    total_emissions = 0
    avg_recycled = 0
    total_waste = 0
    avg_renewable = 0

with col1:
    st.metric(
        label="Total CO2 Emissions (kg)",
        value=f"{total_emissions:,.0f}" if total_emissions > 0 else "No data",
        help="Total carbon dioxide emissions across all operations"
    )

with col2:
    st.metric(
        label="Avg. Recycled Material (%)",
        value=f"{avg_recycled:.1f}%" if avg_recycled > 0 else "No data",
        help="Average percentage of recycled materials used"
    )

with col3:
    st.metric(
        label="Total Waste Generated (kg)",
        value=f"{total_waste:,.0f}" if total_waste > 0 else "No data",
        help="Total waste generated across all operations"
    )

with col4:
    st.metric(
        label="Avg. Renewable Energy (%)",
        value=f"{avg_renewable:.1f}%" if avg_renewable > 0 else "No data",
        help="Average percentage of renewable energy used"
    )

# ESG Trends Section
st.markdown("---")
st.markdown("### 📈 ESG Trends Over Time")

if not filtered_data.empty:
    try:
        # CO2 Emissions by Product Line (Plotly version)
        emissions_by_product = filtered_data.groupby(['date', 'product_line'])['total_emissions_kg_co2'].sum().reset_index()
        
        # Create Plotly line chart with smooth lines and pastel colors
        fig_emissions = px.line(
            emissions_by_product,
            x='date',
            y='total_emissions_kg_co2',
            color='product_line',
            title='CO2 Emissions Over Time by Product Line',
            labels={
                'date': 'Date',
                'total_emissions_kg_co2': 'CO2 Emissions (kg)',
                'product_line': 'Product Line'
            },
            color_discrete_sequence=px.colors.qualitative.Pastel,  # Pastel color palette
            line_shape='spline'  # Smooth lines
        )
        
        # Update layout for better styling
        fig_emissions.update_layout(
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
        fig_emissions.update_traces(
            line=dict(width=3),
            mode='lines+markers',
            marker=dict(size=6, opacity=0.7)
        )
        
        # Update axes styling
        fig_emissions.update_xaxes(
            gridcolor='#f0f0f0',
            showgrid=True,
            zeroline=False
        )
        fig_emissions.update_yaxes(
            gridcolor='#f0f0f0',
            showgrid=True,
            zeroline=False
        )
        
        st.plotly_chart(fig_emissions, use_container_width=True, theme="streamlit")
        
        # Prepare data for recycled and renewable trends (grouped by date)
        trends_data = filtered_data.groupby('date').agg({
            'avg_recycled_material_pct': 'mean',
            'avg_renewable_energy_pct': 'mean',
            'total_waste_generated_kg': 'sum'
        }).reset_index()
        
        # Recycled Material and Renewable Energy Trends
        col1, col2 = st.columns(2)
        
        with col1:
            recycled_chart = alt.Chart(trends_data).mark_line(
                color='#4ECDC4',
                strokeWidth=3,
                point=True
            ).encode(
                x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %Y')),
                y=alt.Y('avg_recycled_material_pct:Q', title='Recycled Material (%)'),
                tooltip=[
                    alt.Tooltip('date:T', title='Date', format='%B %Y'),
                    alt.Tooltip('avg_recycled_material_pct:Q', title='Recycled %', format='.1f')
                ]
            ).properties(
                title='Recycled Material Usage Trend',
                height=250
            ).configure_axis(
                gridColor='#f0f0f0'
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(recycled_chart, use_container_width=True)
        
        with col2:
            renewable_chart = alt.Chart(trends_data).mark_line(
                color='#45B7D1',
                strokeWidth=3,
                point=True
            ).encode(
                x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %Y')),
                y=alt.Y('avg_renewable_energy_pct:Q', title='Renewable Energy (%)'),
                tooltip=[
                    alt.Tooltip('date:T', title='Date', format='%B %Y'),
                    alt.Tooltip('avg_renewable_energy_pct:Q', title='Renewable %', format='.1f')
                ]
            ).properties(
                title='Renewable Energy Usage Trend',
                height=250
            ).configure_axis(
                gridColor='#f0f0f0'
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(renewable_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating trend charts: {e}")

# Material Composition Section  
st.markdown("---")
st.markdown("### ♻️ Material Composition Analysis")

if not filtered_data.empty:
    try:
        # Material composition by product line
        material_data = filtered_data.groupby('product_line').agg({
            'avg_recycled_material_pct': 'mean',
            'avg_virgin_material_pct': 'mean'
        }).reset_index()
        
        # Show a sample of the material composition data for debugging
        with st.expander("Show material composition data sample"):
            st.dataframe(material_data)
        
        # Melt the data for stacked bar chart
        material_melted = material_data.melt(
            id_vars=['product_line'],
            value_vars=['avg_recycled_material_pct', 'avg_virgin_material_pct'],
            var_name='material_type',
            value_name='percentage'
        )
        
        # Map legend names for readability
        legend_names = {
            'avg_recycled_material_pct': 'Recycled Material (%)',
            'avg_virgin_material_pct': 'Virgin Material (%)'
        }
        material_melted['material_type'] = material_melted['material_type'].map(legend_names)
        
        # Create stacked bar chart
        material_chart = alt.Chart(material_melted).mark_bar().encode(
            x=alt.X('product_line:N', title='Product Line', sort='-y'),
            y=alt.Y('percentage:Q', title='Percentage (%)', stack='zero'),
            color=alt.Color('material_type:N', 
                          title='Material Type',
                          scale=alt.Scale(range=['#4ECDC4', '#FFA07A'])),
            tooltip=[
                alt.Tooltip('product_line:N', title='Product Line'),
                alt.Tooltip('material_type:N', title='Material Type'),
                alt.Tooltip('percentage:Q', title='Percentage', format='.1f')
            ]
        ).properties(
            title='Material Composition by Product Line',
            height=450
        ).configure_title(
            fontSize=16
        ).configure_axis(
            gridColor='#f0f0f0'
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(material_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating material composition chart: {e}")

# Facility Performance Section
st.markdown("---")
st.markdown("### 🏭 Facility Performance Comparison")

if not filtered_data.empty:
    try:
        # Facility performance metrics
        facility_data = filtered_data.groupby('facility').agg({
            'overall_emissions_per_unit': 'mean',
            'avg_recycled_material_pct': 'mean',
            'avg_renewable_energy_pct': 'mean',
            'overall_water_recycling_pct': 'mean'
        }).reset_index()
        
        # Create a bubble chart to show multiple dimensions of facility performance
        facility_bubble_chart = alt.Chart(facility_data).mark_circle(
            opacity=0.8,
            stroke='#cccccc',
            strokeWidth=0.5
        ).encode(
            x=alt.X('overall_emissions_per_unit:Q', 
                    title='Emissions per Unit',
                    axis=alt.Axis(labelAngle=0)),
            y=alt.Y('avg_recycled_material_pct:Q', 
                    title='Recycled Material (%)'),
            size=alt.Size('avg_renewable_energy_pct:Q',
                          title='Renewable Energy Use (%)',
                          scale=alt.Scale(range=[100, 1000])),
            color=alt.Color('facility:N', 
                           title='Facility',
                           scale=alt.Scale(scheme='pastel1')),
            tooltip=[
                alt.Tooltip('facility:N', title='Facility'),
                alt.Tooltip('overall_emissions_per_unit:Q', title='Emissions/Unit', format='.3f'),
                alt.Tooltip('avg_recycled_material_pct:Q', title='Recycled Material (%)', format='.1f'),
                alt.Tooltip('avg_renewable_energy_pct:Q', title='Renewable Energy (%)', format='.1f')
            ]
        ).properties(
            title='Facility Performance: Emissions, Recycling & Renewables',
            height=400
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
        
        st.altair_chart(facility_bubble_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating facility performance chart: {e}")

# Regional Analysis Section
st.markdown("---")
st.markdown("### 🌍 Regional Performance Analysis")

if not filtered_data.empty:
    try:
        # Regional performance
        regional_data = filtered_data.groupby('facility_region').agg({
            'total_emissions_kg_co2': 'sum',
            'avg_recycled_material_pct': 'mean',
            'avg_renewable_energy_pct': 'mean',
            'total_waste_generated_kg': 'sum'
        }).reset_index()
        
        # Create horizontal bar chart for regional emissions
        regional_emissions = alt.Chart(regional_data).mark_bar(
            color='#FF6B6B'
        ).encode(
            x=alt.X('total_emissions_kg_co2:Q', title='Total Emissions (kg)'),
            y=alt.Y('facility_region:N', title='Region', sort='-x'),
            tooltip=[
                alt.Tooltip('facility_region:N', title='Region'),
                alt.Tooltip('total_emissions_kg_co2:Q', title='Emissions (kg)', format=',.0f')
            ]
        ).properties(
            title='Total Emissions by Region',
            height=200
        ).configure_title(
            fontSize=16
        ).configure_axis(
            gridColor='#f0f0f0'
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(regional_emissions, use_container_width=True)
        
        # Regional sustainability metrics
        col1, col2 = st.columns(2)
        
        with col1:
            regional_recycled = alt.Chart(regional_data).mark_bar(
                color='#4ECDC4'
            ).encode(
                x=alt.X('avg_recycled_material_pct:Q', title='Recycled Material (%)'),
                y=alt.Y('facility_region:N', title='Region', sort='-x'),
                tooltip=[
                    alt.Tooltip('facility_region:N', title='Region'),
                    alt.Tooltip('avg_recycled_material_pct:Q', title='Recycled %', format='.1f')
                ]
            ).properties(
                title='Recycled Material by Region',
                height=200
            ).configure_title(
                fontSize=16
            ).configure_axis(
                gridColor='#f0f0f0'
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(regional_recycled, use_container_width=True)
        
        with col2:
            regional_renewable = alt.Chart(regional_data).mark_bar(
                color='#45B7D1'
            ).encode(
                x=alt.X('avg_renewable_energy_pct:Q', title='Renewable Energy (%)'),
                y=alt.Y('facility_region:N', title='Region', sort='-x'),
                tooltip=[
                    alt.Tooltip('facility_region:N', title='Region'),
                    alt.Tooltip('avg_renewable_energy_pct:Q', title='Renewable %', format='.1f')
                ]
            ).properties(
                title='Renewable Energy by Region',
                height=200
            ).configure_title(
                fontSize=16
            ).configure_axis(
                gridColor='#f0f0f0'
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(regional_renewable, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating regional analysis charts: {e}")

# Data Summary Section
st.markdown("---")
st.markdown("### 📋 Data Summary")

if not filtered_data.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Data Coverage:**")
        st.write(f"- **Time Period:** {filtered_data['date'].min().strftime('%B %Y')} to {filtered_data['date'].max().strftime('%B %Y')}")
        st.write(f"- **Product Lines:** {len(filtered_data['product_line'].unique())}")
        st.write(f"- **Facilities:** {len(filtered_data['facility'].unique())}")
        st.write(f"- **Data Points:** {len(filtered_data):,}")
    
    with col2:
        st.markdown("**Key Insights:**")
        st.write("- CO2 emissions tracking across all operations")
        st.write("- Recycled material usage optimization")
        st.write("- Renewable energy adoption rates")
        st.write("- Regional performance comparisons")

# Footer navigation
st.markdown("---")
if st.button("🏠 Back to Home"):
    st.switch_page("Home.py") 