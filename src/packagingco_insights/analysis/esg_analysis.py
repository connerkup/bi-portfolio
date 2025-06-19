"""
ESG Analysis module for sustainability metrics and insights.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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
        self.data = data
        self._validate_data()
    
    def _validate_data(self) -> None:
        """Validate that required columns are present in the data."""
        required_columns = [
            'month', 'product_line', 'facility', 'total_emissions_kg_co2',
            'total_energy_kwh', 'avg_recycled_material_pct'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.data.columns]
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
        df['month'] = pd.to_datetime(df['month'])
        
        if period == 'month':
            df['period'] = df['month'].dt.to_period('M')
        elif period == 'quarter':
            df['period'] = df['month'].dt.to_period('Q')
        elif period == 'year':
            df['period'] = df['month'].dt.to_period('Y')
        else:
            raise ValueError("period must be 'month', 'quarter', or 'year'")
        
        trends = df.groupby(['period', group_by])['total_emissions_kg_co2'].sum().reset_index()
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
            'total_waste_kg': 'sum',
            'total_energy_kwh': 'sum'
        }).reset_index()
        
        efficiency['waste_per_kwh'] = (
            efficiency['total_waste_kg'] / efficiency['total_energy_kwh']
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
            (df['total_energy_kwh'] - df['total_energy_kwh'].min()) /
            (df['total_energy_kwh'].max() - df['total_energy_kwh'].min()) * 100
        )
        
        # Materials score (higher recycled content is better)
        materials_score = df['avg_recycled_material_pct']
        
        # Waste score (lower waste is better)
        waste_score = 100 - (
            (df['total_waste_kg'] - df['total_waste_kg'].min()) /
            (df['total_waste_kg'].max() - df['total_waste_kg'].min()) * 100
        )
        
        # Calculate composite score
        composite_score = (
            emissions_score * weights['emissions'] +
            energy_score * weights['energy'] +
            materials_score * weights['materials'] +
            waste_score * weights['waste']
        )
        
        result = df[['month', 'product_line', 'facility']].copy()
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
            }
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
            subplot_titles=('Recycled Material %', 'Virgin Material %', 
                          'Recycling Rate %', 'Waste per kWh'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Recycled material
        fig.add_trace(
            go.Bar(x=efficiency['product_line'], y=efficiency['avg_recycled_material_pct'],
                   name='Recycled %', marker_color='green'),
            row=1, col=1
        )
        
        # Virgin material
        fig.add_trace(
            go.Bar(x=efficiency['product_line'], y=efficiency['avg_virgin_material_pct'],
                   name='Virgin %', marker_color='red'),
            row=1, col=2
        )
        
        # Recycling rate
        fig.add_trace(
            go.Bar(x=efficiency['product_line'], y=efficiency['avg_recycling_rate_pct'],
                   name='Recycling Rate %', marker_color='blue'),
            row=2, col=1
        )
        
        # Waste per kWh
        fig.add_trace(
            go.Bar(x=efficiency['product_line'], y=efficiency['waste_per_kwh'],
                   name='Waste per kWh', marker_color='orange'),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Material Efficiency Metrics by Product Line",
            showlegend=False,
            height=600
        )
        
        return fig
    
    def get_esg_insights(self) -> Dict[str, str]:
        """
        Generate key ESG insights.
        
        Returns:
            Dictionary of insights
        """
        insights = {}
        
        # Emissions insights
        avg_emissions = self.data['total_emissions_kg_co2'].mean()
        max_emissions_product = self.data.loc[
            self.data['total_emissions_kg_co2'].idxmax(), 'product_line'
        ]
        
        insights['emissions'] = (
            f"Average CO2 emissions: {avg_emissions:.0f} kg. "
            f"Highest emissions from {max_emissions_product}."
        )
        
        # Material insights
        avg_recycled = self.data['avg_recycled_material_pct'].mean()
        best_recycled_product = self.data.loc[
            self.data['avg_recycled_material_pct'].idxmax(), 'product_line'
        ]
        
        insights['materials'] = (
            f"Average recycled material usage: {avg_recycled:.1f}%. "
            f"Best performer: {best_recycled_product}."
        )
        
        # Energy insights
        avg_energy = self.data['total_energy_kwh'].mean()
        most_efficient_product = self.data.loc[
            self.data['total_energy_kwh'].idxmin(), 'product_line'
        ]
        
        insights['energy'] = (
            f"Average energy consumption: {avg_energy:.0f} kWh. "
            f"Most efficient: {most_efficient_product}."
        )
        
        return insights 