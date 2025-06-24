import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
import pandas as pd
from ecometrics.data_connector import load_finance_data
from packagingco_insights.analysis.forecasting import SalesForecaster

# Load finance data
def main():
    finance_data, status = load_finance_data()
    print(f"Data status: {status}")
    print(f"Finance data shape: {finance_data.shape}")

    # Prepare data for SalesForecaster (match what 6_Forecasting.py does)
    if all(col in finance_data.columns for col in ["date", "total_revenue", "total_units_sold", "product_line"]):
        sf_data = finance_data.rename(columns={
            "total_revenue": "revenue",
            "total_units_sold": "units_sold"
        })
        sf_data = sf_data[["date", "revenue", "units_sold", "product_line"]]
    else:
        raise Exception("Finance data is missing required columns for advanced forecasting.")

    # Instantiate SalesForecaster
    forecaster = SalesForecaster(sf_data)

    # Run backtest/model comparison
    results = forecaster.compare_forecasting_models(
        periods=6,           # Number of periods to forecast in the test set
        group_by='product_line',
        test_size=0.3        # 30% of data for testing
    )

    # Show real error metrics
    metrics = results.get('performance_metrics')
    if metrics is not None and not metrics.empty:
        print("\nModel Backtest Metrics (averaged across product lines):")
        print(metrics.groupby('model')[['mae', 'rmse', 'mape']].mean().round(2))
    else:
        print("No backtest metrics available.")

    # Optionally, print actual vs. predicted for a sample product line
    if metrics is not None and not metrics.empty:
        for model in metrics['model'].unique():
            print(f"\nSample results for model: {model}")
            sample = metrics[metrics['model'] == model].head()
            print(sample)

if __name__ == "__main__":
    main() 