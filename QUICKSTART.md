# 🚀 Quick Start Guide

Get up and running with the EcoMetrics BI Portfolio in minutes!

## Prerequisites

- Python 3.8 or higher
- Git
- Basic familiarity with command line

## Quick Setup (5 minutes)

### 1. Clone and Navigate
```bash
git clone https://github.com/connerkup/bi-portfolio
cd bi-portfolio
```

### 2. Run Setup Script
```bash
python setup.py
```

This will automatically:
- ✅ Install all dependencies
- ✅ Set up the database
- ✅ Run dbt transformations
- ✅ Test the installation

### 3. Start the Dashboard
```bash
cd ecometrics
streamlit run Home.py
```

Open your browser to `http://localhost:8501` 🎉

## Manual Setup (if needed)

If the setup script doesn't work, follow these steps:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Set Up Database
```bash
cd dbt
dbt deps
dbt seed
dbt run
dbt test
cd ..
```

### 3. Start Dashboard
```bash
cd ecometrics
streamlit run Home.py
```

## What You'll See

### 📊 Dashboard Pages
- **Home**: Executive summary and navigation hub
- **ESG Insights**: Sustainability performance analysis and environmental impact
- **Financial Analysis**: Revenue, profit, and growth metrics with forecasting
- **Supply Chain Insights**: Inventory management and operational efficiency
- **Customer Insights**: Customer behavior analysis and segmentation
- **Data Browser**: Interactive data exploration with filtering, search, and export capabilities
- **Forecasting**: Advanced time series forecasting and trend analysis

### 📈 Key Features
- Interactive visualizations with Plotly and Altair
- Real-time data filtering and drill-down capabilities
- Business insights and recommendations
- Scenario analysis capabilities
- Comprehensive data browser with search and export
- Data quality insights and statistics
- Responsive design for mobile and desktop
- Export capabilities for reports and data

## Exploring the Code

### 📁 Project Structure
```
bi-portfolio/
├── src/                    # Python package
│   └── packagingco_insights/
│       ├── analysis/       # ESG & Finance analyzers
│       └── utils/          # Data loading & utilities
├── dbt/                    # Data transformations
│   ├── models/            # SQL models
│   │   ├── finance/       # Financial analysis models
│   │   ├── sustainability/ # ESG analysis models
│   │   ├── supply_chain/  # Supply chain models
│   │   └── customer_insights/ # Customer analysis models
│   └── seeds/             # Sample data
├── ecometrics/            # Main Streamlit application
│   ├── Home.py           # Dashboard entry point
│   ├── pages/            # Multi-page navigation
│   ├── data_connector.py # Database connection logic
│   └── portfolio.duckdb  # Production database
├── notebooks/             # Jupyter notebooks
└── data/                  # Data files
```

### 🔧 Key Components
- **ESG Analyzer**: Sustainability metrics and insights
- **Finance Analyzer**: Financial performance analysis
- **Supply Chain Analyzer**: Inventory and operational optimization
- **Customer Analyzer**: Customer behavior and segmentation
- **Forecasting Engine**: Advanced time series forecasting
- **Data Connector**: Database connectivity and dbt integration
- **Data Browser**: Interactive data exploration and export tools

## Next Steps

### 📚 Learn More
- Read the full [README.md](README.md) for detailed documentation
- Explore the [notebooks/](notebooks/) for analysis examples
- Check [dbt/](dbt/) for data transformation logic

### 🛠️ Development
- Modify `src/packagingco_insights/` for custom analysis
- Add new dbt models in `dbt/models/`
- Extend the dashboard in `ecometrics/`

### 🚀 Production
- Use the [Dockerfile](deployment/Dockerfile) for containerization
- Check the [Airflow DAG](airflow/dag_bi_portfolio.py) for orchestration
- Deploy to Streamlit Cloud using `ecometrics/Home.py`

## Deployment to Streamlit Cloud

### 1. Prepare for Deployment
```bash
cd ecometrics
python prepare_for_deployment.py
```

### 2. Deploy to Streamlit Cloud
- Connect your GitHub repository to Streamlit Cloud
- Set main file to: `ecometrics/Home.py`
- Set requirements file to: `ecometrics/requirements.txt`

## Troubleshooting

### Common Issues

**Setup fails with dbt errors**
```bash
cd dbt
dbt deps  # Install dependencies first
dbt seed
dbt run
```

**Dashboard won't start**
```bash
# Check if port 8501 is available
lsof -i :8501
# Or use a different port
streamlit run Home.py --server.port 8502
```

**Import errors**
```bash
# Reinstall the package
pip install -e .
# Check Python path
python -c "import sys; print(sys.path)"
```

**Database connection issues**
```bash
# Check if database file exists
ls -la ecometrics/portfolio.duckdb
# Rebuild database if needed
cd dbt && dbt run && cd ..
cp dbt/data/processed/portfolio.duckdb ecometrics/
```

### Getting Help
- Check the [README.md](README.md) for detailed documentation
- Review error messages in the terminal
- Ensure all dependencies are installed correctly
- Check the [Data Browser](http://localhost:8501/Data_Browser) page for database status

## Business Context

This BI portfolio answers the key question:
**"How can PackagingCo drive ESG goals while optimizing financial performance and supply chain efficiency?"**

The dashboard provides:
- 🌱 ESG performance tracking and sustainability insights
- 💰 Financial performance analysis and forecasting
- 🔄 Supply chain optimization and operational efficiency
- 👥 Customer behavior analysis and segmentation
- 📈 Advanced forecasting and trend analysis
- 🔍 Comprehensive data exploration and export capabilities

Each visualization and metric is designed to support real business decisions around sustainability, profitability, and operational excellence.

---

**Ready to explore?** Start with the Home page in the dashboard! 🎯 