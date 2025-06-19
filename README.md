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

## Core Modules (Vertical Slice Deliverables)

### 1. Sustainability & Impact Tracking Module (ESG Insights)
**Objective**: Measure and track sustainability performance and translate metrics into actionable business insights.

**Key Visualizations**:
- Carbon Footprint Trends: Time-series of emissions with filters by plant/product line
- Materials Mix Analysis: Recycled vs. virgin materials usage with scenario simulation
- Impact vs. Cost Trade-off: Dynamic visualization of sustainability initiatives and their financial impact

**Decision Support**: Directly supports procurement and investment decisions in sustainability initiatives.

### 2. Finance & Sales Forecasting Module (Commercial Context)
**Objective**: Provide forward-looking financial performance view contextualized with sustainability initiatives.

**Key Visualizations**:
- Sales & Revenue Forecast: Interactive forecasting with confidence intervals
- Profitability Breakdown: Cost vs. revenue analysis with ESG investment impact
- KPI Dashboard: Financial metrics alongside sustainability metrics

**Decision Support**: Informs strategic and financial planning decisions, ensuring commercial alignment.

## Repository Structure

```
├── README.md                       # Project documentation and run instructions
├── pyproject.toml                  # Project metadata and dependencies
├── requirements.txt                # Python dependencies
├── data/                           # Data files and databases
│   ├── raw/                        # Raw input data
│   └── processed/                  # Processed data and DuckDB files
├── notebooks/                      # Jupyter notebooks for EDA
│   ├── sustainability_eda.ipynb    # ESG module analysis
│   ├── finance_forecasting.ipynb   # Finance module analysis
│   ├── supply_chain_eda.ipynb      # (Placeholder) Future work
│   └── customer_insights_eda.ipynb # (Placeholder) Future work
├── dbt/                            # dbt project for data transformations
│   ├── dbt_project.yml             # dbt configuration
│   ├── profiles.yml                # Database connection settings
│   ├── models/                     # SQL models organized by module
│   │   ├── sustainability/         # ESG metrics models
│   │   ├── finance/                # Financial metrics models
│   │   ├── supply_chain/           # (Placeholder) Future models
│   │   └── customer_insights/      # (Placeholder) Future models
│   ├── seeds/                      # CSV seed data
│   └── tests/                      # Data quality tests
├── src/                            # Python package for custom code
│   ├── __init__.py
│   ├── data_processing.py          # Data manipulation utilities
│   ├── analysis/                   # Custom analysis modules
│   └── utils/                      # Utility functions
├── streamlit_app/                  # Streamlit dashboard application
│   ├── app.py                      # Main dashboard script
│   ├── pages/                      # Multi-page app structure
│   └── assets/                     # Static assets
├── airflow/                        # Workflow orchestration
│   └── dag_bi_portfolio.py         # Airflow DAG for production
└── deployment/                     # Deployment configuration
    └── Dockerfile                  # Containerization setup
```

## Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd bi-portfolio
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. Set up the database:
   ```bash
   cd dbt
   dbt seed
   dbt run
   dbt test
   ```

4. Launch the dashboard:
   ```bash
   streamlit run streamlit_app/app.py
   ```

The dashboard will open at `http://localhost:8501`

## Detailed Usage Instructions

### Jupyter Notebooks
Explore the analysis step-by-step by opening notebooks in `notebooks/`:
- `sustainability_eda.ipynb`: ESG metrics exploration and analysis
- `finance_forecasting.ipynb`: Financial forecasting and modeling

### dbt Models
Run the data pipeline:
```bash
cd dbt
dbt seed        # Load seed data (if any)
dbt run         # Execute all models
dbt test        # Validate data quality
dbt docs generate  # Build documentation
dbt docs serve  # View documentation locally
```

### Streamlit Dashboard
The main dashboard provides:
- **ESG Overview**: Sustainability metrics and impact analysis
- **Financial Overview**: Sales forecasts and financial KPIs
- **Combined Insights**: Integrated ESG-finance scenario analysis

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

### Supply Chain Optimization
- Procurement efficiency analysis
- Logistics optimization
- Inventory management insights
- Supplier performance tracking

### Customer Insights & Segmentation
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
- **Deployment**: Hugging Face Spaces (planned)

## Contributing

This project follows best practices for data engineering:
- Modular code structure
- Version-controlled data models
- Comprehensive testing
- Clear documentation
- Professional packaging

## License

[Add your license information here]

---

**Note**: This is a vertical slice implementation focusing on the most critical ESG and Finance use cases. The modular structure allows for easy expansion to include Supply Chain and Customer Insights modules in future iterations.
