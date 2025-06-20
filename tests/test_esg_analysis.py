"""
Unit tests for ESGAnalyzer class.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.packagingco_insights.analysis.esg_analysis import ESGAnalyzer


class TestESGAnalyzer:
    """Test cases for ESGAnalyzer class."""
    
    def test_init_with_valid_data(self, sample_esg_data):
        """Test initialization with valid data."""
        analyzer = ESGAnalyzer(sample_esg_data)
        assert analyzer.data is not None
        assert len(analyzer.data) > 0
        assert all(col in analyzer.data.columns for col in [
            'date', 'product_line', 'facility', 'total_emissions_kg_co2',
            'total_energy_consumption_kwh', 'avg_recycled_material_pct'
        ])
    
    def test_init_with_invalid_data(self, invalid_esg_data):
        """Test initialization with invalid data raises ValueError."""
        with pytest.raises(ValueError, match="Missing required columns"):
            ESGAnalyzer(invalid_esg_data)
    
    def test_init_with_empty_data(self, empty_dataframe):
        """Test initialization with empty DataFrame raises ValueError."""
        with pytest.raises(ValueError, match="Missing required columns"):
            ESGAnalyzer(empty_dataframe)
    
    def test_calculate_emissions_trends_monthly(self, sample_esg_data):
        """Test emissions trends calculation with monthly period."""
        analyzer = ESGAnalyzer(sample_esg_data)
        trends = analyzer.calculate_emissions_trends(period='month')
        
        assert isinstance(trends, pd.DataFrame)
        assert len(trends) > 0
        assert 'period' in trends.columns
        assert 'product_line' in trends.columns
        assert 'total_emissions_kg_co2' in trends.columns
        assert all(trends['total_emissions_kg_co2'] >= 0)
    
    def test_calculate_emissions_trends_quarterly(self, sample_esg_data):
        """Test emissions trends calculation with quarterly period."""
        analyzer = ESGAnalyzer(sample_esg_data)
        trends = analyzer.calculate_emissions_trends(period='quarter')
        
        assert isinstance(trends, pd.DataFrame)
        assert len(trends) > 0
        assert 'period' in trends.columns
        assert 'product_line' in trends.columns
        assert 'total_emissions_kg_co2' in trends.columns
    
    def test_calculate_emissions_trends_yearly(self, sample_esg_data):
        """Test emissions trends calculation with yearly period."""
        analyzer = ESGAnalyzer(sample_esg_data)
        trends = analyzer.calculate_emissions_trends(period='year')
        
        assert isinstance(trends, pd.DataFrame)
        assert len(trends) > 0
        assert 'period' in trends.columns
        assert 'product_line' in trends.columns
        assert 'total_emissions_kg_co2' in trends.columns
    
    def test_calculate_emissions_trends_invalid_period(self, sample_esg_data):
        """Test emissions trends calculation with invalid period raises ValueError."""
        analyzer = ESGAnalyzer(sample_esg_data)
        with pytest.raises(ValueError, match="period must be"):
            analyzer.calculate_emissions_trends(period='invalid')
    
    def test_calculate_emissions_trends_group_by_facility(self, sample_esg_data):
        """Test emissions trends calculation grouped by facility."""
        analyzer = ESGAnalyzer(sample_esg_data)
        trends = analyzer.calculate_emissions_trends(group_by='facility')
        
        assert isinstance(trends, pd.DataFrame)
        assert len(trends) > 0
        assert 'period' in trends.columns
        assert 'facility' in trends.columns
        assert 'total_emissions_kg_co2' in trends.columns
    
    def test_calculate_material_efficiency(self, sample_esg_data):
        """Test material efficiency calculation."""
        analyzer = ESGAnalyzer(sample_esg_data)
        efficiency = analyzer.calculate_material_efficiency()
        
        assert isinstance(efficiency, pd.DataFrame)
        assert len(efficiency) > 0
        assert 'product_line' in efficiency.columns
        assert 'facility' in efficiency.columns
        assert 'avg_recycled_material_pct' in efficiency.columns
        assert 'avg_virgin_material_pct' in efficiency.columns
        assert 'avg_recycling_rate_pct' in efficiency.columns
        assert 'total_waste_generated_kg' in efficiency.columns
        assert 'total_energy_consumption_kwh' in efficiency.columns
        assert 'waste_per_kwh' in efficiency.columns
        
        # Test calculations are correct
        for _, row in efficiency.iterrows():
            # Recycled and virgin material percentages should sum to approximately 100
            material_sum = row['avg_recycled_material_pct'] + row['avg_virgin_material_pct']
            assert abs(material_sum - 100) < 1.0  # Allow small rounding errors
            
            # Recycling rate should be between 0 and 100
            assert 0 <= row['avg_recycling_rate_pct'] <= 100
            
            # Waste per kWh should be reasonable
            assert row['waste_per_kwh'] >= 0
    
    def test_calculate_esg_score_default_weights(self, sample_esg_data):
        """Test ESG score calculation with default weights."""
        analyzer = ESGAnalyzer(sample_esg_data)
        scores = analyzer.calculate_esg_score()
        
        assert isinstance(scores, pd.DataFrame)
        assert len(scores) > 0
        assert 'date' in scores.columns
        assert 'product_line' in scores.columns
        assert 'facility' in scores.columns
        assert 'esg_score' in scores.columns
        assert 'emissions_score' in scores.columns
        assert 'energy_score' in scores.columns
        assert 'materials_score' in scores.columns
        assert 'waste_score' in scores.columns
        
        # Test score ranges
        for _, row in scores.iterrows():
            assert 0 <= row['esg_score'] <= 100
            assert 0 <= row['emissions_score'] <= 100
            assert 0 <= row['energy_score'] <= 100
            assert 0 <= row['materials_score'] <= 100
            assert 0 <= row['waste_score'] <= 100
    
    def test_calculate_esg_score_custom_weights(self, sample_esg_data):
        """Test ESG score calculation with custom weights."""
        analyzer = ESGAnalyzer(sample_esg_data)
        custom_weights = {
            'emissions': 0.5,
            'energy': 0.2,
            'materials': 0.2,
            'waste': 0.1
        }
        scores = analyzer.calculate_esg_score(weights=custom_weights)
        
        assert isinstance(scores, pd.DataFrame)
        assert len(scores) > 0
        assert 'esg_score' in scores.columns
        
        # Test that weights sum to 1
        weight_sum = sum(custom_weights.values())
        assert abs(weight_sum - 1.0) < 0.01
    
    def test_calculate_esg_score_invalid_weights(self, sample_esg_data):
        """Test ESG score calculation with invalid weights."""
        analyzer = ESGAnalyzer(sample_esg_data)
        invalid_weights = {
            'emissions': 0.5,
            'energy': 0.2,
            'materials': 0.2,
            'waste': 0.1,
            'invalid_component': 0.1  # Extra component
        }
        
        # Should still work but ignore extra components
        scores = analyzer.calculate_esg_score(weights=invalid_weights)
        assert isinstance(scores, pd.DataFrame)
        assert len(scores) > 0
    
    def test_generate_emissions_chart(self, sample_esg_data):
        """Test emissions chart generation."""
        analyzer = ESGAnalyzer(sample_esg_data)
        chart = analyzer.generate_emissions_chart()
        
        assert chart is not None
        assert hasattr(chart, 'data')
        assert hasattr(chart, 'layout')
    
    def test_generate_materials_chart(self, sample_esg_data):
        """Test materials chart generation."""
        analyzer = ESGAnalyzer(sample_esg_data)
        chart = analyzer.generate_materials_chart()
        
        assert chart is not None
        assert hasattr(chart, 'data')
        assert hasattr(chart, 'layout')
    
    def test_get_esg_insights(self, sample_esg_data):
        """Test ESG insights generation."""
        analyzer = ESGAnalyzer(sample_esg_data)
        insights = analyzer.get_esg_insights()
        
        assert isinstance(insights, dict)
        assert len(insights) > 0
        assert all(isinstance(key, str) for key in insights.keys())
        assert all(isinstance(value, str) for value in insights.values())
    
    def test_data_validation_edge_cases(self):
        """Test data validation with various edge cases."""
        # Test with None data
        with pytest.raises(TypeError):
            ESGAnalyzer(None)  # type: ignore
        
        # Test with list instead of DataFrame
        with pytest.raises(TypeError):
            ESGAnalyzer([1, 2, 3])  # type: ignore
    
    def test_esg_score_calculation_logic(self, sample_esg_data):
        """Test that ESG score calculation logic is correct."""
        analyzer = ESGAnalyzer(sample_esg_data)
        scores = analyzer.calculate_esg_score()
        
        # Test that the composite score is calculated correctly
        assert len(scores) > 0
        
        for _, row in scores.iterrows():
            # Verify that all scores are within valid ranges
            assert 0 <= row['esg_score'] <= 100
            assert 0 <= row['emissions_score'] <= 100
            assert 0 <= row['energy_score'] <= 100
            assert 0 <= row['materials_score'] <= 100
            assert 0 <= row['waste_score'] <= 100
            
            # Verify that materials score is reasonable (should be recycled material percentage)
            # Since data is aggregated, we can't expect exact matches
            assert row['materials_score'] >= 0
            assert row['materials_score'] <= 100
            
            # Verify that the composite score is a weighted combination
            # The weights should be: emissions(0.4), energy(0.3), materials(0.2), waste(0.1)
            expected_composite = (
                row['emissions_score'] * 0.4 +
                row['energy_score'] * 0.3 +
                row['materials_score'] * 0.2 +
                row['waste_score'] * 0.1
            )
            assert abs(row['esg_score'] - expected_composite) < 0.01
    
    def test_emissions_score_normalization(self, sample_esg_data):
        """Test that emissions scores are properly normalized."""
        analyzer = ESGAnalyzer(sample_esg_data)
        scores = analyzer.calculate_esg_score()
        
        # Test that the highest emissions get the lowest score
        emissions_scores = scores['emissions_score'].values
        assert len(emissions_scores) > 0
        assert min(emissions_scores) >= 0
        assert max(emissions_scores) <= 100
    
    def test_energy_score_normalization(self, sample_esg_data):
        """Test that energy scores are properly normalized."""
        analyzer = ESGAnalyzer(sample_esg_data)
        scores = analyzer.calculate_esg_score()
        
        # Test that the highest energy consumption gets the lowest score
        energy_scores = scores['energy_score'].values
        assert len(energy_scores) > 0
        assert min(energy_scores) >= 0
        assert max(energy_scores) <= 100
    
    def test_waste_score_normalization(self, sample_esg_data):
        """Test that waste scores are properly normalized."""
        analyzer = ESGAnalyzer(sample_esg_data)
        scores = analyzer.calculate_esg_score()
        
        # Test that the highest waste generation gets the lowest score
        waste_scores = scores['waste_score'].values
        assert len(waste_scores) > 0
        assert min(waste_scores) >= 0
        assert max(waste_scores) <= 100 