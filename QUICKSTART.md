# 🚀 Quick Start Guide

Get up and running with the PackagingCo BI Portfolio in minutes!

## Prerequisites

- Python 3.8 or higher
- Git
- Basic familiarity with command line

## Quick Setup (5 minutes)

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
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
streamlit run streamlit_app/app.py
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
dbt seed
dbt run
dbt test
cd ..
```

### 3. Start Dashboard
```bash
streamlit run streamlit_app/app.py
```

## What You'll See

### 📊 Dashboard Pages
- **Overview**: Executive summary and key metrics
- **ESG Insights**: Sustainability performance analysis
- **Financial Analysis**: Revenue, profit, and growth metrics
- **Forecasting**: Sales projections and trend analysis
- **Combined Insights**: ESG-Finance integration
- **Data Browser**: Interactive data exploration with filtering, search, and export capabilities

### 📈 Key Features
- Interactive visualizations with Plotly
- Real-time data filtering
- Business insights and recommendations
- Scenario analysis capabilities
- Comprehensive data browser with search and export
- Data quality insights and statistics

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
│   └── seeds/             # Sample data
├── notebooks/             # Jupyter notebooks
├── streamlit_app/         # Dashboard application
└── data/                  # Data files
```

### 🔧 Key Components
- **ESG Analyzer**: Sustainability metrics and insights
- **Finance Analyzer**: Financial performance analysis
- **Sales Forecaster**: Revenue projections
- **Data Loader**: Database connectivity utilities
- **Data Browser**: Interactive data exploration and export tools

## Next Steps

### 📚 Learn More
- Read the full [README.md](README.md) for detailed documentation
- Explore the [notebooks/](notebooks/) for analysis examples
- Check [dbt/](dbt/) for data transformation logic

### 🛠️ Development
- Modify `src/packagingco_insights/` for custom analysis
- Add new dbt models in `dbt/models/`
- Extend the dashboard in `streamlit_app/`

### 🚀 Production
- Use the [Dockerfile](deployment/Dockerfile) for containerization
- Check the [Airflow DAG](airflow/dag_bi_portfolio.py) for orchestration
- Deploy to your preferred platform

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
streamlit run streamlit_app/app.py --server.port 8502
```

**Import errors**
```bash
# Reinstall the package
pip install -e .
# Check Python path
python -c "import sys; print(sys.path)"
```

### Getting Help
- Check the [README.md](README.md) for detailed documentation
- Review error messages in the terminal
- Ensure all dependencies are installed correctly

## Business Context

This BI portfolio answers the key question:
**"How can PackagingCo drive ESG goals without compromising financial health?"**

The dashboard provides:
- 🌱 ESG performance tracking
- 💰 Financial performance analysis
- 📈 Forecasting and trends
- 🔄 Integrated insights

Each visualization and metric is designed to support real business decisions around sustainability and profitability.

---

**Ready to explore?** Start with the Overview page in the dashboard! 🎯 