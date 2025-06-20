"""
Forecasting Page

This page provides sales forecasting and projections for PackagingCo.
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

from packagingco_insights.analysis import SalesForecaster

# Import shared controls
from components.shared_controls import setup_sidebar_controls

# Setup sidebar controls
setup_sidebar_controls()

def check_model_availability():
    """Check which advanced forecasting models are available."""
    models_available = {
        'prophet': False,
        'statsmodels': False,
        'pmdarima': False
    }
    
    try:
        from prophet import Prophet
        models_available['prophet'] = True
    except ImportError:
        pass
    
    try:
        from statsmodels.tsa.arima.model import ARIMA
        models_available['statsmodels'] = True
    except ImportError:
        pass
    
    try:
        from pmdarima import auto_arima  # type: ignore
        models_available['pmdarima'] = True
    except ImportError:
        pass
    
    return models_available

# Check for data availability
if 'filtered_sales' not in st.session_state:
    st.warning("Data is being filtered, please wait...")
    st.info("Please return to the main page to load and filter data.")
else:
    # Page content
    sales_data = st.session_state.filtered_sales
    
    if sales_data.empty:
        st.warning("No sales data available for the selected filters.")
        st.info("Please adjust the filters in the sidebar.")
    else:
        # Check model availability
        models_available = check_model_availability()

        forecaster = SalesForecaster(sales_data)

        st.subheader("⚙️ Forecasting Controls")

        # Forecasting parameters
        col1, col2, col3 = st.columns(3)
        with col1:
            forecast_periods = st.slider("Forecast Periods", 3, 12, 6)
        with col2:
            forecast_method = st.selectbox(
                "Forecast Method", 
                [
                    "Exponential Smoothing", 
                    "Moving Average",
                    "Prophet (Advanced)" if models_available['prophet'] else "Prophet (Not Available)",
                    "ARIMA (Advanced)" if models_available['statsmodels'] else "ARIMA (Not Available)",
                    "Auto-ARIMA (Advanced)" if models_available['pmdarima'] else "Auto-ARIMA (Not Available)"
                ]
            )
        with col3:
            compare_models = st.checkbox("Compare Multiple Models", value=False)

        # Model comparison section
        if compare_models:
            st.subheader("🔍 Model Comparison")
            
            with st.expander("Model Comparison Settings", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    test_size = st.slider("Test Data Size (%)", 10, 50, 20) / 100
                with col2:
                    comparison_models = st.multiselect(
                        "Select Models to Compare",
                        [
                            "exponential_smoothing",
                            "moving_average",
                            "prophet" if models_available['prophet'] else None,
                            "arima" if models_available['statsmodels'] else None,
                            "auto_arima" if models_available['pmdarima'] else None
                        ],
                        default=["exponential_smoothing", "moving_average"]
                    )
                    # Remove None values
                    comparison_models = [m for m in comparison_models if m is not None]
            
            if st.button("🔄 Run Model Comparison"):
                with st.spinner("Comparing forecasting models..."):
                    try:
                        comparison_results = forecaster.compare_forecasting_models(
                            periods=forecast_periods,
                            group_by='product_line',
                            test_size=test_size
                        )
                        
                        if 'performance_metrics' in comparison_results:
                            st.success("✅ Model comparison completed!")
                            
                            # Display performance metrics
                            metrics = comparison_results['performance_metrics']
                            st.subheader("📊 Model Performance Metrics")
                            
                            # Create a DataFrame for better display
                            metrics_df = pd.DataFrame(metrics).T
                            st.dataframe(metrics_df, use_container_width=True)
                            
                            # Show best model
                            if 'best_model' in comparison_results:
                                best_model = comparison_results['best_model']
                                st.success(f"🏆 Best Model: {best_model}")
                        
                        if 'forecast_plots' in comparison_results:
                            st.subheader("📈 Forecast Comparison")
                            plots = comparison_results['forecast_plots']
                            
                            for plot_name, fig in plots.items():
                                st.plotly_chart(fig, use_container_width=True)
                                
                    except Exception as e:
                        st.error(f"Error during model comparison: {e}")

        # Single model forecasting
        else:
            st.subheader("📈 Sales Forecast")
            
            if st.button("🚀 Generate Forecast"):
                with st.spinner("Generating forecast..."):
                    try:
                        # Generate forecast based on selected method
                        if "Prophet" in forecast_method and models_available['prophet']:
                            forecast_result = forecaster.prophet_forecast_wrapper(forecast_periods)
                        elif "ARIMA" in forecast_method and models_available['statsmodels']:
                            forecast_result = forecaster.arima_forecast_wrapper(forecast_periods)
                        elif "Auto-ARIMA" in forecast_method and models_available['pmdarima']:
                            forecast_result = forecaster.auto_arima_forecast_wrapper(forecast_periods)
                        elif "Moving Average" in forecast_method:
                            forecast_result = forecaster.moving_average_forecast_wrapper(forecast_periods)
                        else:
                            forecast_result = forecaster.exponential_smoothing_forecast(forecast_periods)
                        
                        # Display results
                        if 'forecast_plot' in forecast_result:
                            st.plotly_chart(forecast_result['forecast_plot'], use_container_width=True)
                        
                        if 'forecast_data' in forecast_result:
                            st.subheader("📊 Forecast Data")
                            st.dataframe(forecast_result['forecast_data'], use_container_width=True)
                        
                        if 'metrics' in forecast_result:
                            st.subheader("📈 Forecast Metrics")
                            metrics = forecast_result['metrics']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("MAE", f"{metrics.get('mae', 0):.2f}")
                            with col2:
                                st.metric("RMSE", f"{metrics.get('rmse', 0):.2f}")
                            with col3:
                                st.metric("MAPE", f"{metrics.get('mape', 0):.2f}%")
                        
                        # Key insights
                        st.markdown("## 💡 Forecast Insights")
                        
                        insights = forecaster.generate_insights(forecast_result)
                        for key, insight in insights.items():
                            st.markdown(f"**{key.replace('_', ' ').title()}:** {insight}")
                            
                    except Exception as e:
                        st.error(f"Error generating forecast: {e}")
                        st.info("Please check your data and try again.") 