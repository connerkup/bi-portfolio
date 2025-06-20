"""
ESG Analysis module for sustainability metrics and insights.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional


class ESGAnalyzer:
    """
    Analyzer for ESG (Environmental, Social, Governance) metrics.

    Provides methods to analyze sustainability data, calculate key metrics,
    and generate insights for decision-making.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the ESG analyzer with data.

        Args:
            data: DataFrame containing ESG metrics
        """
        if data is None:
            raise TypeError("Data cannot be None")
        self.data = data
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate that required columns are present in the data."""
        if not isinstance(self.data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")
            
        required_columns = [
            'date', 'product_line', 'facility', 'total_emissions_kg_co2',
            'total_energy_consumption_kwh', 'avg_recycled_material_pct'
        ]

        missing_columns = [
            col for col in required_columns if col not in self.data.columns
        ]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

    def calculate_emissions_trends(self,
                                 group_by: str = 'product_line',
                                 period: str = 'month') -> pd.DataFrame:
        """
        Calculate emissions trends over time.

        Args:
            group_by: Column to group by ('product_line', 'facility', etc.)
            period: Time period for aggregation ('month', 'quarter', 'year')

        Returns:
            DataFrame with emissions trends
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
            'total_emissions_kg_co2'
        ].sum().reset_index()
        trends['period'] = trends['period'].astype(str)

        return trends

    def calculate_material_efficiency(self) -> pd.DataFrame:
        """
        Calculate material efficiency metrics.

        Returns:
            DataFrame with material efficiency metrics
        """
        efficiency = self.data.groupby(['product_line', 'facility']).agg({
            'avg_recycled_material_pct': 'mean',
            'avg_virgin_material_pct': 'mean',
            'avg_recycling_rate_pct': 'mean',
            'total_waste_generated_kg': 'sum',
            'total_energy_consumption_kwh': 'sum'
        }).reset_index()

        efficiency['waste_per_kwh'] = (
            efficiency['total_waste_generated_kg'] /
            efficiency['total_energy_consumption_kwh']
        )

        return efficiency

    def calculate_esg_score(self,
                          weights: Optional[Dict[str, float]] = None) -> pd.DataFrame:
        """
        Calculate composite ESG score.

        Args:
            weights: Dictionary of weights for different ESG components

        Returns:
            DataFrame with ESG scores
        """
        if weights is None:
            weights = {
                'emissions': 0.4,
                'energy': 0.3,
                'materials': 0.2,
                'waste': 0.1
            }

        # Normalize metrics to 0-100 scale
        df = self.data.copy()

        # Emissions score (lower is better)
        emissions_score = 100 - (
            (df['total_emissions_kg_co2'] - df['total_emissions_kg_co2'].min()) /
            (df['total_emissions_kg_co2'].max() - df['total_emissions_kg_co2'].min()) * 100
        )

        # Energy efficiency score (lower consumption is better)
        energy_score = 100 - (
            (df['total_energy_consumption_kwh'] - df['total_energy_consumption_kwh'].min()) /
            (df['total_energy_consumption_kwh'].max() - df['total_energy_consumption_kwh'].min()) * 100
        )

        # Materials score (higher recycled content is better)
        materials_score = df['avg_recycled_material_pct']

        # Waste score (lower waste is better)
        waste_score = 100 - (
            (df['total_waste_generated_kg'] - df['total_waste_generated_kg'].min()) /
            (df['total_waste_generated_kg'].max() - df['total_waste_generated_kg'].min()) * 100
        )

        # Calculate composite score
        composite_score = (
            emissions_score * weights['emissions'] +
            energy_score * weights['energy'] +
            materials_score * weights['materials'] +
            waste_score * weights['waste']
        )

        result = df[['date', 'product_line', 'facility']].copy()
        result['esg_score'] = composite_score
        result['emissions_score'] = emissions_score
        result['energy_score'] = energy_score
        result['materials_score'] = materials_score
        result['waste_score'] = waste_score

        return result

    def generate_emissions_chart(self,
                               group_by: str = 'product_line',
                               period: str = 'month') -> go.Figure:
        """
        Generate emissions trend chart.

        Args:
            group_by: Column to group by
            period: Time period for aggregation

        Returns:
            Plotly figure object
        """
        trends = self.calculate_emissions_trends(group_by, period)

        fig = px.line(
            trends,
            x='period',
            y='total_emissions_kg_co2',
            color=group_by,
            title=f'CO2 Emissions Trends by {group_by.replace("_", " ").title()}',
            labels={
                'period': 'Time Period',
                'total_emissions_kg_co2': 'CO2 Emissions (kg)',
                group_by: group_by.replace("_", " ").title()
            },
            line_shape='spline'
        )

        fig.update_layout(
            xaxis_title="Time Period",
            yaxis_title="CO2 Emissions (kg)",
            hovermode='x unified'
        )

        return fig

    def generate_materials_chart(self) -> go.Figure:
        """
        Generate materials usage chart.

        Returns:
            Plotly figure object
        """
        efficiency = self.calculate_material_efficiency()

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Recycled Material %',
                'Virgin Material %',
                'Recycling Rate %',
                'Waste per kWh'
            )
        )

        # Recycled material
        fig.add_trace(
            go.Bar(
                x=efficiency['product_line'],
                y=efficiency['avg_recycled_material_pct'],
                name='Recycled %',
                marker_color='green'
            ),
            row=1, col=1
        )

        # Virgin material
        fig.add_trace(
            go.Bar(
                x=efficiency['product_line'],
                y=efficiency['avg_virgin_material_pct'],
                name='Virgin %',
                marker_color='red'
            ),
            row=1, col=2
        )

        # Recycling rate
        fig.add_trace(
            go.Bar(
                x=efficiency['product_line'],
                y=efficiency['avg_recycling_rate_pct'],
                name='Recycling Rate %',
                marker_color='blue'
            ),
            row=2, col=1
        )

        # Waste per kWh
        fig.add_trace(
            go.Bar(
                x=efficiency['product_line'],
                y=efficiency['waste_per_kwh'],
                name='Waste per kWh',
                marker_color='orange'
            ),
            row=2, col=2
        )

        fig.update_layout(
            title='Material Efficiency Metrics by Product Line',
            height=600,
            showlegend=False
        )

        return fig

    def get_esg_insights(self) -> Dict[str, str]:
        """
        Generate ESG insights and recommendations.

        Returns:
            Dictionary containing insights and recommendations
        """
        insights = {}

        # Emissions insights
        emissions_trend = self.calculate_emissions_trends()
        if len(emissions_trend) > 1:
            recent_emissions = emissions_trend['total_emissions_kg_co2'].iloc[-1]
            previous_emissions = emissions_trend['total_emissions_kg_co2'].iloc[-2]
            emissions_change = (
                (recent_emissions - previous_emissions) / previous_emissions * 100
            )
            insights['emissions_trend'] = (
                f"Emissions {'increased' if emissions_change > 0 else 'decreased'} "
                f"by {abs(emissions_change):.1f}% in the latest period"
            )
        else:
            insights['emissions_trend'] = "Insufficient data for trend analysis"

        # Energy efficiency insights
        avg_energy = self.data['total_energy_consumption_kwh'].mean()
        insights['energy_efficiency'] = (
            f"Average energy consumption: {avg_energy:.0f} kWh"
        )

        # Materials insights
        avg_recycled = self.data['avg_recycled_material_pct'].mean()
        insights['materials'] = (
            f"Average recycled material content: {avg_recycled:.1f}%"
        )

        # Waste insights
        total_waste = self.data['total_waste_generated_kg'].sum()
        insights['waste'] = f"Total waste generated: {total_waste:.0f} kg"

        return insights

    def get_summary(self) -> Dict[str, float]:
        """
        Get summary statistics for ESG metrics.

        Returns:
            Dictionary containing summary statistics
        """
        summary = {
            'total_emissions_kg_co2': self.data['total_emissions_kg_co2'].sum(),
            'avg_recycled_material_pct': self.data['avg_recycled_material_pct'].mean(),
            'total_waste_generated_kg': self.data['total_waste_generated_kg'].sum(),
            'total_energy_consumption_kwh': self.data['total_energy_consumption_kwh'].sum(),
            'avg_energy_consumption_kwh': self.data['total_energy_consumption_kwh'].mean(),
        }
        
        # Add optional columns if they exist
        if 'avg_virgin_material_pct' in self.data.columns:
            summary['avg_virgin_material_pct'] = self.data['avg_virgin_material_pct'].mean()
        else:
            summary['avg_virgin_material_pct'] = 0.0
            
        if 'avg_recycling_rate_pct' in self.data.columns:
            summary['avg_recycling_rate_pct'] = self.data['avg_recycling_rate_pct'].mean()
        else:
            summary['avg_recycling_rate_pct'] = 0.0
        
        return summary 