"""
Tests for supply chain analysis module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.packagingco_insights.analysis.supply_chain_analysis import (
    SupplyChainAnalyzer, analyze_supply_chain_data, generate_supply_chain_report
)


@pytest.fixture
def sample_supply_chain_data():
    """Create sample supply chain data for testing."""
    np.random.seed(42)
    
    # Generate sample data
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    suppliers = ['Supplier A', 'Supplier B', 'Supplier C']
    
    data = []
    for date in dates:
        for supplier in suppliers:
            if np.random.random() > 0.3:  # 70% chance of having an order
                order_quantity = np.random.randint(100, 10000)
                unit_cost = np.random.uniform(2.0, 10.0)
                order_value = order_quantity * unit_cost
                
                # Delivery dates
                expected_delivery = date + timedelta(days=np.random.randint(3, 10))
                delivery_variance = np.random.randint(-2, 5)  # Some late, some early
                actual_delivery = expected_delivery + timedelta(days=delivery_variance)
                on_time_delivery = actual_delivery <= expected_delivery
                
                # Quality metrics
                quality_issues = np.random.random() < 0.1  # 10% chance of quality issues
                defect_quantity = np.random.randint(0, int(order_quantity * 0.05)) if quality_issues else 0
                
                # Supplier ratings
                supplier_reliability = np.random.uniform(0.85, 0.98)
                sustainability_rating = np.random.uniform(2.5, 5.0)
                
                data.append({
                    'date': date,
                    'supplier': supplier,
                    'order_id': f'PO_{date.strftime("%Y%m%d")}_{np.random.randint(1000, 9999)}',
                    'order_quantity': order_quantity,
                    'order_value': order_value,
                    'expected_delivery': expected_delivery,
                    'actual_delivery': actual_delivery,
                    'on_time_delivery': on_time_delivery,
                    'quality_issues': quality_issues,
                    'defect_quantity': defect_quantity,
                    'supplier_reliability': supplier_reliability,
                    'sustainability_rating': sustainability_rating
                })
    
    return pd.DataFrame(data)


class TestSupplyChainAnalyzer:
    """Test the SupplyChainAnalyzer class."""
    
    def test_initialization(self, sample_supply_chain_data):
        """Test analyzer initialization."""
        analyzer = SupplyChainAnalyzer(sample_supply_chain_data)
        assert analyzer.data is not None
        assert len(analyzer.data) > 0
    
    def test_data_validation(self):
        """Test data validation with missing columns."""
        invalid_data = pd.DataFrame({'date': ['2023-01-01'], 'supplier': ['Test']})
        
        with pytest.raises(ValueError, match="Missing required columns"):
            SupplyChainAnalyzer(invalid_data)
    
    def test_supplier_performance_summary(self, sample_supply_chain_data):
        """Test supplier performance summary generation."""
        analyzer = SupplyChainAnalyzer(sample_supply_chain_data)
        summary = analyzer.get_supplier_performance_summary()
        
        assert isinstance(summary, pd.DataFrame)
        assert len(summary) == len(sample_supply_chain_data['supplier'].unique())
        assert 'supplier' in summary.columns
        assert 'total_orders' in summary.columns
        assert 'on_time_delivery_rate_pct' in summary.columns
        assert 'avg_defect_rate' in summary.columns
    
    def test_delivery_performance_analysis(self, sample_supply_chain_data):
        """Test delivery performance analysis."""
        analyzer = SupplyChainAnalyzer(sample_supply_chain_data)
        analysis = analyzer.get_delivery_performance_analysis()
        
        assert isinstance(analysis, dict)
        assert 'overall_on_time_rate' in analysis
        assert 'supplier_delivery_performance' in analysis
        assert 'monthly_delivery_trends' in analysis
        assert 'delivery_performance_categories' in analysis
        
        # Check that on-time rate is between 0 and 100
        assert 0 <= analysis['overall_on_time_rate'] <= 100
    
    def test_quality_control_analysis(self, sample_supply_chain_data):
        """Test quality control analysis."""
        analyzer = SupplyChainAnalyzer(sample_supply_chain_data)
        analysis = analyzer.get_quality_control_analysis()
        
        assert isinstance(analysis, dict)
        assert 'overall_quality_metrics' in analysis
        assert 'supplier_quality_performance' in analysis
        assert 'monthly_quality_trends' in analysis
        assert 'quality_categories' in analysis
        
        # Check quality metrics
        metrics = analysis['overall_quality_metrics']
        assert metrics['total_orders'] > 0
        assert metrics['avg_defect_rate'] >= 0
    
    def test_sustainability_analysis(self, sample_supply_chain_data):
        """Test sustainability analysis."""
        analyzer = SupplyChainAnalyzer(sample_supply_chain_data)
        analysis = analyzer.get_sustainability_analysis()
        
        assert isinstance(analysis, dict)
        assert 'overall_sustainability_metrics' in analysis
        assert 'supplier_sustainability_performance' in analysis
        assert 'sustainability_categories' in analysis
        assert 'monthly_sustainability_trends' in analysis
        
        # Check sustainability metrics
        metrics = analysis['overall_sustainability_metrics']
        assert 1 <= metrics['avg_sustainability_rating'] <= 5
    
    def test_cost_analysis(self, sample_supply_chain_data):
        """Test cost analysis."""
        analyzer = SupplyChainAnalyzer(sample_supply_chain_data)
        analysis = analyzer.get_cost_analysis()
        
        assert isinstance(analysis, dict)
        assert 'overall_cost_metrics' in analysis
        assert 'monthly_cost_trends' in analysis
        assert 'supplier_cost_performance' in analysis
        assert 'cost_quality_correlation' in analysis
        
        # Check cost metrics
        metrics = analysis['overall_cost_metrics']
        assert metrics['total_order_value'] > 0
        assert metrics['avg_unit_cost'] > 0
    
    def test_supplier_risk_assessment(self, sample_supply_chain_data):
        """Test supplier risk assessment."""
        analyzer = SupplyChainAnalyzer(sample_supply_chain_data)
        risk_assessment = analyzer.get_supplier_risk_assessment()
        
        assert isinstance(risk_assessment, pd.DataFrame)
        assert 'supplier' in risk_assessment.columns
        assert 'overall_risk_score' in risk_assessment.columns
        assert 'risk_category' in risk_assessment.columns
        
        # Check that risk scores are reasonable
        assert risk_assessment['overall_risk_score'].min() >= 0
        assert risk_assessment['overall_risk_score'].max() <= 100
    
    def test_key_insights(self, sample_supply_chain_data):
        """Test key insights generation."""
        analyzer = SupplyChainAnalyzer(sample_supply_chain_data)
        insights = analyzer.get_key_insights()
        
        assert isinstance(insights, list)
        
        for insight in insights:
            assert 'category' in insight
            assert 'insight' in insight
            assert 'impact' in insight
            assert 'recommendation' in insight
    
    def test_recommendations(self, sample_supply_chain_data):
        """Test recommendations generation."""
        analyzer = SupplyChainAnalyzer(sample_supply_chain_data)
        recommendations = analyzer.get_recommendations()
        
        assert isinstance(recommendations, list)
        
        for rec in recommendations:
            assert 'category' in rec
            assert 'priority' in rec
            assert 'action' in rec
            assert 'expected_impact' in rec


class TestSupplyChainAnalysisFunctions:
    """Test the convenience functions."""
    
    def test_analyze_supply_chain_data(self, sample_supply_chain_data):
        """Test the analyze_supply_chain_data function."""
        analysis = analyze_supply_chain_data(sample_supply_chain_data)
        
        assert isinstance(analysis, dict)
        assert 'supplier_performance' in analysis
        assert 'delivery_analysis' in analysis
        assert 'quality_analysis' in analysis
        assert 'sustainability_analysis' in analysis
        assert 'cost_analysis' in analysis
        assert 'risk_assessment' in analysis
        assert 'key_insights' in analysis
        assert 'recommendations' in analysis
    
    def test_generate_supply_chain_report(self, sample_supply_chain_data):
        """Test the generate_supply_chain_report function."""
        report = generate_supply_chain_report(sample_supply_chain_data)
        
        assert isinstance(report, str)
        assert len(report) > 0
        assert 'SUPPLY CHAIN ANALYSIS REPORT' in report
        assert 'EXECUTIVE SUMMARY' in report
        assert 'KEY INSIGHTS' in report
        assert 'RECOMMENDATIONS' in report


class TestSupplyChainAnalysisEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_data(self):
        """Test handling of empty data."""
        empty_data = pd.DataFrame()
        
        with pytest.raises(ValueError):
            SupplyChainAnalyzer(empty_data)
    
    def test_single_supplier(self):
        """Test analysis with single supplier."""
        single_supplier_data = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'supplier': ['Supplier A', 'Supplier A'],
            'order_id': ['PO_001', 'PO_002'],
            'order_quantity': [100, 200],
            'order_value': [1000, 2000],
            'expected_delivery': ['2023-01-05', '2023-01-06'],
            'actual_delivery': ['2023-01-05', '2023-01-07'],
            'on_time_delivery': [True, False],
            'quality_issues': [False, False],
            'defect_quantity': [0, 0],
            'supplier_reliability': [0.95, 0.95],
            'sustainability_rating': [4.5, 4.5]
        })
        
        analyzer = SupplyChainAnalyzer(single_supplier_data)
        summary = analyzer.get_supplier_performance_summary()
        
        assert len(summary) == 1
        assert summary.iloc[0]['supplier'] == 'Supplier A'
    
    def test_zero_quantities(self):
        """Test handling of zero quantities."""
        zero_quantity_data = pd.DataFrame({
            'date': ['2023-01-01'],
            'supplier': ['Supplier A'],
            'order_id': ['PO_001'],
            'order_quantity': [0],
            'order_value': [0],
            'expected_delivery': ['2023-01-05'],
            'actual_delivery': ['2023-01-05'],
            'on_time_delivery': [True],
            'quality_issues': [False],
            'defect_quantity': [0],
            'supplier_reliability': [0.95],
            'sustainability_rating': [4.5]
        })
        
        analyzer = SupplyChainAnalyzer(zero_quantity_data)
        
        # Should not raise an error
        summary = analyzer.get_supplier_performance_summary()
        assert len(summary) == 1
    
    def test_all_late_deliveries(self):
        """Test analysis when all deliveries are late."""
        late_delivery_data = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'supplier': ['Supplier A', 'Supplier A'],
            'order_id': ['PO_001', 'PO_002'],
            'order_quantity': [100, 200],
            'order_value': [1000, 2000],
            'expected_delivery': ['2023-01-05', '2023-01-06'],
            'actual_delivery': ['2023-01-07', '2023-01-08'],
            'on_time_delivery': [False, False],
            'quality_issues': [False, False],
            'defect_quantity': [0, 0],
            'supplier_reliability': [0.95, 0.95],
            'sustainability_rating': [4.5, 4.5]
        })
        
        analyzer = SupplyChainAnalyzer(late_delivery_data)
        delivery_analysis = analyzer.get_delivery_performance_analysis()
        
        assert delivery_analysis['overall_on_time_rate'] == 0.0
    
    def test_all_quality_issues(self):
        """Test analysis when all orders have quality issues."""
        quality_issue_data = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'supplier': ['Supplier A', 'Supplier A'],
            'order_id': ['PO_001', 'PO_002'],
            'order_quantity': [100, 200],
            'order_value': [1000, 2000],
            'expected_delivery': ['2023-01-05', '2023-01-06'],
            'actual_delivery': ['2023-01-05', '2023-01-06'],
            'on_time_delivery': [True, True],
            'quality_issues': [True, True],
            'defect_quantity': [5, 10],
            'supplier_reliability': [0.95, 0.95],
            'sustainability_rating': [4.5, 4.5]
        })
        
        analyzer = SupplyChainAnalyzer(quality_issue_data)
        quality_analysis = analyzer.get_quality_control_analysis()
        
        metrics = quality_analysis['overall_quality_metrics']
        assert metrics['quality_issue_rate'] == 100.0


if __name__ == "__main__":
    pytest.main([__file__]) 