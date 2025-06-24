# 🌱 EcoMetrics - ESG & Financial Intelligence Platform

A comprehensive business intelligence platform for Environmental, Social, and Governance (ESG) metrics and financial performance analysis. Built with modern data engineering practices and designed for enterprise-scale sustainability analytics.

## 🚀 Live Demo

**[EcoMetrics Dashboard](https://ecometrics.streamlit.app)**

## 📊 Features

### **ESG Analytics** ✅
- Sustainability performance tracking
- Emissions analysis and reporting
- Material efficiency metrics
- Renewable energy usage monitoring
- Water conservation analytics

### **Financial Intelligence** ✅
- Revenue and profitability analysis
- Cost structure optimization
- Regional performance insights
- Growth trend forecasting
- Profit margin analysis

### **Supply Chain Optimization** ✅
- Inventory management and tracking
- Material flow analysis
- Operational efficiency metrics
- Supply chain cost optimization
- Sustainability impact assessment

### **Customer Insights** ✅
- Customer behavior analysis
- Segmentation and profiling
- Sustainability preferences tracking
- Customer lifetime value analysis
- Market opportunity identification

### **Interactive Dashboards** ✅
- Real-time data visualization
- Multi-dimensional filtering
- Responsive design (mobile-friendly)
- Export capabilities
- Drill-down analytics

### **Data Pipeline** ✅
- Robust ETL process with dbt
- Comprehensive data testing
- Transaction-level data processing
- Automated data validation
- Production-ready architecture

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python)
- **Data Processing**: dbt (Data Build Tool)
- **Database**: DuckDB
- **Analysis**: Pandas, Plotly, NumPy, Scikit-learn
- **Testing**: Comprehensive dbt tests
- **Deployment**: Streamlit Cloud

## 🏗️ Architecture

```
📁 bi-portfolio/
├── 📁 dbt/                    # Data transformation layer
│   ├── 📁 models/            # SQL models
│   │   ├── 📁 finance/       # Financial analysis models
│   │   ├── 📁 sustainability/ # ESG analysis models
│   │   ├── 📁 supply_chain/  # Supply chain models
│   │   └── 📁 customer_insights/ # Customer analysis models
│   ├── 📁 tests/             # Data quality tests
│   └── 📁 macros/            # Reusable SQL macros
├── 📁 ecometrics/            # Main Streamlit application
│   ├── Home.py              # Main dashboard entry point
│   ├── 📁 pages/            # Multi-page navigation
│   ├── data_connector.py    # Database connection logic
│   └── portfolio.duckdb     # Production database
├── 📁 src/                   # Python analysis modules
│   └── 📁 packagingco_insights/
└── 📁 data/                  # Raw and processed data
```

## 🚀 Quick Start

### **Local Development**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/bi-portfolio.git
   cd bi-portfolio
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the data pipeline**:
   ```bash
   cd dbt
   dbt deps
   dbt run
   dbt test
   ```

4. **Start the dashboard**:
   ```bash
   cd ecometrics
   streamlit run Home.py
   ```

5. **Access the application**:
   Open your browser to `http://localhost:8501`

### **Deployment to Streamlit Cloud**

1. **Prepare for deployment**:
   ```bash
   cd ecometrics
   python prepare_for_deployment.py
   ```

2. **Deploy to Streamlit Cloud**:
   - Connect your GitHub repository to Streamlit Cloud
   - Set main file to: `ecometrics/Home.py`
   - Set requirements file to: `ecometrics/requirements.txt`

## 📈 Key Metrics & Insights

### **Sustainability KPIs**
- **ESG Score**: Composite sustainability performance (0-100)
- **Emissions per Unit**: CO2 emissions efficiency
- **Recycled Content**: Material sustainability percentage
- **Renewable Energy**: Clean energy usage percentage
- **Water Efficiency**: Conservation and recycling metrics

### **Financial Performance**
- **Revenue Trends**: Growth and regional analysis
- **Profit Margins**: Gross and net profitability
- **Cost Optimization**: Efficiency and waste reduction
- **Market Performance**: Segment and product analysis

### **Supply Chain Metrics**
- **Inventory Turnover**: Efficiency of inventory management
- **Material Flow**: Tracking of sustainable materials
- **Operational Costs**: Supply chain cost analysis
- **Sustainability Impact**: ESG metrics across supply chain

### **Customer Analytics**
- **Customer Segments**: Behavioral and demographic analysis
- **Sustainability Preferences**: Customer ESG awareness
- **Lifetime Value**: Customer profitability analysis
- **Market Opportunities**: Growth potential identification

## 🎯 Business Value

- **Data-Driven Sustainability**: Real-time ESG performance monitoring
- **Compliance Ready**: Comprehensive reporting for ESG regulations
- **Cost Optimization**: Identify efficiency opportunities
- **Strategic Planning**: Forecast trends and plan initiatives
- **Stakeholder Communication**: Clear, visual reporting

## 🧪 Data Quality & Testing

- **105+ automated tests** ensuring data accuracy
- **Comprehensive validation** of all calculations
- **Material balance checks** (percentages sum to 100%)
- **Range validation** for all metrics
- **Business logic verification** for profit margins

## 📊 Portfolio Project

This project demonstrates:

- **End-to-end data solution** from raw data to interactive dashboards
- **Modern data engineering** practices with dbt and comprehensive testing
- **Business intelligence** development with real-world applications
- **Sustainability analytics** - a rapidly growing field in business technology
- **Production-ready architecture** suitable for enterprise deployment

Perfect for showcasing data engineering, business intelligence, and sustainability technology skills!

## 🤝 Contributing

This is a portfolio project demonstrating modern data engineering and business intelligence capabilities. Feel free to explore the code and architecture!

## 📄 License

This project is for portfolio demonstration purposes.

---

**Built with ❤️ using modern data engineering practices**
