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
- **Database**: PostgreSQL (via dbt)

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
├── requirements.txt        # Python dependencies
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

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the ecometrics directory:
```env
DBT_PROJECT_DIR=../dbt
DATABASE_URL=postgresql://user:password@localhost:5432/database
```

### dbt Integration
The app is designed to work with the existing dbt project. Ensure:
1. dbt project is properly configured
2. Database connection is established
3. Models are compiled and tested

## 🎯 Development Roadmap

### Phase 1: Basic Structure ✅
- [x] Multipage app skeleton
- [x] Navigation setup
- [x] Page layouts and placeholders

### Phase 2: Data Integration
- [ ] Connect to dbt models
- [ ] Load and display raw data
- [ ] Implement data quality checks

### Phase 3: Analytics & Visualization
- [ ] ESG metrics dashboard
- [ ] Financial analysis charts
- [ ] Supply chain optimization tools
- [ ] Customer insights analytics

### Phase 4: Advanced Features
- [ ] Interactive forecasting models
- [ ] Real-time data updates
- [ ] Custom visualization builder
- [ ] Export and reporting tools

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