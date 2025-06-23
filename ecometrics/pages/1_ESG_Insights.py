import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_connector import load_esg_data

st.set_page_config(
    page_title="ESG Insights - EcoMetrics",
    page_icon="🌱",
    layout="wide"
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
st.cache_data(ttl=3600)
with st.spinner("Loading ESG data..."):
    esg_data, status_message = load_esg_data()

if esg_data.empty:
    st.error(f"No ESG data available: {status_message}")
    st.stop()

# Display data status
st.sidebar.success(f"Data loaded: {status_message}")

# Placeholder for sidebar filters (to be implemented later)
with st.sidebar:
    st.markdown("### 🔍 Filters")
    st.info("Filters will be implemented here")

# KPI Metrics Section
st.markdown("### 📊 Key Performance Indicators")

# Create columns for KPIs
col1, col2, col3 = st.columns(3)

if not esg_data.empty:
  try:  
    total_emissions = esg_data['total_emissions_kg_co2'].sum()
    avg_recycled = esg_data['avg_recycled_material_pct'].mean()
    total_waste = esg_data['total_waste_generated_kg'].sum()
  except Exception as e:
    st.error(f"Error calculating KPIs: {e}")
    st.stop()
else:
  total_emissions = 0
  avg_recycled = 0
  total_waste = 0

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

# ESG Trends Section
st.markdown("---")
st.markdown("### 📈 ESG Trends Over Time")

# Create CO2 emissions line chart
if not esg_data.empty:
    try:
        # Prepare data for the line chart
        # Group by date and sum emissions across all product lines/facilities
        emissions_trend = esg_data.groupby('date')['total_emissions_kg_co2'].sum().reset_index()
        emissions_trend = emissions_trend.sort_values('date')
        
        # Create the line chart
        st.line_chart(
            emissions_trend.set_index('date')['total_emissions_kg_co2'],
            use_container_width=True
        )
        
        st.caption("📊 Total CO2 emissions over time across all operations")
        
    except Exception as e:
        st.error(f"Error creating emissions chart: {e}")
        st.write("This section will show trends for:")
        st.write("- CO2 emissions over time")
        st.write("- Recycled material usage trends")
        st.write("- Waste generation patterns")
else:
    st.info("No data available for emissions trend chart")
    st.write("This section will show trends for:")
    st.write("- CO2 emissions over time")
    st.write("- Recycled material usage trends")
    st.write("- Waste generation patterns")

# Material Composition Section  
st.markdown("---")
st.markdown("### ♻️ Material Composition")

# Placeholder for material composition chart
st.info("📊 Material composition visualization will be displayed here")
st.write("This section will show:")
st.write("- Breakdown of materials used")
st.write("- Recycled vs virgin material ratios")
st.write("- Material type distribution")

# Additional ESG Sections (placeholders for future expansion)
st.markdown("---")
st.markdown("### 🌍 Environmental Impact")
st.info("Environmental impact metrics will be displayed here")

st.markdown("### 👥 Social Responsibility")
st.info("Social responsibility metrics will be displayed here")

st.markdown("### 🏛️ Governance Performance")
st.info("Governance performance metrics will be displayed here")

# Data information section
st.markdown("---")
st.markdown("### 📋 Data Sources")
st.write("- ESG transaction data")
st.write("- Sustainability reports")
st.write("- Environmental impact assessments")
st.write("- Social responsibility initiatives")

# Footer navigation
st.markdown("---")
if st.button("🏠 Back to Home"):
    st.switch_page("Home.py") 