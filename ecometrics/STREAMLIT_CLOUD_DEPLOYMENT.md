# Streamlit Cloud Deployment Guide

This guide explains how to deploy the EcoMetrics app to Streamlit Cloud while ensuring it can access your dbt pipeline data.

## Prerequisites

1. **dbt Pipeline Built**: Your dbt models must be built and the database file generated
2. **GitHub Repository**: Your code must be in a GitHub repository
3. **Streamlit Cloud Account**: Access to Streamlit Cloud (free tier available)

## Step 1: Prepare Your Repository

### 1.1 Build the dbt Pipeline

Before deploying, ensure your dbt pipeline is built:

```bash
# Navigate to dbt directory
cd dbt

# Install dependencies
dbt deps

# Run the models
dbt run

# Verify the database was created
ls -la data/processed/portfolio.duckdb
```

### 1.2 Include the Database File

**Important**: For Streamlit Cloud to access your dbt data, you must include the database file in your repository.

```bash
# From the project root, copy the database to the ecometrics directory
cp data/processed/portfolio.duckdb ecometrics/portfolio.duckdb

# Add to git
git add ecometrics/portfolio.duckdb
git commit -m "Add dbt database for Streamlit Cloud deployment"
git push
```

### 1.3 Update .gitignore (if needed)

Ensure your `.gitignore` doesn't exclude the database file in the ecometrics directory:

```gitignore
# Don't ignore the database file in ecometrics directory
!ecometrics/portfolio.duckdb

# But still ignore it in other locations
data/processed/*.duckdb
```

### 1.4 Using the Deployment Script (Recommended)

As an alternative to the manual steps above, you can use the `prepare_for_deployment.py` script to automate the process of building the dbt pipeline and preparing the database for deployment.

**What it does:**
- Checks for dbt installation.
- Runs `dbt deps`, `dbt run`, and `dbt test`.
- Copies the `portfolio.duckdb` database to the `ecometrics` directory.
- Verifies the contents of the copied database.
- Creates a `DEPLOYMENT_INFO.md` file with details about the build.

**How to run it:**

1.  Navigate to the `ecometrics` directory:
    ```bash
    cd ecometrics
    ```
2.  Run the script:
    ```bash
    python prepare_for_deployment.py
    ```
3.  After the script finishes, commit the changes to your repository:
    ```bash
    git add portfolio.duckdb DEPLOYMENT_INFO.md
    git commit -m "Update dbt database and deployment info"
    git push
    ```

## Step 2: Deploy to Streamlit Cloud

### 2.1 Connect Your Repository

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set the main file path to: `ecometrics/Home.py`
6. Set the app URL (optional)

### 2.2 Configure App Settings

In the Streamlit Cloud dashboard:

- **Python version**: 3.9 or higher
- **Requirements file**: `ecometrics/requirements.txt`
- **Main file**: `ecometrics/Home.py`

## Step 3: Verify Deployment

### 3.1 Check Data Connection

Once deployed, visit your app and navigate to the "Data Browser" page. You should see:

- ✅ Database connection status
- Available tables from your dbt models
- Data quality metrics

### 3.2 Troubleshooting

If the database connection fails:

1. **Check file path**: Ensure `portfolio.duckdb` is in the `ecometrics/` directory
2. **Check file size**: The database file should be included in the deployment
3. **Check logs**: View deployment logs in Streamlit Cloud dashboard

## Step 4: Automated Deployment (Optional)

### 4.1 GitHub Actions Workflow

Create `.github/workflows/deploy-dbt.yml`:

```yaml
name: Build dbt and Deploy

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-dbt:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dbt
      run: |
        pip install dbt-core dbt-duckdb
    
    - name: Build dbt models
      run: |
        cd dbt
        dbt deps
        dbt run
    
    - name: Copy database to ecometrics
      run: |
        cp data/processed/portfolio.duckdb ecometrics/portfolio.duckdb
    
    - name: Commit and push changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add ecometrics/portfolio.duckdb
        git commit -m "Update dbt database for deployment" || exit 0
        git push
```

## Alternative Approaches

### Option 1: External Database

For production deployments, consider using an external database:

1. **PostgreSQL**: Update `dbt/profiles.yml` to use PostgreSQL
2. **BigQuery**: Use BigQuery for larger datasets
3. **Snowflake**: Enterprise-grade data warehouse

### Option 2: Data Refresh Schedule

Set up automated data refresh:

1. **GitHub Actions**: Daily/weekly dbt runs
2. **Streamlit Cloud**: Configure to redeploy on repository updates
3. **External Scheduler**: Use Airflow or similar

## Environment Variables

For production deployments, you can set environment variables in Streamlit Cloud:

- `DBT_PROFILE`: Database connection profile
- `DBT_TARGET`: Target environment (dev/prod)
- `DATABASE_URL`: Direct database connection string

## Monitoring and Maintenance

### Regular Tasks

1. **Monitor data freshness**: Check when dbt models were last updated
2. **Verify data quality**: Use the Data Browser page to check metrics
3. **Update dependencies**: Keep requirements.txt updated
4. **Backup database**: Regular backups of the dbt database

### Performance Optimization

1. **Database optimization**: Regular VACUUM and ANALYZE
2. **Caching**: Use Streamlit's caching for expensive queries
3. **Query optimization**: Monitor slow queries in the Data Browser

## Support

If you encounter issues:

1. Check the Streamlit Cloud logs
2. Verify the database file is included in the repository
3. Test locally with the same file structure
4. Review the Data Browser page for connection status

## Best Practices

1. **Version control**: Always commit the database file after dbt runs
2. **Documentation**: Keep this guide updated with any changes
3. **Testing**: Test locally before deploying
4. **Monitoring**: Set up alerts for data pipeline failures
5. **Backup**: Regular backups of both code and data 