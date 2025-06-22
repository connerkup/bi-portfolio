# 🚀 EcoMetrics Deployment Guide

This guide explains how to deploy EcoMetrics and showcase your dbt expertise.

## 🎯 Quick Deployment (Streamlit Cloud)

### Option 1: Deploy with Sample Data (Immediate)
1. **Push to GitHub**: Your app will work immediately with sample data
2. **Deploy to Streamlit Cloud**: Connect your GitHub repository
3. **No Configuration Needed**: The app automatically uses sample CSV files

### Option 2: Deploy with dbt Models (Showcase Mode)
1. **Run dbt locally first**:
   ```bash
   cd dbt
   dbt deps
   dbt run
   ```

2. **Include the database file**: Make sure `data/processed/portfolio.duckdb` is committed to your repository

3. **Deploy to Streamlit Cloud**: The app will automatically detect and use dbt models

## 📊 Data Source Indicators

The app shows which data source is being used:

| Indicator | Data Source | What it means |
|-----------|-------------|---------------|
| ✅ **Green** | dbt Models | Your dbt expertise is showcased |
| ℹ️ **Blue** | Sample CSV | Using processed sample data |
| ⚠️ **Yellow** | Generated Sample | Fallback minimal data |

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.8+
- Git

### Step-by-Step Setup

1. **Clone and navigate**:
   ```bash
   git clone <your-repo>
   cd bi-portfolio/streamlit_app
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up dbt (optional)**:
   ```bash
   cd ../dbt
   dbt deps
   dbt run
   ```

4. **Run the app**:
   ```bash
   cd ../streamlit_app
   streamlit run EcoMetrics.py
   ```

## 🎨 Showcasing Your dbt Skills

### For Portfolio/Interview
1. **Include dbt models**: Run `dbt run` and commit the database
2. **Document the process**: Update README with dbt setup instructions
3. **Highlight the architecture**: Explain the hybrid approach
4. **Show data lineage**: Point out the dbt model structure

### Key Talking Points
- **"The app automatically detects and uses dbt models when available"**
- **"I implemented a hybrid architecture that works in any environment"**
- **"The data source indicators show real-time which data is being used"**
- **"This demonstrates both technical skills and practical deployment considerations"**

## 🔧 Troubleshooting

### Common Issues

**Issue**: "Failed to load core dashboard data"
- **Solution**: The app will automatically fall back to sample data
- **Check**: Look at the sidebar data source indicators

**Issue**: dbt models not showing
- **Solution**: Run `dbt run` locally and commit the database file
- **Check**: Ensure `data/processed/portfolio.duckdb` exists

**Issue**: Sample data not loading
- **Solution**: Check that CSV files are in `data/raw/`
- **Check**: The app will generate minimal sample data as fallback

### Debug Mode
Add this to your app for debugging:
```python
# Add to EcoMetrics.py for debugging
st.sidebar.markdown("### 🔍 Debug Info")
st.sidebar.write(f"ESG Source: {st.session_state.get('esg_source')}")
st.sidebar.write(f"Finance Source: {st.session_state.get('finance_source')}")
st.sidebar.write(f"Sales Source: {st.session_state.get('sales_source')}")
```

## 📈 Performance Optimization

### For Large Datasets
1. **Use dbt models**: Pre-aggregated data is faster
2. **Enable caching**: Streamlit's `@st.cache_data` is already implemented
3. **Filter early**: Use sidebar filters to reduce data size

### For Production
1. **Set up automated dbt runs**: Use Airflow or similar
2. **Add monitoring**: Log data source usage and performance
3. **Implement authentication**: Add user access controls

## 🎯 Deployment Checklist

### Before Deploying
- [ ] Test locally with sample data
- [ ] Test locally with dbt models (if showcasing)
- [ ] Update README with setup instructions
- [ ] Check all dependencies are in requirements.txt
- [ ] Verify CSV files are included in repository

### After Deploying
- [ ] Check data source indicators in sidebar
- [ ] Test all pages and filters
- [ ] Verify responsive design on mobile
- [ ] Document any issues and solutions

## 🌟 Pro Tips

### For Maximum Impact
1. **Show both modes**: Demonstrate the app works with and without dbt
2. **Explain the architecture**: Highlight the hybrid approach
3. **Document everything**: Clear setup instructions show professionalism
4. **Add screenshots**: Show the data source indicators in action

### For Technical Interviews
- **"I designed this to work in any environment"**
- **"The hybrid approach ensures reliability"**
- **"I prioritized user experience over technical complexity"**
- **"This demonstrates both technical skills and business thinking"**

---

**🚀 Ready to deploy? Your EcoMetrics app will showcase both your dbt expertise and practical deployment skills!** 