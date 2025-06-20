"""
Integration tests for the packagingco_insights package.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.packagingco_insights.analysis.finance_analysis import FinanceAnalyzer
from src.packagingco_insights.analysis.esg_analysis import ESGAnalyzer
from src.packagingco_insights.analysis.forecasting import SalesForecaster
from src.packagingco_insights.utils.data_loader import check_data_quality


class TestIntegration:
    """Integration tests for the complete analysis pipeline."""
    
    @pytest.fixture
    def integrated_test_data(self):
        """Create comprehensive test data for integration testing."""
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='ME')
        product_lines = ['Beverage Containers', 'Food Packaging', 'Industrial Packaging']
        regions = ['North America', 'Europe', 'Asia Pacific']
        facilities = ['Facility A', 'Facility B', 'Facility C']
        
        data = []
        for date in dates:
            for product in product_lines:
                for region in regions:
                    for facility in facilities:
                        # Financial metrics
                        revenue = np.random.uniform(100000, 500000)
                        cog = revenue * np.random.uniform(0.4, 0.7)
                        operating_cost = revenue * np.random.uniform(0.1, 0.3)
                        profit_margin = revenue - cog - operating_cost
                        units_sold = np.random.randint(1000, 10000)
                        
                        # ESG metrics
                        emissions = np.random.uniform(100, 1000)
                        energy = np.random.uniform(5000, 50000)
                        recycled_pct = np.random.uniform(20, 80)
                        virgin_pct = 100 - recycled_pct
                        recycling_rate = np.random.uniform(60, 95)
                        waste = np.random.uniform(50, 500)
                        
                        data.append({
                            'date': date,
                            'product_line': product,
                            'region': region,
                            'facility': facility,
                            'total_revenue': revenue,
                            'total_cost_of_goods': cog,
                            'total_operating_cost': operating_cost,
                            'total_profit_margin': profit_margin,
                            'total_units_sold': units_sold,
                            'total_emissions_kg_co2': emissions,
                            'total_energy_consumption_kwh': energy,
                            'avg_recycled_material_pct': recycled_pct,
                            'avg_virgin_material_pct': virgin_pct,
                            'avg_recycling_rate_pct': recycling_rate,
                            'total_waste_generated_kg': waste,
                            'revenue': revenue,  # For forecasting
                            'units_sold': units_sold  # For forecasting
                        })
        
        return pd.DataFrame(data)
    
    @pytest.mark.integration
    def test_complete_analysis_pipeline(self, integrated_test_data):
        """Test the complete analysis pipeline from data to insights."""
        # Step 1: Data quality check
        quality_report = check_data_quality(integrated_test_data)
        assert quality_report['total_rows'] > 0
        assert quality_report['total_columns'] > 0
        
        # Step 2: Financial analysis
        finance_data = integrated_test_data[['date', 'product_line', 'region', 
                                           'total_revenue', 'total_cost_of_goods',
                                           'total_operating_cost', 'total_profit_margin',
                                           'total_units_sold']].copy()
        finance_analyzer = FinanceAnalyzer(finance_data)
        
        # Test financial calculations
        profitability = finance_analyzer.calculate_profitability_metrics()
        assert len(profitability) > 0
        assert 'gross_profit' in profitability.columns
        
        revenue_trends = finance_analyzer.calculate_revenue_trends()
        assert len(revenue_trends) > 0
        assert 'total_revenue' in revenue_trends.columns
        
        # Step 3: ESG analysis
        esg_data = integrated_test_data[['date', 'product_line', 'facility',
                                       'total_emissions_kg_co2', 'total_energy_consumption_kwh',
                                       'avg_recycled_material_pct', 'avg_virgin_material_pct',
                                       'avg_recycling_rate_pct', 'total_waste_generated_kg']].copy()
        esg_analyzer = ESGAnalyzer(esg_data)
        
        # Test ESG calculations
        esg_scores = esg_analyzer.calculate_esg_score()
        assert len(esg_scores) > 0
        assert 'esg_score' in esg_scores.columns
        
        material_efficiency = esg_analyzer.calculate_material_efficiency()
        assert len(material_efficiency) > 0
        assert 'waste_per_kwh' in material_efficiency.columns
        
        # Step 4: Sales forecasting
        sales_data = integrated_test_data[['date', 'product_line', 'revenue', 'units_sold']].copy()
        sales_forecaster = SalesForecaster(sales_data)
        
        # Test forecasting
        forecast = sales_forecaster.simple_linear_forecast(periods=6)
        assert isinstance(forecast, pd.DataFrame)
        
        # Step 5: Generate insights
        financial_insights = finance_analyzer.get_financial_insights()
        esg_insights = esg_analyzer.get_esg_insights()
        forecast_insights = sales_forecaster.get_forecast_insights(forecast)
        
        assert isinstance(financial_insights, dict)
        assert isinstance(esg_insights, dict)
        assert isinstance(forecast_insights, dict)
    
    @pytest.mark.integration
    def test_cross_analysis_consistency(self, integrated_test_data):
        """Test that different analyzers produce consistent results."""
        # Extract data for different analyzers
        finance_data = integrated_test_data[['date', 'product_line', 'region', 
                                           'total_revenue', 'total_cost_of_goods',
                                           'total_operating_cost', 'total_profit_margin',
                                           'total_units_sold']].copy()
        
        esg_data = integrated_test_data[['date', 'product_line', 'facility',
                                       'total_emissions_kg_co2', 'total_energy_consumption_kwh',
                                       'avg_recycled_material_pct', 'avg_virgin_material_pct',
                                       'avg_recycling_rate_pct', 'total_waste_generated_kg']].copy()
        
        # Create analyzers
        finance_analyzer = FinanceAnalyzer(finance_data)
        esg_analyzer = ESGAnalyzer(esg_data)
        
        # Test that both analyzers can handle the same product lines
        finance_trends = finance_analyzer.calculate_revenue_trends()
        esg_trends = esg_analyzer.calculate_emissions_trends()
        
        # Both should have data for the same time periods
        assert len(finance_trends) > 0
        assert len(esg_trends) > 0
        
        # Test that product lines are consistent
        finance_products = set(finance_trends['product_line'].unique())
        esg_products = set(esg_trends['product_line'].unique())
        
        # Should have some overlap in product lines
        assert len(finance_products.intersection(esg_products)) > 0
    
    @pytest.mark.integration
    def test_data_flow_between_components(self, integrated_test_data):
        """Test data flow between different analysis components."""
        # Test that data can flow from one analyzer to another
        # This simulates a real-world scenario where data is processed sequentially
        
        # Step 1: Start with raw data
        raw_data = integrated_test_data.copy()
        assert len(raw_data) > 0
        
        # Step 2: Process through financial analyzer
        finance_data = raw_data[['date', 'product_line', 'region', 
                               'total_revenue', 'total_cost_of_goods',
                               'total_operating_cost', 'total_profit_margin',
                               'total_units_sold']].copy()
        finance_analyzer = FinanceAnalyzer(finance_data)
        
        # Step 3: Use financial results to filter ESG data
        profitable_products = finance_analyzer.calculate_profitability_metrics()
        profitable_products = profitable_products[profitable_products['gross_margin_pct'] > 20]
        
        # Step 4: Analyze ESG for profitable products only
        profitable_product_lines = profitable_products['product_line'].unique()
        esg_data_filtered = integrated_test_data[
            integrated_test_data['product_line'].isin(profitable_product_lines)
        ][['date', 'product_line', 'facility',
           'total_emissions_kg_co2', 'total_energy_consumption_kwh',
           'avg_recycled_material_pct', 'avg_virgin_material_pct',
           'avg_recycling_rate_pct', 'total_waste_generated_kg']].copy()
        
        esg_analyzer = ESGAnalyzer(esg_data_filtered)
        esg_scores = esg_analyzer.calculate_esg_score()
        
        # Step 5: Use ESG scores to prioritize forecasting
        high_esg_products = esg_scores[esg_scores['esg_score'] > 70]['product_line'].unique()
        
        sales_data_filtered = integrated_test_data[
            integrated_test_data['product_line'].isin(high_esg_products)
        ][['date', 'product_line', 'revenue', 'units_sold']].copy()
        
        sales_forecaster = SalesForecaster(sales_data_filtered)
        forecast = sales_forecaster.simple_linear_forecast(periods=6)
        
        # All steps should complete successfully
        assert len(profitable_products) > 0
        assert len(esg_scores) > 0
        assert isinstance(forecast, pd.DataFrame)
    
    @pytest.mark.integration
    def test_error_handling_across_components(self, integrated_test_data):
        """Test error handling across different analysis components."""
        # Test that errors in one component don't break the entire pipeline
        
        # Create data with some issues
        problematic_data = integrated_test_data.copy()
        
        # Add some invalid values
        problematic_data.loc[0, 'total_revenue'] = -1000  # Negative revenue
        problematic_data.loc[1, 'total_emissions_kg_co2'] = np.nan  # Missing emissions
        
        # Test that analyzers handle problematic data gracefully
        try:
            finance_data = problematic_data[['date', 'product_line', 'region', 
                                           'total_revenue', 'total_cost_of_goods',
                                           'total_operating_cost', 'total_profit_margin',
                                           'total_units_sold']].copy()
            finance_analyzer = FinanceAnalyzer(finance_data)
            
            # Should still be able to calculate metrics
            profitability = finance_analyzer.calculate_profitability_metrics()
            assert len(profitability) > 0
            
        except Exception as e:
            # If there's an error, it should be handled gracefully
            assert "error" in str(e).lower() or "invalid" in str(e).lower()
        
        try:
            esg_data = problematic_data[['date', 'product_line', 'facility',
                                       'total_emissions_kg_co2', 'total_energy_consumption_kwh',
                                       'avg_recycled_material_pct', 'avg_virgin_material_pct',
                                       'avg_recycling_rate_pct', 'total_waste_generated_kg']].copy()
            esg_analyzer = ESGAnalyzer(esg_data)
            
            # Should still be able to calculate ESG scores
            esg_scores = esg_analyzer.calculate_esg_score()
            assert len(esg_scores) > 0
            
        except Exception as e:
            # If there's an error, it should be handled gracefully
            assert "error" in str(e).lower() or "invalid" in str(e).lower()
    
    @pytest.mark.integration
    def test_performance_with_large_dataset(self):
        """Test performance with a larger dataset."""
        # Create a larger dataset for performance testing
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')  # Daily data
        product_lines = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
        regions = ['Region 1', 'Region 2', 'Region 3']
        
        data = []
        for date in dates[::30]:  # Sample every 30 days to keep it manageable
            for product in product_lines:
                for region in regions:
                    revenue = np.random.uniform(50000, 300000)
                    cog = revenue * np.random.uniform(0.4, 0.7)
                    operating_cost = revenue * np.random.uniform(0.1, 0.3)
                    profit_margin = revenue - cog - operating_cost
                    units_sold = np.random.randint(500, 5000)
                    
                    data.append({
                        'date': date,
                        'product_line': product,
                        'region': region,
                        'total_revenue': revenue,
                        'total_cost_of_goods': cog,
                        'total_operating_cost': operating_cost,
                        'total_profit_margin': profit_margin,
                        'total_units_sold': units_sold,
                        'revenue': revenue,
                        'units_sold': units_sold
                    })
        
        large_dataset = pd.DataFrame(data)
        
        # Test that all analyzers can handle the larger dataset
        finance_analyzer = FinanceAnalyzer(large_dataset)
        profitability = finance_analyzer.calculate_profitability_metrics()
        assert len(profitability) > 0
        
        sales_forecaster = SalesForecaster(large_dataset)
        forecast = sales_forecaster.simple_linear_forecast(periods=3)
        assert isinstance(forecast, pd.DataFrame) 