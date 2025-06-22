# 🌱 EcoMetrics - ESG & Financial Intelligence Platform

A comprehensive Streamlit dashboard showcasing ESG and financial analytics with **hybrid data architecture** - supporting both dbt models and sample data.

## 🚀 Features

- **Hybrid Data Architecture**: Automatically detects and uses dbt models when available, falls back to sample data
- **Real-time Data Source Indicators**: Shows which data source is being used (dbt models vs sample data)
- **Interactive Filters**: Date ranges, product lines, and dynamic filtering
- **Multi-page Dashboard**: ESG Insights, Financial Analysis, Forecasting, Combined Insights, and Data Browser
- **Responsive Design**: Works on desktop and mobile devices

## 📊 Data Sources

The app intelligently handles multiple data sources:

### 🎯 Primary: dbt Models (When Available)
- **fact_esg_monthly**: Aggregated ESG metrics by month
- **fact_financial_monthly**: Financial performance metrics
- **stg_sales_data**: Sales transaction data

### 🔄 Fallback: Sample Data
- **sample_esg_data.csv**: Raw ESG metrics
- **sample_sales_data.csv**: Sales transaction data
- **Generated Sample Data**: Minimal data when files aren't available

## 🛠️ Setup & Deployment

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo>
   cd bi-portfolio
   ```

2. **Install dependencies**
   ```bash
   cd streamlit_app
   pip install -r requirements.txt
   ```

3. **Set up dbt models (optional but recommended)**
   ```bash
   cd ../dbt
   dbt deps
   dbt run
   ```

4. **Run the Streamlit app**
   ```bash
   cd ../streamlit_app
   streamlit run EcoMetrics.py
   ```

### Streamlit Cloud Deployment

The app is designed to work immediately on Streamlit Cloud:

1. **Automatic Setup**: The app will automatically detect available data sources
2. **Sample Data**: Uses sample CSV files if dbt models aren't available
3. **No Manual Configuration**: Works out of the box

### Showcasing dbt Models

To showcase your dbt expertise:

1. **Run dbt locally first**:
   ```bash
   cd dbt
   dbt run
   ```

2. **Upload the generated database**:
   - The `data/processed/portfolio.duckdb` file will be used if available
   - The app will show "dbt Models" indicators in the sidebar

3. **Data Source Indicators**:
   - ✅ **Green**: dbt Models (shows your dbt expertise)
   - ℹ️ **Blue**: Sample CSV (processed sample data)
   - ⚠️ **Yellow**: Generated Sample (fallback data)

## 📁 Project Structure

```
streamlit_app/
├── EcoMetrics.py              # Main app entry point
├── setup_dbt.py              # dbt setup script
├── requirements.txt           # Python dependencies
├── components/
│   ├── shared_controls.py    # Sidebar filters
│   └── responsive_layout.py  # Responsive design utilities
├── pages/
│   ├── 1_🌱_ESG_Insights.py
│   ├── 2_💰_Financial_Analysis.py
│   ├── 3_📈_Forecasting.py
│   ├── 4_🔄_Combined_Insights.py
│   └── 5_📋_Data_Browser.py
└── assets/                   # Static assets
```

## 🎯 Business Value

This dashboard answers the key business question:
**"How can PackagingCo drive ESG goals without compromising financial health?"**

### Key Metrics Tracked:
- **ESG Performance**: CO2 emissions, recycled material %, energy efficiency
- **Financial Health**: Revenue, profit margins, cost analysis
- **Trends**: Monthly performance tracking and forecasting
- **Correlations**: ESG vs Financial performance relationships

## 🔧 Technical Architecture

### Data Flow:
1. **Data Loading**: Hybrid approach with automatic fallback
2. **Data Processing**: Real-time filtering and aggregation
3. **Visualization**: Interactive Plotly charts
4. **User Interface**: Responsive Streamlit components

### Key Technologies:
- **Streamlit**: Web application framework
- **dbt**: Data transformation and modeling
- **DuckDB**: Embedded analytical database
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation and analysis

## 🚀 Deployment Tips

### For Portfolio Showcase:
1. **Include dbt models**: Run `dbt run` locally and include the database file
2. **Document the process**: Show your dbt expertise in the README
3. **Highlight the hybrid approach**: Demonstrate both technical skills and practical deployment

### For Production Use:
1. **Set up automated dbt runs**: Use Airflow or similar for data pipeline
2. **Add authentication**: Implement user access controls
3. **Monitor performance**: Add logging and performance metrics

## 📈 Future Enhancements

- **Real-time data feeds**: Connect to live data sources
- **Advanced forecasting**: Machine learning models for predictions
- **User management**: Multi-user access and permissions
- **API integration**: REST API for external access
- **Mobile app**: Native mobile application

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🌱 Built with Streamlit, dbt, and ❤️ for sustainable business intelligence** 