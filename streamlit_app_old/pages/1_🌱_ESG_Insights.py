"""
ESG Insights Page

This page provides detailed ESG and sustainability insights for PackagingCo.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add the project root to the path to allow importing from 'streamlit_app'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from packagingco_insights.analysis.esg_analysis import ESGAnalyzer
from packagingco_insights.utils.visualization import plot_esg_trends, plot_material_composition

# Import shared controls
from components.shared_controls import setup_sidebar_controls

def show_esg_insights(esg_data):
    """Renders the ESG insights page."""
    st.markdown("## 🌱 ESG Performance Insights")
    st.markdown(
        "Analyze key environmental, social, and governance metrics. "
        "Use the filters in the sidebar to drill down into specific product lines or time periods."
    )

    analyzer = ESGAnalyzer(esg_data)
    summary = analyzer.get_summary()

    # Create simple columns for KPIs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total CO2 Emissions (kg)", 
            f"{summary['total_emissions_kg_co2']:,}"
        )
    with col2:
        st.metric(
            "Avg. Recycled Material (%)", 
            f"{summary['avg_recycled_material_pct']:.2f}%"
        )
    with col3:
        st.metric(
            "Total Waste Generated (kg)",
            f"{summary['total_waste_generated_kg']:,}"
        )

    st.markdown("### 📈 ESG Trends Over Time")

    fig = plot_esg_trends(analyzer.data)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### ♻️ Material Composition")
    
    material_fig = plot_material_composition(analyzer.data)
    st.plotly_chart(material_fig, use_container_width=True)

# Setup sidebar controls
setup_sidebar_controls()

# Wait for data to be filtered
if 'filtered_esg' not in st.session_state:
    st.warning("Data is being filtered, please wait...")
    st.stop()

# Page content
filtered_esg = st.session_state.filtered_esg
if filtered_esg.empty:
    st.warning("No ESG data available for the selected filters.")
else:
    show_esg_insights(filtered_esg)