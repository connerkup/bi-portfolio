import streamlit as st
from streamlit import navigation
from data_connector import check_dbt_availability

# Configure the page
st.set_page_config(
    page_title="EcoMetrics - Business Intelligence Portfolio",
    page_icon="🌱",
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
    .creator-card {
        background: linear-gradient(135deg, rgba(31, 119, 180, 0.1), rgba(69, 183, 209, 0.1));
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #1f77b4;
        margin: 2rem 0;
        text-align: center;
    }
    .creator-name {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .creator-title {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 1rem;
    }
    .creator-description {
        font-size: 1rem;
        color: #888;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    .portfolio-link {
        display: inline-block;
        background-color: #1f77b4;
        color: white;
        padding: 0.75rem 1.5rem;
        text-decoration: none;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
        margin-top: 1rem;
    }
    .portfolio-link:hover {
        background-color: #45B7D1;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(31, 119, 180, 0.3);
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
    if st.button("\n🌱 ESG Insights\n\nExplore sustainability metrics, environmental impact analysis, and ESG performance tracking.\n", key="esg_card"):
        st.switch_page("pages/1_ESG_Insights.py")
    st.markdown("""
    <style>
    div[data-testid="stButton"][key="esg_card"] button {
        width: 100%;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #1f77b4;
        margin-bottom: 1rem;
        background-color: transparent;
        color: inherit;
        font-size: 1.1rem;
        text-align: left;
        transition: background 0.2s;
    }
    div[data-testid="stButton"][key="esg_card"] button:hover {
        background: rgba(31, 119, 180, 0.08);
        border-color: #45B7D1;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("\n💰 Financial Analysis\n\nComprehensive financial forecasting, profit margin analysis, and revenue optimization.\n", key="finance_card"):
        st.switch_page("pages/2_Financial_Analysis.py")
    st.markdown("""
    <style>
    div[data-testid="stButton"][key="finance_card"] button {
        width: 100%;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #1f77b4;
        margin-bottom: 1rem;
        background-color: transparent;
        color: inherit;
        font-size: 1.1rem;
        text-align: left;
        transition: background 0.2s;
    }
    div[data-testid="stButton"][key="finance_card"] button:hover {
        background: rgba(31, 119, 180, 0.08);
        border-color: #45B7D1;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("\n🔄 Supply Chain Insights\n\nSupply chain optimization, material tracking, and operational efficiency analysis.\n", key="supply_card"):
        st.switch_page("pages/3_Supply_Chain_Insights.py")
    st.markdown("""
    <style>
    div[data-testid="stButton"][key="supply_card"] button {
        width: 100%;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #1f77b4;
        margin-bottom: 1rem;
        background-color: transparent;
        color: inherit;
        font-size: 1.1rem;
        text-align: left;
        transition: background 0.2s;
    }
    div[data-testid="stButton"][key="supply_card"] button:hover {
        background: rgba(31, 119, 180, 0.08);
        border-color: #45B7D1;
    }
    </style>
    """, unsafe_allow_html=True)

with col2:
    if st.button("\n👥 Customer Insights\n\nCustomer behavior analysis, segmentation, and engagement metrics.\n", key="customer_card"):
        st.switch_page("pages/4_Customer_Insights.py")
    st.markdown("""
    <style>
    div[data-testid="stButton"][key="customer_card"] button {
        width: 100%;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #1f77b4;
        margin-bottom: 1rem;
        background-color: transparent;
        color: inherit;
        font-size: 1.1rem;
        text-align: left;
        transition: background 0.2s;
    }
    div[data-testid="stButton"][key="customer_card"] button:hover {
        background: rgba(31, 119, 180, 0.08);
        border-color: #45B7D1;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("\n📊 Data Browser\n\nExplore raw data, dbt models, and perform ad-hoc analysis.\n", key="data_card"):
        st.switch_page("pages/5_Data_Browser.py")
    st.markdown("""
    <style>
    div[data-testid="stButton"][key="data_card"] button {
        width: 100%;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #1f77b4;
        margin-bottom: 1rem;
        background-color: transparent;
        color: inherit;
        font-size: 1.1rem;
        text-align: left;
        transition: background 0.2s;
    }
    div[data-testid="stButton"][key="data_card"] button:hover {
        background: rgba(31, 119, 180, 0.08);
        border-color: #45B7D1;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("\n📈 Forecasting\n\nAdvanced forecasting models for business planning and decision making.\n", key="forecast_card"):
        st.switch_page("pages/6_Forecasting.py")
    st.markdown("""
    <style>
    div[data-testid="stButton"][key="forecast_card"] button {
        width: 100%;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #1f77b4;
        margin-bottom: 1rem;
        background-color: transparent;
        color: inherit;
        font-size: 1.1rem;
        text-align: left;
        transition: background 0.2s;
    }
    div[data-testid="stButton"][key="forecast_card"] button:hover {
        background: rgba(31, 119, 180, 0.08);
        border-color: #45B7D1;
    }
    </style>
    """, unsafe_allow_html=True)

# Creator Section
st.markdown("---")
st.markdown("## 👨‍💻 About the Creator")

st.markdown("""
<div class="creator-card">
    <div class="creator-name">👨‍💻 Conner Kupferberg</div>
    <div class="creator-title">Data Scientist & Business Intelligence Developer</div>
    <div class="creator-description">
        Passionate about leveraging data to drive sustainable business decisions and create meaningful insights. 
        This dashboard showcases expertise in data engineering, analytics, and visualization using modern BI tools 
        including dbt, Streamlit, and advanced forecasting techniques.
    </div>
    <a href="https://connerkupferberg.com" target="_blank" class="portfolio-link">
        🌐 View My Portfolio
    </a>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with Streamlit • Powered by dbt • Data-driven insights</p>
</div>
""", unsafe_allow_html=True) 