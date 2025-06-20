"""
ESG Insights Page

This page provides detailed ESG and sustainability insights for PackagingCo.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from packagingco_insights.analysis import ESGAnalyzer
from packagingco_insights.utils import create_kpi_card, display_charts_responsive

def main():
    """ESG Insights page main function."""
    
    st.title("🌱 ESG & Sustainability Insights")
    
    # Check if data is available in session state
    if 'filtered_esg' not in st.session_state:
        st.error("No ESG data available. Please return to the main page to load data.")
        st.info("The main page loads and filters the data for all pages.")
        return
    
    esg_data = st.session_state.filtered_esg
    
    if esg_data.empty:
        st.warning("No ESG data available for the selected filters.")
        return
    
    esg_analyzer = ESGAnalyzer(esg_data)
    
    st.subheader("📊 Key ESG Metrics")
    
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
    
    st.subheader("📊 ESG Performance Charts")
    
    # Correct date column for grouping
    emissions_fig = esg_analyzer.generate_emissions_chart('product_line', 'date')
    materials_fig = esg_analyzer.generate_materials_chart()
    
    display_charts_responsive([emissions_fig, materials_fig])
    
    st.subheader("🏆 ESG Performance Score")
    
    esg_scores = esg_analyzer.calculate_esg_score()
    avg_esg_score = esg_scores['esg_score'].mean()
    
    # Use a gauge chart for the average score
    st.metric("Average ESG Score", f"{avg_esg_score:.1f}/100")
    
    product_scores = esg_scores.groupby('product_line')['esg_score'].mean().sort_values(ascending=False)
    product_scores_fig = px.bar(product_scores, x=product_scores.index, y=product_scores.values, title="ESG Score by Product Line", text_auto=True)
    product_scores_fig.update_traces(texttemplate='%{y:.2s}', textangle=0, textposition="outside")

    component_scores = {
        'Emissions': esg_scores['emissions_score'].mean(),
        'Energy': esg_scores['energy_score'].mean(),
        'Materials': esg_scores['materials_score'].mean(),
        'Waste': esg_scores['waste_score'].mean()
    }
    component_scores_fig = px.bar(x=component_scores.keys(), y=component_scores.values(), title="ESG Score Components", text_auto=True)
    component_scores_fig.update_traces(texttemplate='%{y:.2f}', textangle=0, textposition="outside")

    display_charts_responsive([product_scores_fig, component_scores_fig])
    
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

if __name__ == "__main__":
    main() 