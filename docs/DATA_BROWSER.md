# 📋 Data Browser Documentation

## Overview

The Data Browser is a comprehensive data exploration tool integrated into the PackagingCo BI Portfolio dashboard. It provides interactive access to both processed and raw datasets with advanced filtering, search, and export capabilities.

## Features

### 🎯 **Multi-Dataset Support**
- **Processed Data**: ESG, Financial, and Sales data from the database
- **Raw Data**: Original CSV files for comparison and validation
- Easy switching between datasets with intuitive dropdown selection

### 🔍 **Advanced Filtering & Search**
- **Global Search**: Case-insensitive search across all columns
- **Column-Specific Filters**: 
  - Categorical filters for text columns (up to 20 unique values)
  - Range sliders for numeric columns
- **Column Selection**: Choose which columns to display for focused analysis

### 📊 **Data Exploration Tools**
- **Data Overview Tabs**:
  - **Sample Data**: First 10 rows preview
  - **Statistics**: Descriptive statistics for numeric columns
  - **Data Info**: Detailed dataset information (dtypes, memory usage, etc.)
- **Key Metrics**: Total rows, columns, missing data percentage, memory usage

### 📄 **Pagination & Export**
- **Pagination**: Browse large datasets efficiently (10, 25, 50, 100, 500 rows per page)
- **Export**: Download filtered data as CSV files
- **Performance**: Optimized for large datasets with efficient rendering

### 📈 **Data Quality Insights**
- Missing value analysis by column
- Data type information
- Memory usage statistics
- Data quality metrics

## Usage Guide

### 1. **Accessing the Data Browser**
- Navigate to the Streamlit dashboard
- Select "📋 Data Browser" from the sidebar navigation
- Choose your preferred dataset from the dropdown

### 2. **Exploring Data Structure**
- Review the dataset metrics (rows, columns, missing data %)
- Use the "Data Overview" tabs to understand the data:
  - **Sample Data**: See actual data values
  - **Statistics**: Understand numeric distributions
  - **Data Info**: Check data types and memory usage

### 3. **Filtering and Searching**
- **Global Search**: Enter terms to search across all columns
- **Column Selection**: Choose which columns to display
- **Column Filters**: Apply specific filters for each column type
- **Numeric Ranges**: Use sliders for numeric column filtering

### 4. **Browsing Data**
- Navigate through pages using pagination controls
- Adjust rows per page as needed
- View filtered results in the interactive data table

### 5. **Exporting Data**
- Click "Download filtered data as CSV" to export
- Exported file includes only the filtered and selected data
- File naming follows the pattern: `{dataset_name}_filtered.csv`

## Available Datasets

### Processed Data (from Database)
- **🌱 ESG Data (Processed)**: Transformed ESG metrics and sustainability data
- **💰 Financial Data (Processed)**: Aggregated financial metrics and KPIs
- **📈 Sales Data (Processed)**: Processed sales and forecasting data

### Raw Data (from CSV Files)
- **📄 Raw ESG Data**: Original ESG data before transformation
- **📄 Raw Sales Data**: Original sales data before processing

## Best Practices

### 🔍 **Data Validation**
- Compare processed vs. raw data to validate transformations
- Check for missing values and data quality issues
- Verify data types and ranges are as expected

### 📊 **Analysis Workflow**
1. Start with the Overview tabs to understand data structure
2. Use column selection to focus on relevant fields
3. Apply filters to isolate specific data subsets
4. Export filtered data for external analysis if needed

### 🚀 **Performance Tips**
- Use column selection to reduce memory usage
- Apply filters early to reduce dataset size
- Use appropriate pagination settings for large datasets

## Troubleshooting

### Common Issues

**No data displayed**
- Ensure the database is properly set up (`dbt run`)
- Check that CSV files exist in `data/raw/`
- Verify data loading functions are working

**Slow performance**
- Reduce the number of selected columns
- Apply filters to reduce dataset size
- Use smaller pagination settings

**Export not working**
- Ensure you have selected at least one column
- Check browser download settings
- Verify sufficient disk space

### Getting Help
- Check the main [README.md](../README.md) for setup instructions
- Review the [QUICKSTART.md](../QUICKSTART.md) for quick setup
- Ensure all dependencies are properly installed

## Technical Details

### Data Sources
- **Database**: DuckDB with dbt-transformed data
- **CSV Files**: Raw data files in `data/raw/` directory
- **Caching**: Streamlit caching for improved performance

### Performance Optimizations
- Lazy loading of data
- Efficient filtering with pandas operations
- Pagination to handle large datasets
- Memory usage monitoring

### Export Format
- CSV format for maximum compatibility
- UTF-8 encoding
- Includes only filtered and selected data
- Preserves data types and formatting

---

**Note**: The Data Browser is designed to complement the dashboard visualizations by providing detailed data access for validation, exploration, and export purposes. 