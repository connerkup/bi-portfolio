"""
Combined Insights Page

This page provides integrated ESG and financial insights for PackagingCo.
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

# Import shared controls
from components.shared_controls import setup_sidebar_controls

# Setup sidebar controls
setup_sidebar_controls()

def display_charts_responsive(charts_data, titles=None):
    """Display charts stacked vertically, full width."""
    for i, chart in enumerate(charts_data):
        if titles and i < len(titles):
            st.subheader(titles[i])
        st.plotly_chart(chart, use_container_width=True)

# Check for data availability
if 'filtered_esg' not in st.session_state or 'filtered_finance' not in st.session_state:
    st.warning("Data is being filtered, please wait...")
    st.info("Please return to the main page to load and filter data.")
else:
    # Page content
    esg_data = st.session_state.filtered_esg
    finance_data = st.session_state.filtered_finance

    if esg_data.empty or finance_data.empty:
        st.warning("No data available for the selected filters.")
        st.info("Please adjust the filters in the sidebar.")
    else:
        # Combined insights content
        st.markdown("## 🔄 ESG-Finance Combined Insights")
        st.markdown("""
        ### 🎯 Integrated Analysis
        This section explores the relationship between ESG performance and financial outcomes, 
        helping identify win-win opportunities for sustainability and profitability.
        """)

        merged_data = pd.merge(
            esg_data.groupby('product_line').agg({
                'total_emissions_kg_co2': 'sum',
                'avg_recycled_material_pct': 'mean',
                'avg_recycling_rate_pct': 'mean'
            }).reset_index(),
            finance_data.groupby('product_line').agg({
                'total_revenue': 'sum',
                'total_profit_margin': 'sum',
                'avg_profit_margin_pct': 'mean'
            }).reset_index(),
            on='product_line'
        )

        st.subheader("🌱 ESG vs Financial Performance")

        emissions_vs_revenue_fig = px.scatter(
            merged_data, 
            x='total_emissions_kg_co2', 
            y='total_revenue', 
            size='total_profit_margin', 
            color='product_line', 
            title="Emissions vs Revenue", 
            labels={'total_emissions_kg_co2': 'Total CO2 Emissions (kg)', 'total_revenue': 'Total Revenue ($)'}
        )

        recycled_vs_margin_fig = px.scatter(
            merged_data, 
            x='avg_recycled_material_pct', 
            y='avg_profit_margin_pct', 
            size='total_revenue', 
            color='product_line', 
            title="Recycled Material % vs Profit Margin %", 
            labels={'avg_recycled_material_pct': 'Recycled Material %', 'avg_profit_margin_pct': 'Profit Margin %'}
        )

        # Display charts using responsive function
        display_charts_responsive([emissions_vs_revenue_fig, recycled_vs_margin_fig], ["Emissions vs Revenue", "Recycled Material % vs Profit Margin %"])

        st.subheader("📊 Correlation Analysis")

        correlations = merged_data[['total_emissions_kg_co2', 'avg_recycled_material_pct', 'avg_recycling_rate_pct', 'total_revenue', 'total_profit_margin', 'avg_profit_margin_pct']].corr()
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
        ### 💡 Win-Win Opportunities
        - **Invest in Paper Packaging:** High recycled content, good margins
        - **Optimize Glass Production:** Reduce emissions while maintaining quality
        - **Scale Plastic Recycling:** Increase recycled content in plastic containers
        - **Regional Strategy:** Focus on high-margin regions with ESG initiatives
        """) 