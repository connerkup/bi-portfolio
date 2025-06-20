"""
Unit tests for FinanceAnalyzer class.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.packagingco_insights.analysis.finance_analysis import FinanceAnalyzer


class TestFinanceAnalyzer:
    """Test cases for FinanceAnalyzer class."""
    
    def test_init_with_valid_data(self, sample_finance_data):
        """Test initialization with valid data."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        assert analyzer.data is not None
        assert len(analyzer.data) > 0
        assert all(col in analyzer.data.columns for col in [
            'date', 'product_line', 'total_revenue', 'total_cost_of_goods',
            'total_operating_cost', 'total_profit_margin'
        ])
    
    def test_init_with_invalid_data(self, invalid_finance_data):
        """Test initialization with invalid data raises ValueError."""
        with pytest.raises(ValueError, match="Missing required columns"):
            FinanceAnalyzer(invalid_finance_data)
    
    def test_init_with_empty_data(self, empty_dataframe):
        """Test initialization with empty DataFrame raises ValueError."""
        with pytest.raises(ValueError, match="Missing required columns"):
            FinanceAnalyzer(empty_dataframe)
    
    def test_calculate_revenue_trends_monthly(self, sample_finance_data):
        """Test revenue trends calculation with monthly period."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        trends = analyzer.calculate_revenue_trends(period='month')
        
        assert isinstance(trends, pd.DataFrame)
        assert len(trends) > 0
        assert 'period' in trends.columns
        assert 'product_line' in trends.columns
        assert 'total_revenue' in trends.columns
        assert all(trends['total_revenue'] >= 0)
    
    def test_calculate_revenue_trends_quarterly(self, sample_finance_data):
        """Test revenue trends calculation with quarterly period."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        trends = analyzer.calculate_revenue_trends(period='quarter')
        
        assert isinstance(trends, pd.DataFrame)
        assert len(trends) > 0
        assert 'period' in trends.columns
        assert 'product_line' in trends.columns
        assert 'total_revenue' in trends.columns
    
    def test_calculate_revenue_trends_yearly(self, sample_finance_data):
        """Test revenue trends calculation with yearly period."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        trends = analyzer.calculate_revenue_trends(period='year')
        
        assert isinstance(trends, pd.DataFrame)
        assert len(trends) > 0
        assert 'period' in trends.columns
        assert 'product_line' in trends.columns
        assert 'total_revenue' in trends.columns
    
    def test_calculate_revenue_trends_invalid_period(self, sample_finance_data):
        """Test revenue trends calculation with invalid period raises ValueError."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        with pytest.raises(ValueError, match="period must be"):
            analyzer.calculate_revenue_trends(period='invalid')
    
    def test_calculate_revenue_trends_group_by_region(self, sample_finance_data):
        """Test revenue trends calculation grouped by region."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        trends = analyzer.calculate_revenue_trends(group_by='region')
        
        assert isinstance(trends, pd.DataFrame)
        assert len(trends) > 0
        assert 'period' in trends.columns
        assert 'region' in trends.columns
        assert 'total_revenue' in trends.columns
    
    def test_calculate_profitability_metrics(self, sample_finance_data):
        """Test profitability metrics calculation."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        metrics = analyzer.calculate_profitability_metrics()
        
        assert isinstance(metrics, pd.DataFrame)
        assert len(metrics) > 0
        assert 'product_line' in metrics.columns
        assert 'region' in metrics.columns
        assert 'gross_profit' in metrics.columns
        assert 'gross_margin_pct' in metrics.columns
        assert 'net_margin_pct' in metrics.columns
        assert 'revenue_per_unit' in metrics.columns
        assert 'profit_per_unit' in metrics.columns
        
        # Test calculations are correct
        for _, row in metrics.iterrows():
            # Gross profit should equal revenue - cost of goods
            expected_gross_profit = row['total_revenue'] - row['total_cost_of_goods']
            assert abs(row['gross_profit'] - expected_gross_profit) < 0.01
            
            # Gross margin percentage should be positive and reasonable
            assert 0 <= row['gross_margin_pct'] <= 100
            
            # Net margin percentage should be reasonable
            assert -100 <= row['net_margin_pct'] <= 100
            
            # Revenue per unit should be positive
            assert row['revenue_per_unit'] > 0
    
    def test_calculate_growth_rates(self, sample_finance_data):
        """Test growth rates calculation."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        growth = analyzer.calculate_growth_rates(metric='total_revenue', periods=1)
        
        assert isinstance(growth, pd.DataFrame)
        if len(growth) > 0:  # May be empty if insufficient data
            assert 'date' in growth.columns
            assert 'product_line' in growth.columns
            assert 'total_revenue' in growth.columns
            assert 'total_revenue_growth_pct' in growth.columns
            assert 'total_revenue_growth_pct_smoothed' in growth.columns
    
    def test_calculate_growth_rates_invalid_metric(self, sample_finance_data):
        """Test growth rates calculation with invalid metric."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        growth = analyzer.calculate_growth_rates(metric='invalid_metric')
        
        # Should return empty DataFrame with expected columns
        assert isinstance(growth, pd.DataFrame)
        assert len(growth) == 0
    
    def test_calculate_contribution_margin(self, sample_finance_data):
        """Test contribution margin calculation."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        margins = analyzer.calculate_contribution_margin()
        
        assert isinstance(margins, pd.DataFrame)
        assert len(margins) > 0
        assert 'contribution_margin' in margins.columns
        assert 'contribution_margin_pct' in margins.columns
        assert 'contribution_margin_per_unit' in margins.columns
        
        # Test calculations are correct
        for _, row in margins.iterrows():
            # Contribution margin should equal revenue - cost of goods
            expected_margin = row['total_revenue'] - row['total_cost_of_goods']
            assert abs(row['contribution_margin'] - expected_margin) < 0.01
            
            # Contribution margin percentage should be reasonable
            assert -100 <= row['contribution_margin_pct'] <= 100
    
    def test_generate_revenue_chart(self, sample_finance_data):
        """Test revenue chart generation."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        chart = analyzer.generate_revenue_chart()
        
        assert chart is not None
        assert hasattr(chart, 'data')
        assert hasattr(chart, 'layout')
    
    def test_generate_profitability_chart(self, sample_finance_data):
        """Test profitability chart generation."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        chart = analyzer.generate_profitability_chart()
        
        assert chart is not None
        assert hasattr(chart, 'data')
        assert hasattr(chart, 'layout')
    
    def test_generate_cost_breakdown_chart(self, sample_finance_data):
        """Test cost breakdown chart generation."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        chart = analyzer.generate_cost_breakdown_chart()
        
        assert chart is not None
        assert hasattr(chart, 'data')
        assert hasattr(chart, 'layout')
    
    def test_get_financial_insights(self, sample_finance_data):
        """Test financial insights generation."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        insights = analyzer.get_financial_insights()
        
        assert isinstance(insights, dict)
        assert len(insights) > 0
        assert all(isinstance(key, str) for key in insights.keys())
        assert all(isinstance(value, str) for value in insights.values())
    
    def test_data_validation_edge_cases(self):
        """Test data validation with various edge cases."""
        # Test with None data
        with pytest.raises(TypeError):
            FinanceAnalyzer(None)
        
        # Test with list instead of DataFrame
        with pytest.raises(TypeError):
            FinanceAnalyzer([1, 2, 3])
    
    def test_calculation_precision(self, sample_finance_data):
        """Test that calculations maintain precision."""
        analyzer = FinanceAnalyzer(sample_finance_data)
        metrics = analyzer.calculate_profitability_metrics()
        
        # Test that calculations don't lose precision due to floating point errors
        for _, row in metrics.iterrows():
            # Test that gross profit calculation is correct
            expected_gross_profit = row['total_revenue'] - row['total_cost_of_goods']
            assert abs(row['gross_profit'] - expected_gross_profit) < 0.01
            
            # Test that gross margin percentage calculation is correct
            expected_gross_margin = (row['gross_profit'] / row['total_revenue']) * 100
            assert abs(row['gross_margin_pct'] - expected_gross_margin) < 0.01
            
            # Test that net margin percentage calculation is correct
            expected_net_margin = (row['total_profit_margin'] / row['total_revenue']) * 100
            assert abs(row['net_margin_pct'] - expected_net_margin) < 0.01
            
            # Test that revenue per unit calculation is correct
            expected_revenue_per_unit = row['total_revenue'] / row['total_units_sold']
            assert abs(row['revenue_per_unit'] - expected_revenue_per_unit) < 0.01 