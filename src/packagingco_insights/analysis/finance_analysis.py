"""
Finance Analysis module for financial metrics and insights.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class FinanceAnalyzer:
    """
    Analyzer for financial metrics and performance.
    
    Provides methods to analyze financial data, calculate key metrics,
    and generate insights for decision-making.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the finance analyzer with data.
        
        Args:
            data: DataFrame containing financial metrics
        """
        self.data = data
        self._validate_data()
    
    def _validate_data(self) -> None:
        """Validate that required columns are present in the data."""
        required_columns = [
            'month', 'product_line', 'total_revenue', 'total_cost_of_goods',
            'total_operating_cost', 'total_profit_margin'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
    
    def calculate_revenue_trends(self, 
                               group_by: str = 'product_line',
                               period: str = 'month') -> pd.DataFrame:
        """
        Calculate revenue trends over time.
        
        Args:
            group_by: Column to group by ('product_line', 'region', etc.)
            period: Time period for aggregation ('month', 'quarter', 'year')
        
        Returns:
            DataFrame with revenue trends
        """
        df = self.data.copy()
        df['month'] = pd.to_datetime(df['month'])
        
        if period == 'month':
            df['period'] = df['month'].dt.to_period('M')
        elif period == 'quarter':
            df['period'] = df['month'].dt.to_period('Q')
        elif period == 'year':
            df['period'] = df['month'].dt.to_period('Y')
        else:
            raise ValueError("period must be 'month', 'quarter', or 'year'")
        
        trends = df.groupby(['period', group_by])['total_revenue'].sum().reset_index()
        trends['period'] = trends['period'].astype(str)
        
        return trends
    
    def calculate_profitability_metrics(self) -> pd.DataFrame:
        """
        Calculate profitability metrics by product line and region.
        
        Returns:
            DataFrame with profitability metrics
        """
        metrics = self.data.groupby(['product_line', 'region']).agg({
            'total_revenue': 'sum',
            'total_cost_of_goods': 'sum',
            'total_operating_cost': 'sum',
            'total_profit_margin': 'sum',
            'total_units_sold': 'sum'
        }).reset_index()
        
        # Calculate additional metrics
        metrics['gross_profit'] = metrics['total_revenue'] - metrics['total_cost_of_goods']
        metrics['gross_margin_pct'] = (
            metrics['gross_profit'] / metrics['total_revenue'] * 100
        )
        metrics['net_margin_pct'] = (
            metrics['total_profit_margin'] / metrics['total_revenue'] * 100
        )
        metrics['revenue_per_unit'] = metrics['total_revenue'] / metrics['total_units_sold']
        metrics['profit_per_unit'] = metrics['total_profit_margin'] / metrics['total_units_sold']
        
        return metrics
    
    def calculate_growth_rates(self, 
                             metric: str = 'total_revenue',
                             periods: int = 1) -> pd.DataFrame:
        """
        Calculate growth rates for specified metric.
        
        Args:
            metric: Metric to calculate growth for
            periods: Number of periods to look back
        
        Returns:
            DataFrame with growth rates
        """
        df = self.data.copy()
        df['month'] = pd.to_datetime(df['month'])
        df = df.sort_values(['product_line', 'region', 'month'])
        
        # Calculate lagged values
        df[f'{metric}_lag'] = df.groupby(['product_line', 'region'])[metric].shift(periods)
        
        # Calculate growth rate
        df[f'{metric}_growth_pct'] = (
            (df[metric] - df[f'{metric}_lag']) / df[f'{metric}_lag'] * 100
        )
        
        return df[['month', 'product_line', 'region', metric, f'{metric}_growth_pct']].dropna()
    
    def calculate_contribution_margin(self) -> pd.DataFrame:
        """
        Calculate contribution margin analysis.
        
        Returns:
            DataFrame with contribution margin metrics
        """
        df = self.data.copy()
        
        # Calculate contribution margin
        df['contribution_margin'] = df['total_revenue'] - df['total_cost_of_goods']
        df['contribution_margin_pct'] = (
            df['contribution_margin'] / df['total_revenue'] * 100
        )
        
        # Calculate contribution margin per unit
        df['contribution_margin_per_unit'] = df['contribution_margin'] / df['total_units_sold']
        
        return df
    
    def generate_revenue_chart(self, 
                             group_by: str = 'product_line',
                             period: str = 'month') -> go.Figure:
        """
        Generate revenue trend chart.
        
        Args:
            group_by: Column to group by
            period: Time period for aggregation
        
        Returns:
            Plotly figure object
        """
        trends = self.calculate_revenue_trends(group_by, period)
        
        fig = px.line(
            trends, 
            x='period', 
            y='total_revenue',
            color=group_by,
            title=f'Revenue Trends by {group_by.replace("_", " ").title()}',
            labels={
                'period': 'Time Period',
                'total_revenue': 'Revenue ($)',
                group_by: group_by.replace("_", " ").title()
            }
        )
        
        fig.update_layout(
            xaxis_title="Time Period",
            yaxis_title="Revenue ($)",
            hovermode='x unified'
        )
        
        return fig
    
    def generate_profitability_chart(self) -> go.Figure:
        """
        Generate profitability analysis chart.
        
        Returns:
            Plotly figure object
        """
        metrics = self.calculate_profitability_metrics()
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Gross Margin %', 'Net Margin %', 
                          'Revenue per Unit', 'Profit per Unit'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gross margin
        fig.add_trace(
            go.Bar(x=metrics['product_line'], y=metrics['gross_margin_pct'],
                   name='Gross Margin %', marker_color='green'),
            row=1, col=1
        )
        
        # Net margin
        fig.add_trace(
            go.Bar(x=metrics['product_line'], y=metrics['net_margin_pct'],
                   name='Net Margin %', marker_color='blue'),
            row=1, col=2
        )
        
        # Revenue per unit
        fig.add_trace(
            go.Bar(x=metrics['product_line'], y=metrics['revenue_per_unit'],
                   name='Revenue per Unit', marker_color='orange'),
            row=2, col=1
        )
        
        # Profit per unit
        fig.add_trace(
            go.Bar(x=metrics['product_line'], y=metrics['profit_per_unit'],
                   name='Profit per Unit', marker_color='red'),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Profitability Metrics by Product Line",
            showlegend=False,
            height=600
        )
        
        return fig
    
    def generate_cost_breakdown_chart(self) -> go.Figure:
        """
        Generate cost breakdown chart.
        
        Returns:
            Plotly figure object
        """
        df = self.data.copy()
        
        # Calculate total costs
        total_revenue = df['total_revenue'].sum()
        total_cogs = df['total_cost_of_goods'].sum()
        total_opex = df['total_operating_cost'].sum()
        total_profit = df['total_profit_margin'].sum()
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=['Cost of Goods', 'Operating Expenses', 'Net Profit'],
            values=[total_cogs, total_opex, total_profit],
            hole=0.3,
            marker_colors=['red', 'orange', 'green']
        )])
        
        fig.update_layout(
            title_text="Cost Structure Breakdown",
            annotations=[dict(text='Total Revenue', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        return fig
    
    def get_financial_insights(self) -> Dict[str, str]:
        """
        Generate key financial insights.
        
        Returns:
            Dictionary of insights
        """
        insights = {}
        
        # Revenue insights
        total_revenue = self.data['total_revenue'].sum()
        avg_revenue = self.data['total_revenue'].mean()
        
        # Find top product by revenue
        product_revenue = self.data.groupby('product_line')['total_revenue'].sum()
        top_product = product_revenue.idxmax()
        
        insights['revenue'] = (
            f"Total revenue: ${total_revenue:,.0f}. "
            f"Average per record: ${avg_revenue:,.0f}. "
            f"Top product: {top_product}."
        )
        
        # Profitability insights
        total_profit = self.data['total_profit_margin'].sum()
        avg_margin = (total_profit / total_revenue) * 100
        
        # Find most profitable product
        product_profit = self.data.groupby('product_line')['total_profit_margin'].sum()
        most_profitable_product = product_profit.idxmax()
        
        insights['profitability'] = (
            f"Total profit: ${total_profit:,.0f}. "
            f"Average margin: {avg_margin:.1f}%. "
            f"Most profitable: {most_profitable_product}."
        )
        
        # Growth insights
        growth_data = self.calculate_growth_rates('total_revenue', 1)
        if not growth_data.empty:
            avg_growth = growth_data['total_revenue_growth_pct'].mean()
            insights['growth'] = f"Average revenue growth: {avg_growth:.1f}%."
        else:
            insights['growth'] = "Insufficient data for growth analysis."
        
        return insights 