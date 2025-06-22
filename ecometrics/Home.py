import streamlit as st
from streamlit import navigation
from data_connector import check_dbt_availability

# Configure the page
st.set_page_config(
    page_title="EcoMetrics - Business Intelligence Portfolio",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #888;
        text-align: center;
        margin-bottom: 3rem;
    }
    .feature-card {
        background-color: transparent;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .status-card {
        background-color: rgba(31, 119, 180, 0.15); /* Adjusted for dark theme */
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Check dbt availability
availability = check_dbt_availability()

# Main content
st.markdown('<h1 class="main-header">🌱 EcoMetrics</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Business Intelligence Portfolio Dashboard</p>', unsafe_allow_html=True)

# Display connection status
if availability['available']:
    st.markdown(f"""
    <div class="status-card">
        <h4>✅ Data Pipeline Connected</h4>
        <p>{availability['message']}</p>
        <small>Database: {availability['db_path']}</small>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="status-card">
        <h4>⚠️ Data Pipeline Not Available</h4>
        <p>{availability['message']}</p>
        <small>Database: {availability['db_path']}</small>
        <br><small><strong>Note:</strong> {availability.get('deployment_note', '')}</small>
    </div>
    """, unsafe_allow_html=True)

# Introduction
st.markdown("""
Welcome to EcoMetrics, your comprehensive business intelligence dashboard that combines 
environmental, social, and governance (ESG) insights with financial analysis and supply chain optimization.
""")

# Feature overview
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🌱 ESG Insights</h3>
        <p>Explore sustainability metrics, environmental impact analysis, and ESG performance tracking.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>💰 Financial Analysis</h3>
        <p>Comprehensive financial forecasting, profit margin analysis, and revenue optimization.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>🔄 Supply Chain Insights</h3>
        <p>Supply chain optimization, material tracking, and operational efficiency analysis.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>👥 Customer Insights</h3>
        <p>Customer behavior analysis, segmentation, and engagement metrics.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Data Browser</h3>
        <p>Explore raw data, dbt models, and perform ad-hoc analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>📈 Forecasting</h3>
        <p>Advanced forecasting models for business planning and decision making.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with Streamlit • Powered by dbt • Data-driven insights</p>
</div>
""", unsafe_allow_html=True) 