"""
Forecasting Page

This page provides sales forecasting and projections for PackagingCo.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from packagingco_insights.analysis import SalesForecaster
from packagingco_insights.utils import display_charts_responsive

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
        from pmdarima import auto_arima
        models_available['pmdarima'] = True
    except ImportError:
        pass
    
    return models_available

def main():
    """Forecasting page main function."""
    
    st.title("📈 Sales Forecasting & Projections")

    # Check if data is available in session state
    if 'filtered_sales' not in st.session_state:
        st.error("No sales data available. Please return to the main page to load data.")
        st.info("The main page loads and filters the data for all pages.")
        return
    
    sales_data = st.session_state.filtered_sales
    
    if sales_data.empty:
        st.warning("No sales data available for the selected filters.")
        return
    
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
                        
                        # Average metrics by model
                        avg_metrics = metrics.groupby('model')[['mae', 'mape', 'rmse']].mean().round(2)
                        st.dataframe(avg_metrics, use_container_width=True)
                        
                        # Performance visualization
                        fig_mae = px.bar(avg_metrics.reset_index(), x='model', y='mae', 
                                       title="Mean Absolute Error by Model")
                        fig_mape = px.bar(avg_metrics.reset_index(), x='model', y='mape', 
                                        title="Mean Absolute Percentage Error by Model")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.plotly_chart(fig_mae, use_container_width=True)
                        with col2:
                            st.plotly_chart(fig_mape, use_container_width=True)
                        
                        # Model recommendations
                        recommendations = forecaster.get_model_recommendations(metrics)
                        st.subheader("💡 Model Recommendations")
                        for key, recommendation in recommendations.items():
                            st.info(f"**{key.replace('_', ' ').title()}:** {recommendation}")
                    else:
                        st.warning("⚠️ Insufficient data for model comparison")
                        
                except Exception as e:
                    st.error(f"❌ Error in model comparison: {str(e)}")
    
    # Generate forecast based on selected method
    try:
        if forecast_method == "Exponential Smoothing":
            forecast_data = forecaster.simple_linear_forecast(forecast_periods, 'product_line')
            st.info("📊 Using exponential smoothing with trend and seasonality for smooth forecasts")
        elif forecast_method == "Moving Average":
            forecast_data = forecaster.moving_average_forecast(forecast_periods, 3, 'product_line')
            st.info("📊 Using moving average with trend consideration for stable forecasts")
        elif forecast_method == "Prophet (Advanced)":
            forecast_data = forecaster.prophet_forecast(forecast_periods, 'product_line')
            st.info("📊 Using Facebook Prophet for advanced time-series forecasting with seasonality detection")
        elif forecast_method == "ARIMA (Advanced)":
            forecast_data = forecaster.arima_forecast(forecast_periods, 'product_line')
            st.info("📊 Using ARIMA model for stationary time-series forecasting")
        elif forecast_method == "Auto-ARIMA (Advanced)":
            forecast_data = forecaster.auto_arima_forecast(forecast_periods, 'product_line')
            st.info("📊 Using Auto-ARIMA with automatic parameter selection")
        else:
            st.warning("⚠️ Selected model is not available")
            return
            
        if forecast_data.empty:
            st.warning("⚠️ No forecast data generated. This may be due to insufficient historical data.")
            return
            
    except Exception as e:
        st.error(f"❌ Error generating forecast: {str(e)}")
        return
    
    st.subheader("🔮 Sales Forecast")
    
    # Generate and display the forecast chart
    fig = forecaster.generate_forecast_chart(forecast_data, sales_data, 'product_line')
    st.plotly_chart(fig, use_container_width=True)
    
    # Display forecast insights
    insights = forecaster.get_forecast_insights(forecast_data)
    st.markdown("## 💡 Forecast Insights")
    for key, insight in insights.items():
        st.markdown(f"**{key.replace('_', ' ').title()}:** {insight}")
    
    # Additional forecast details
    st.subheader("📊 Forecast Details")
    
    # Show forecast table
    if not forecast_data.empty:
        display_forecast = forecast_data.copy()
        display_forecast['forecasted_revenue'] = display_forecast['forecasted_revenue'].apply(lambda x: f"${x:,.0f}")
        display_forecast['date'] = display_forecast['date'].dt.strftime('%Y-%m-%d')
        
        # Add confidence intervals if available (Prophet)
        if 'forecast_lower' in display_forecast.columns and 'forecast_upper' in display_forecast.columns:
            display_forecast['confidence_interval'] = display_forecast.apply(
                lambda row: f"${row['forecast_lower']:,.0f} - ${row['forecast_upper']:,.0f}", 
                axis=1
            )
            columns_to_show = ['date', 'product_line', 'forecasted_revenue', 'confidence_interval', 'model_type']
        else:
            columns_to_show = ['date', 'product_line', 'forecasted_revenue', 'model_type']
        
        st.dataframe(
            display_forecast[columns_to_show].rename(columns={
                'date': 'Date',
                'product_line': 'Product Line',
                'forecasted_revenue': 'Forecasted Revenue',
                'confidence_interval': 'Confidence Interval',
                'model_type': 'Model Type'
            }),
            use_container_width=True
        )
    
    st.subheader("📊 Trend Analysis")
    trends = forecaster.trend_analysis('revenue', 'product_line')
    growth_by_product_fig = px.bar(trends, x='product_line', y='percent_change', title="Revenue Growth by Product Line")
    avg_growth_fig = px.bar(trends, x='product_line', y='avg_monthly_growth', title="Average Monthly Growth")
    display_charts_responsive([growth_by_product_fig, avg_growth_fig], ["Revenue Growth by Product Line", "Average Monthly Growth"])
    
    st.subheader("📈 Historical Trends")
    fig = forecaster.generate_trend_chart('revenue', 'product_line')
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main() 