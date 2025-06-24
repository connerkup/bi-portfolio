# 🌱 EcoMetrics - Business Intelligence Portfolio

A comprehensive Streamlit-based business intelligence dashboard that combines environmental, social, and governance (ESG) insights with financial analysis and supply chain optimization.

## 🚀 Features

### 📊 Dashboard Pages
- **Home**: Overview and navigation hub
- **ESG Insights**: Sustainability metrics and environmental impact analysis
- **Financial Analysis**: Revenue, profitability, and financial performance metrics
- **Supply Chain Insights**: Inventory management and logistics optimization
- **Customer Insights**: Customer behavior analysis and segmentation
- **Data Browser**: Interactive data exploration and dbt model browser
- **Forecasting**: Advanced forecasting models for business planning

### 🛠️ Technology Stack
- **Frontend**: Streamlit (latest multipage app structure)
- **Data Processing**: dbt (data build tool)
- **Analytics**: Python (pandas, numpy, scikit-learn)
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Database**: DuckDB (local file-based database)

## 📁 Project Structure

```
ecometrics/
├── Home.py                 # Main entry point
├── pages/                  # Multipage app pages
│   ├── 1_ESG_Insights.py
│   ├── 2_Financial_Analysis.py
│   ├── 3_Supply_Chain_Insights.py
│   ├── 4_Customer_Insights.py
│   ├── 5_Data_Browser.py
│   └── 6_Forecasting.py
├── data_connector.py       # Database connection and dbt integration
├── portfolio.duckdb        # Production database with dbt models
├── requirements.txt        # Python dependencies
├── prepare_for_deployment.py # Automated deployment preparation
├── STREAMLIT_CLOUD_DEPLOYMENT.md # Deployment guide
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda
- Access to the dbt project (../dbt/)

### Installation

1. **Clone and navigate to the project**
   ```bash
   cd ecometrics
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit app**
   ```bash
   streamlit run Home.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 📊 Data Sources

The app integrates with the existing dbt project and data sources:

- **Raw Data**: `../data/raw/`
  - `sample_esg_data.csv`
  - `sample_sales_data.csv`

- **dbt Models**: `../dbt/models/`
  - Finance models
  - Sustainability models
  - Supply chain models
  - Customer insights models

- **Production Database**: `portfolio.duckdb`
  - Contains all processed dbt models
  - Ready for deployment to Streamlit Cloud

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the ecometrics directory:
```env
DBT_PROJECT_DIR=../dbt
DATABASE_URL=duckdb:///portfolio.duckdb
```

### dbt Integration
The app is designed to work with the existing dbt project. Ensure:
1. dbt project is properly configured
2. Database connection is established
3. Models are compiled and tested

## 🚀 Deployment

### Streamlit Cloud Deployment

1. **Prepare for deployment**:
   ```bash
   python prepare_for_deployment.py
   ```

2. **Deploy to Streamlit Cloud**:
   - Connect your GitHub repository to Streamlit Cloud
   - Set main file to: `ecometrics/Home.py`
   - Set requirements file to: `ecometrics/requirements.txt`

3. **Verify deployment**:
   - Check the Data Browser page for database connection
   - Verify all dashboard pages are functional

### Local Development

For local development with live dbt integration:

1. **Build dbt models**:
   ```bash
   cd ../dbt
   dbt deps
   dbt run
   dbt test
   ```

2. **Update database**:
   ```bash
   cp ../dbt/data/processed/portfolio.duckdb .
   ```

## 📈 Current Implementation Status

### ✅ Completed Features
- **ESG Analytics**: Full sustainability metrics dashboard
- **Financial Analysis**: Comprehensive financial reporting
- **Supply Chain Insights**: Complete supply chain optimization
- **Customer Insights**: Advanced customer analytics
- **Data Browser**: Interactive dbt model exploration
- **Forecasting**: Advanced time series forecasting
- **Responsive Design**: Mobile-friendly interface
- **Data Quality**: 105+ automated tests

### 🎯 Key Capabilities
- Real-time data visualization with Plotly
- Multi-dimensional filtering and drill-down
- Export capabilities for reports
- Comprehensive ESG and financial metrics
- Supply chain optimization insights
- Customer segmentation and analysis
- Advanced forecasting models
- Production-ready data pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is part of the BI Portfolio and follows the same licensing terms.

## 🆘 Support

For questions or issues:
1. Check the existing documentation
2. Review the dbt project setup
3. Create an issue in the repository

---

**Built with ❤️ using Streamlit and dbt** 