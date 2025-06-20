"""
Finance Analysis module for financial metrics and insights.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional


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
        if not isinstance(self.data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")
            
        required_columns = [
            'date', 'product_line', 'total_revenue', 'total_cost_of_goods',
            'total_operating_cost', 'total_profit_margin'
        ]

        missing_columns = [
            col for col in required_columns if col not in self.data.columns
        ]
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
        df['date'] = pd.to_datetime(df['date'])

        if period == 'month':
            df['period'] = df['date'].dt.to_period('M')
        elif period == 'quarter':
            df['period'] = df['date'].dt.to_period('Q')
        elif period == 'year':
            df['period'] = df['date'].dt.to_period('Y')
        else:
            raise ValueError("period must be 'month', 'quarter', or 'year'")

        trends = df.groupby(['period', group_by])[
            'total_revenue'
        ].sum().reset_index()
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
        metrics['gross_profit'] = (
            metrics['total_revenue'] - metrics['total_cost_of_goods']
        )
        metrics['gross_margin_pct'] = (
            metrics['gross_profit'] / metrics['total_revenue'] * 100
        )
        metrics['net_margin_pct'] = (
            metrics['total_profit_margin'] / metrics['total_revenue'] * 100
        )
        metrics['revenue_per_unit'] = (
            metrics['total_revenue'] / metrics['total_units_sold']
        )
        metrics['profit_per_unit'] = (
            metrics['total_profit_margin'] / metrics['total_units_sold']
        )

        return metrics

    def calculate_growth_rates(self,
                             metric: str = 'total_revenue',
                             periods: int = 1,
                             smoothing_window: int = 3) -> pd.DataFrame:
        """
        Calculate growth rates for specified metric.

        Args:
            metric: Metric to calculate growth for
            periods: Number of periods to look back
            smoothing_window: The window size for the rolling average

        Returns:
            DataFrame with growth rates
        """
        try:
            if not isinstance(self.data, pd.DataFrame) or self.data.empty:
                # Early exit if data is not a valid DataFrame
                return pd.DataFrame()

            df = self.data.copy()
            df['date'] = pd.to_datetime(df['date'])

            # Ensure we have the required metric column
            if metric not in df.columns:
                raise ValueError(
                    f"Metric '{metric}' not found in data columns: {list(df.columns)}"
                )

            # Group by product_line and date, then resample to monthly frequency
            df = df.set_index('date')

            # Resample to monthly frequency and sum the metric for each product line
            monthly_df = df.groupby('product_line')[[metric]].resample('MS').sum()

            # Calculate growth rate using percentage change
            monthly_df[f'{metric}_growth_pct'] = (
                monthly_df.groupby('product_line')[metric].pct_change(periods) * 100
            )

            # Reset index to bring 'product_line' and 'date' back as columns
            monthly_df = monthly_df.reset_index()

            # Replace infinite values with NaN
            monthly_df.replace([np.inf, -np.inf], np.nan, inplace=True)

            # Apply a rolling average to smooth the growth percentage
            monthly_df[f'{metric}_growth_pct_smoothed'] = (
                monthly_df.groupby('product_line')[f'{metric}_growth_pct'].transform(
                    lambda x: x.rolling(
                        window=smoothing_window, min_periods=1, center=True
                    ).mean()
                )
            )

            # Ensure we return the expected columns
            result_columns = [
                'date', 'product_line', metric, f'{metric}_growth_pct',
                f'{metric}_growth_pct_smoothed'
            ]
            available_columns = [
                col for col in result_columns if col in monthly_df.columns
            ]

            result_df = monthly_df[available_columns].dropna(
                subset=[f'{metric}_growth_pct']
            )

            return result_df

        except Exception as e:
            # Return empty DataFrame with expected columns if there's an error
            print(f"Error in calculate_growth_rates: {e}")
            return pd.DataFrame(columns=[
                'date', 'product_line', metric, f'{metric}_growth_pct',
                f'{metric}_growth_pct_smoothed'
            ])

    def calculate_contribution_margin(self) -> pd.DataFrame:
        """
        Calculate contribution margin analysis.

        Returns:
            DataFrame with contribution margin metrics
        """
        df = self.data.copy()

        # Calculate contribution margin
        df['contribution_margin'] = (
            df['total_revenue'] - df['total_cost_of_goods']
        )
        df['contribution_margin_pct'] = (
            df['contribution_margin'] / df['total_revenue'] * 100
        )

        # Calculate contribution margin per unit
        df['contribution_margin_per_unit'] = (
            df['contribution_margin'] / df['total_units_sold']
        )

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
            },
            line_shape='spline'
        )

        fig.update_layout(
            xaxis_title="Time Period",
            yaxis_title="Revenue ($)",
            hovermode='x unified'
        )

        return fig

    def generate_profitability_chart(self) -> go.Figure:
        """
        Generate profitability metrics chart.

        Returns:
            Plotly figure object
        """
        metrics = self.calculate_profitability_metrics()

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Gross Margin %',
                'Net Margin %',
                'Revenue per Unit',
                'Profit per Unit'
            )
        )

        # Gross margin
        fig.add_trace(
            go.Bar(
                x=metrics['product_line'],
                y=metrics['gross_margin_pct'],
                name='Gross Margin %',
                marker_color='green'
            ),
            row=1, col=1
        )

        # Net margin
        fig.add_trace(
            go.Bar(
                x=metrics['product_line'],
                y=metrics['net_margin_pct'],
                name='Net Margin %',
                marker_color='blue'
            ),
            row=1, col=2
        )

        # Revenue per unit
        fig.add_trace(
            go.Bar(
                x=metrics['product_line'],
                y=metrics['revenue_per_unit'],
                name='Revenue per Unit',
                marker_color='orange'
            ),
            row=2, col=1
        )

        # Profit per unit
        fig.add_trace(
            go.Bar(
                x=metrics['product_line'],
                y=metrics['profit_per_unit'],
                name='Profit per Unit',
                marker_color='red'
            ),
            row=2, col=2
        )

        fig.update_layout(
            title='Profitability Metrics by Product Line',
            height=600,
            showlegend=False
        )

        return fig

    def generate_cost_breakdown_chart(self) -> go.Figure:
        """
        Generate cost breakdown chart.

        Returns:
            Plotly figure object
        """
        metrics = self.calculate_profitability_metrics()

        fig = go.Figure()

        for _, row in metrics.iterrows():
            fig.add_trace(go.Bar(
                name=row['product_line'],
                x=['COGS', 'Operating Cost', 'Profit'],
                y=[
                    row['total_cost_of_goods'],
                    row['total_operating_cost'],
                    row['total_profit_margin']
                ],
                text=[
                    f"${row['total_cost_of_goods']:,.0f}",
                    f"${row['total_operating_cost']:,.0f}",
                    f"${row['total_profit_margin']:,.0f}"
                ],
                textposition='auto'
            ))

        fig.update_layout(
            title='Cost Breakdown by Product Line',
            barmode='group',
            xaxis_title="Cost Component",
            yaxis_title="Amount ($)"
        )

        return fig

    def get_financial_insights(self) -> Dict[str, str]:
        """
        Generate financial insights and recommendations.

        Returns:
            Dictionary containing insights and recommendations
        """
        insights = {}

        # Revenue insights
        total_revenue = self.data['total_revenue'].sum()
        avg_revenue = self.data['total_revenue'].mean()
        insights['revenue'] = (
            f"Total revenue: ${total_revenue:,.0f}, "
            f"Average per period: ${avg_revenue:,.0f}"
        )

        # Profitability insights
        total_profit = self.data['total_profit_margin'].sum()
        avg_margin = (
            self.data['total_profit_margin'].sum() /
            self.data['total_revenue'].sum() * 100
        )
        insights['profitability'] = (
            f"Total profit: ${total_profit:,.0f}, "
            f"Average margin: {avg_margin:.1f}%"
        )

        # Growth insights
        growth_data = self.calculate_growth_rates()
        if not growth_data.empty:
            recent_growth = growth_data['total_revenue_growth_pct'].iloc[-1]
            insights['growth'] = (
                f"Recent revenue growth: {recent_growth:.1f}%"
            )
        else:
            insights['growth'] = "Insufficient data for growth analysis"

        # Cost insights
        total_cogs = self.data['total_cost_of_goods'].sum()
        total_operating = self.data['total_operating_cost'].sum()
        insights['costs'] = (
            f"Total COGS: ${total_cogs:,.0f}, "
            f"Total operating costs: ${total_operating:,.0f}"
        )

        return insights 