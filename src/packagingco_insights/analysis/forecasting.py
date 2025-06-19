"""
Forecasting module for sales and financial projections.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')


class SalesForecaster:
    """
    Sales forecasting and trend analysis.
    
    Provides methods to forecast sales, analyze trends, and generate
    projections for business planning.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the sales forecaster with data.
        
        Args:
            data: DataFrame containing sales data
        """
        self.data = data
        self._validate_data()
        self._prepare_data()
    
    def _validate_data(self) -> None:
        """Validate that required columns are present in the data."""
        required_columns = ['date', 'revenue', 'units_sold']
        
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
    
    def _prepare_data(self) -> None:
        """Prepare data for forecasting."""
        df = self.data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Create time-based features
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['year'] = df['date'].dt.year
        
        # Create lag features
        df['revenue_lag1'] = df.groupby('product_line')['revenue'].shift(1)
        df['revenue_lag2'] = df.groupby('product_line')['revenue'].shift(2)
        
        # Create rolling averages
        df['revenue_ma3'] = df.groupby('product_line')['revenue'].rolling(3).mean().reset_index(0, drop=True)
        df['revenue_ma6'] = df.groupby('product_line')['revenue'].rolling(6).mean().reset_index(0, drop=True)
        
        self.prepared_data = df
    
    def simple_linear_forecast(self, 
                             periods: int = 6,
                             group_by: str = 'product_line') -> pd.DataFrame:
        """
        Generate simple linear forecast.
        
        Args:
            periods: Number of periods to forecast
            group_by: Column to group by for forecasting
        
        Returns:
            DataFrame with forecasts
        """
        forecasts = []
        
        for group in self.prepared_data[group_by].unique():
            group_data = self.prepared_data[self.prepared_data[group_by] == group].copy()
            
            if len(group_data) < 3:
                continue
            
            # Prepare features for modeling
            X = group_data[['month', 'quarter', 'year']].values
            y = group_data['revenue'].values
            
            # Fit linear model
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate future dates
            last_date = group_data['date'].max()
            future_dates = pd.date_range(
                start=last_date + pd.DateOffset(months=1),
                periods=periods,
                freq='MS'
            )
            
            # Create future features
            future_features = []
            for date in future_dates:
                future_features.append([date.month, date.quarter, date.year])
            
            # Make predictions
            predictions = model.predict(future_features)
            
            # Create forecast DataFrame
            for i, (date, pred) in enumerate(zip(future_dates, predictions)):
                forecasts.append({
                    'date': date,
                    group_by: group,
                    'forecasted_revenue': max(0, pred),  # Ensure non-negative
                    'forecast_period': i + 1,
                    'model_type': 'linear'
                })
        
        return pd.DataFrame(forecasts)
    
    def moving_average_forecast(self, 
                              periods: int = 6,
                              window: int = 3,
                              group_by: str = 'product_line') -> pd.DataFrame:
        """
        Generate moving average forecast.
        
        Args:
            periods: Number of periods to forecast
            window: Window size for moving average
            group_by: Column to group by for forecasting
        
        Returns:
            DataFrame with forecasts
        """
        forecasts = []
        
        for group in self.prepared_data[group_by].unique():
            group_data = self.prepared_data[self.prepared_data[group_by] == group].copy()
            
            if len(group_data) < window:
                continue
            
            # Calculate moving average
            ma_values = group_data['revenue'].rolling(window=window).mean()
            last_ma = ma_values.iloc[-1]
            
            # Generate future dates
            last_date = group_data['date'].max()
            future_dates = pd.date_range(
                start=last_date + pd.DateOffset(months=1),
                periods=periods,
                freq='MS'
            )
            
            # Create forecasts using last moving average value
            for i, date in enumerate(future_dates):
                forecasts.append({
                    'date': date,
                    group_by: group,
                    'forecasted_revenue': last_ma,
                    'forecast_period': i + 1,
                    'model_type': f'ma_{window}'
                })
        
        return pd.DataFrame(forecasts)
    
    def trend_analysis(self, 
                      metric: str = 'revenue',
                      group_by: str = 'product_line') -> pd.DataFrame:
        """
        Analyze trends in the data.
        
        Args:
            metric: Metric to analyze
            group_by: Column to group by
        
        Returns:
            DataFrame with trend analysis
        """
        trends = []
        
        for group in self.prepared_data[group_by].unique():
            group_data = self.prepared_data[self.prepared_data[group_by] == group].copy()
            
            if len(group_data) < 3:
                continue
            
            # Calculate trend metrics
            first_value = group_data[metric].iloc[0]
            last_value = group_data[metric].iloc[-1]
            total_change = last_value - first_value
            percent_change = (total_change / first_value) * 100 if first_value != 0 else 0
            
            # Calculate average monthly growth
            monthly_growth = []
            for i in range(1, len(group_data)):
                current = group_data[metric].iloc[i]
                previous = group_data[metric].iloc[i-1]
                if previous != 0:
                    growth = ((current - previous) / previous) * 100
                    monthly_growth.append(growth)
            
            avg_monthly_growth = np.mean(monthly_growth) if monthly_growth else 0
            
            trends.append({
                group_by: group,
                'first_value': first_value,
                'last_value': last_value,
                'total_change': total_change,
                'percent_change': percent_change,
                'avg_monthly_growth': avg_monthly_growth,
                'data_points': len(group_data)
            })
        
        return pd.DataFrame(trends)
    
    def generate_forecast_chart(self, 
                              forecast_data: pd.DataFrame,
                              actual_data: Optional[pd.DataFrame] = None,
                              group_by: str = 'product_line') -> go.Figure:
        """
        Generate forecast visualization chart.
        
        Args:
            forecast_data: DataFrame with forecast data
            actual_data: DataFrame with actual data (optional)
            group_by: Column to group by
        
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        # Add actual data if provided
        if actual_data is not None:
            for group in actual_data[group_by].unique():
                group_data = actual_data[actual_data[group_by] == group]
                fig.add_trace(go.Scatter(
                    x=group_data['date'],
                    y=group_data['revenue'],
                    mode='lines+markers',
                    name=f'{group} (Actual)',
                    line=dict(width=2)
                ))
        
        # Add forecast data
        for group in forecast_data[group_by].unique():
            group_data = forecast_data[forecast_data[group_by] == group]
            fig.add_trace(go.Scatter(
                x=group_data['date'],
                y=group_data['forecasted_revenue'],
                mode='lines+markers',
                name=f'{group} (Forecast)',
                line=dict(dash='dash', width=2)
            ))
        
        fig.update_layout(
            title="Sales Forecast",
            xaxis_title="Date",
            yaxis_title="Revenue ($)",
            hovermode='x unified'
        )
        
        return fig
    
    def generate_trend_chart(self, 
                           metric: str = 'revenue',
                           group_by: str = 'product_line') -> go.Figure:
        """
        Generate trend analysis chart.
        
        Args:
            metric: Metric to visualize
            group_by: Column to group by
        
        Returns:
            Plotly figure object
        """
        fig = px.line(
            self.prepared_data,
            x='date',
            y=metric,
            color=group_by,
            title=f'{metric.title()} Trends by {group_by.replace("_", " ").title()}',
            labels={
                'date': 'Date',
                metric: metric.replace('_', ' ').title(),
                group_by: group_by.replace('_', ' ').title()
            }
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title=metric.replace('_', ' ').title(),
            hovermode='x unified'
        )
        
        return fig
    
    def get_forecast_insights(self, 
                            forecast_data: pd.DataFrame) -> Dict[str, str]:
        """
        Generate insights from forecast data.
        
        Args:
            forecast_data: DataFrame with forecast data
        
        Returns:
            Dictionary of insights
        """
        insights = {}
        
        if forecast_data.empty:
            insights['forecast'] = "No forecast data available."
            return insights
        
        # Total forecasted revenue
        total_forecast = forecast_data['forecasted_revenue'].sum()
        insights['total_forecast'] = f"Total forecasted revenue: ${total_forecast:,.0f}"
        
        # Average forecast by group
        avg_by_group = forecast_data.groupby('product_line')['forecasted_revenue'].mean()
        top_forecast_product = avg_by_group.idxmax()
        top_forecast_value = avg_by_group.max()
        
        insights['top_product'] = (
            f"Highest forecasted revenue: {top_forecast_product} "
            f"(${top_forecast_value:,.0f} avg)"
        )
        
        # Forecast confidence (based on model type)
        model_types = forecast_data['model_type'].value_counts()
        insights['models'] = f"Forecast models used: {', '.join(model_types.index)}"
        
        return insights 