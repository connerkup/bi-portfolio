# PackagingCo ESG & Finance Insights – Vertical Slice BI Portfolio

## Business Question
**How can a packaging company drive ESG (Environmental, Social, Governance) goals without compromising financial health?**

This project delivers a focused vertical slice of a Business Intelligence portfolio to answer that question end-to-end. We prioritize two core analytics modules – **Sustainability & Impact Tracking** and **Finance & Sales Forecasting** – and defer the other planned modules (Supply Chain Optimization and Customer Insights) as future extensions.

By slicing vertically through the data stack, we aim to deliver stakeholder value quickly with a polished, end-to-end solution for the most critical use cases. This approach shortens feedback loops, delivers value sooner, and keeps development aligned with business outcomes.

## Project Overview

This vertical slice implements the two primary modules in full, providing a complete working prototype that spans data ingestion, transformation, analysis, and visualization for ESG impact and financial performance. The other two modules are included as stubs to indicate where future development will occur.

### Key Features
- **End-to-end implementation** of Sustainability and Finance modules, from data models to interactive dashboard
- **Business storytelling emphasis**: Each analysis directly ties to real-world decision points
- **Robust tooling**: Modern data stack with dbt, Streamlit, and DuckDB
- **Professional structure**: Modular code, version control, testing, and documentation
- **Interactive data exploration**: Comprehensive data browser with filtering, search, and export capabilities
- **Responsive design**: Mobile-friendly dashboard that works across all devices

## Core Modules (Vertical Slice Deliverables)

### 1. Sustainability & Impact Tracking Module (ESG Insights) ✅ **IMPLEMENTED**
**Objective**: Measure and track sustainability performance and translate metrics into actionable business insights.

**Key Visualizations**:
- Carbon Footprint Trends: Time-series of emissions with filters by plant/product line
- Materials Mix Analysis: Recycled vs. virgin materials usage with scenario simulation
- Impact vs. Cost Trade-off: Dynamic visualization of sustainability initiatives and their financial impact

**Decision Support**: Directly supports procurement and investment decisions in sustainability initiatives.

### 2. Finance & Sales Forecasting Module (Commercial Context) ✅ **IMPLEMENTED**
**Objective**: Provide forward-looking financial performance view contextualized with sustainability initiatives.

**Key Visualizations**:
- Sales & Revenue Forecast: Interactive forecasting with confidence intervals
- Profitability Breakdown: Cost vs. revenue analysis with ESG investment impact
- KPI Dashboard: Financial metrics alongside sustainability metrics

**Decision Support**: Informs strategic and financial planning decisions, ensuring commercial alignment.

## Repository Structure

```
├── README.md                       # Project documentation and run instructions
├── QUICKSTART.md                   # Quick start guide for immediate setup
├── pyproject.toml                  # Project metadata and dependencies
├── requirements.txt                # Python dependencies (Linux/macOS)
├── requirements-windows.txt        # Python dependencies (Windows)
├── setup.py                        # Automated setup script
├── data/                           # Data files and databases
│   ├── raw/                        # Raw input data
│   │   ├── sample_esg_data.csv     # Sample ESG metrics data
│   │   └── sample_sales_data.csv   # Sample sales data
│   └── processed/                  # Processed data and DuckDB files
├── notebooks/                      # Jupyter notebooks for EDA
│   ├── sustainability_eda.ipynb    # ESG module analysis ✅
│   ├── finance_forecasting.ipynb   # Finance module analysis ✅
│   ├── supply_chain_eda.ipynb      # Future module placeholder
│   └── customer_insights_eda.ipynb # Future module placeholder
├── dbt/                            # dbt project for data transformations
│   ├── dbt_project.yml             # dbt configuration
│   ├── profiles.yml                # Database connection settings
│   ├── models/                     # SQL models organized by module
│   │   ├── sustainability/         # ESG metrics models ✅
│   │   │   ├── stg_esg_data.sql
│   │   │   ├── fact_esg_monthly.sql
│   │   │   └── mart_esg_summary.sql
│   │   ├── finance/                # Financial metrics models ✅
│   │   │   ├── stg_sales_data.sql
│   │   │   └── fact_financial_monthly.sql
│   │   ├── supply_chain/           # Future models (placeholder)
│   │   └── customer_insights/      # Future models (placeholder)
│   ├── seeds/                      # CSV seed data
│   └── tests/                      # Data quality tests
├── src/                            # Python package for custom code
│   └── packagingco_insights/
│       ├── __init__.py
│       ├── analysis/               # Custom analysis modules
│       │   ├── __init__.py
│       │   ├── esg_analysis.py     # ESG analysis functions
│       │   ├── finance_analysis.py # Finance analysis functions
│       │   └── forecasting.py      # Sales forecasting functions
│       └── utils/                  # Utility functions
│           ├── __init__.py
│           ├── data_generator.py   # Sample data generation
│           ├── data_loader.py      # Database connectivity
│           └── visualization.py    # Chart utilities
├── streamlit_app/                  # Streamlit dashboard application
│   ├── app.py                      # Main dashboard script (587 lines)
│   ├── components/                 # Reusable dashboard components
│   └── assets/                     # Static assets
├── airflow/                        # Workflow orchestration
│   └── dag_bi_portfolio.py         # Airflow DAG for production
├── deployment/                     # Deployment configuration
│   └── Dockerfile                  # Containerization setup
└── docs/                           # Additional documentation
    ├── DATA_ARCHITECTURE.md        # Data architecture overview
    ├── DATA_BROWSER.md             # Data browser documentation
    └── DATA_VALIDATION_ANSWERS.md  # Data validation details
```

## Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation (Recommended - Automated Setup)
1. Clone the repository:
   ```bash
   git clone https://github.com/connerkup/bi-portfolio
   cd bi-portfolio
   ```

2. Run the automated setup script:
   ```bash
   python setup.py
   ```

   This will automatically:
   - ✅ Install all dependencies (platform-specific)
   - ✅ Set up the database
   - ✅ Run dbt transformations
   - ✅ Test the installation

3. Launch the dashboard:
   ```bash
   streamlit run streamlit_app/app.py
   ```

The dashboard will open at `http://localhost:8501`

### Manual Installation (Alternative)
If the setup script doesn't work, follow these steps:

1. Install dependencies:
   ```bash
   # For Linux/macOS
   pip install -r requirements.txt
   
   # For Windows
   pip install -r requirements-windows.txt
   ```

2. Set up the database:
   ```bash
   cd dbt
   dbt deps
   dbt seed
   dbt run
   dbt test
   cd ..
   ```

3. Launch the dashboard:
   ```bash
   streamlit run streamlit_app/app.py
   ```

## Detailed Usage Instructions

### Jupyter Notebooks
Explore the analysis step-by-step by opening notebooks in `notebooks/`:
- `sustainability_eda.ipynb`: ESG metrics exploration and analysis (370 lines)
- `finance_forecasting.ipynb`: Financial forecasting and modeling (3,627 lines)

### dbt Models
Run the data pipeline:
```bash
cd dbt
dbt deps        # Install dependencies
dbt seed        # Load seed data
dbt run         # Execute all models
dbt test        # Validate data quality
dbt docs generate  # Build documentation
dbt docs serve  # View documentation locally
```

### Streamlit Dashboard
The main dashboard provides:
- **Overview**: Executive summary with key ESG and financial KPIs
- **ESG Insights**: Sustainability metrics and impact analysis with interactive visualizations
- **Financial Analysis**: Sales forecasts and financial KPIs with trend analysis
- **Forecasting**: Advanced sales forecasting with scenario modeling
- **Combined Insights**: Integrated ESG-finance scenario analysis and trade-off exploration
- **Data Browser**: Interactive data exploration with filtering, search, pagination, and export capabilities for both processed and raw datasets

### Key Dashboard Features
- **Responsive Design**: Automatically adapts to mobile, tablet, and desktop screens
- **Interactive Visualizations**: Plotly charts with zoom, pan, and hover capabilities
- **Real-time Filtering**: Dynamic data filtering across all visualizations
- **Export Functionality**: Download data as CSV or Excel files
- **Business Insights**: Contextual recommendations and insights

### Airflow DAG
The included DAG script (`airflow/dag_bi_portfolio.py`) demonstrates how to orchestrate the pipeline in production. While not deployed in this project, it shows the workflow:
1. Data extraction and loading
2. dbt transformations
3. Dashboard refresh
4. Notification/alerts

## Business Impact & Storytelling

This project addresses the critical intersection of sustainability and profitability through:

- **Clear Business Question**: Every analysis ties back to the core question of balancing ESG goals with financial health
- **Decision-Driven Insights**: Visualizations are designed to inform specific business decisions
- **Scenario Analysis**: Interactive tools allow stakeholders to explore trade-offs
- **Actionable Recommendations**: Clear calls-to-action based on data insights

## Future Extensions

The following modules are planned for future development:

### Supply Chain Optimization (Phase 2)
- Procurement efficiency analysis
- Logistics optimization
- Inventory management insights
- Supplier performance tracking

### Customer Insights & Segmentation (Phase 3)
- Customer behavior analysis
- Sales by segment breakdown
- Sustainability perception analysis
- Customer loyalty and retention insights

## Technology Stack

- **Data Warehouse**: DuckDB (local) / SQLite
- **Transformation**: dbt Core with DuckDB adapter
- **Visualization**: Streamlit with Plotly/Altair
- **Orchestration**: Airflow (conceptual, included as DAG script)
- **Language**: Python, SQL
- **Deployment**: Docker containerization ready

## Platform Support

- **Linux/macOS**: Full support with all features
- **Windows**: Supported with platform-specific requirements file
- **Mobile**: Responsive dashboard design for mobile devices

## Contributing

This project follows best practices for data engineering:
- Modular code structure
- Version-controlled data models
- Comprehensive testing
- Clear documentation
- Professional packaging

## License

MIT License - see LICENSE file for details.

## Repository

**GitHub**: https://github.com/connerkup/bi-portfolio

---

**Note**: This is a vertical slice implementation focusing on the most critical ESG and Finance use cases. The modular structure allows for easy expansion to include Supply Chain and Customer Insights modules in future iterations.
