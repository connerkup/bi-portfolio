"""
Airflow DAG for PackagingCo BI Portfolio

This DAG orchestrates the data pipeline for the ESG & Finance Insights BI Portfolio.
It demonstrates how to schedule and automate the data transformation and analysis processes.

Note: This is a conceptual DAG for demonstration purposes. In a real production environment,
you would need to configure Airflow with the appropriate connections and variables.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago

# Default arguments for the DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['data-team@packagingco.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'packagingco_bi_portfolio',
    default_args=default_args,
    description='ESG & Finance Insights BI Portfolio Pipeline',
    schedule_interval='0 2 * * *',  # Run daily at 2 AM
    catchup=False,
    tags=['bi', 'esg', 'finance', 'packagingco'],
)

def load_raw_data(**context):
    """
    Load raw data from various sources.
    
    This function would typically:
    - Extract data from source systems
    - Load into staging area
    - Validate data quality
    """
    import pandas as pd
    import os
    from datetime import datetime
    
    # This is a placeholder for the actual data loading logic
    # In production, this would connect to actual data sources
    
    print(f"Loading raw data at {datetime.now()}")
    
    # Example: Load sample data if it doesn't exist
    data_dir = "../data/raw"
    if not os.path.exists(f"{data_dir}/sample_sales_data.csv"):
        print("Sample data not found - this is expected in development")
    
    # In production, this would be actual data extraction
    # Example:
    # - Extract from ERP system
    # - Extract from sustainability tracking system
    # - Extract from financial systems
    # - Load to staging area
    
    return "Data loaded successfully"

def run_dbt_transformations(**context):
    """
    Run dbt transformations to create the data models.
    
    This function:
    - Runs dbt models
    - Executes tests
    - Generates documentation
    """
    import subprocess
    import os
    
    # Change to dbt directory
    dbt_dir = "../dbt"
    
    try:
        # Run dbt seed to load seed data
        subprocess.run(["dbt", "seed"], cwd=dbt_dir, check=True)
        print("✅ dbt seed completed successfully")
        
        # Run dbt models
        subprocess.run(["dbt", "run"], cwd=dbt_dir, check=True)
        print("✅ dbt run completed successfully")
        
        # Run dbt tests
        subprocess.run(["dbt", "test"], cwd=dbt_dir, check=True)
        print("✅ dbt test completed successfully")
        
        # Generate documentation
        subprocess.run(["dbt", "docs", "generate"], cwd=dbt_dir, check=True)
        print("✅ dbt docs generated successfully")
        
        return "dbt transformations completed successfully"
        
    except subprocess.CalledProcessError as e:
        print(f"❌ dbt transformation failed: {e}")
        raise

def generate_insights(**context):
    """
    Generate business insights and analytics.
    
    This function would:
    - Run analysis scripts
    - Generate reports
    - Calculate KPIs
    """
    import sys
    import os
    
    # Add src directory to path
    sys.path.append("../src")
    
    try:
        from packagingco_insights.utils import load_esg_data, load_finance_data
        from packagingco_insights.analysis import ESGAnalyzer, FinanceAnalyzer
        
        # Load data
        esg_data = load_esg_data()
        finance_data = load_finance_data()
        
        # Generate insights
        esg_analyzer = ESGAnalyzer(esg_data)
        finance_analyzer = FinanceAnalyzer(finance_data)
        
        # Get insights
        esg_insights = esg_analyzer.get_esg_insights()
        financial_insights = finance_analyzer.get_financial_insights()
        
        print("✅ Insights generated successfully")
        print(f"ESG Insights: {len(esg_insights)} metrics calculated")
        print(f"Financial Insights: {len(financial_insights)} metrics calculated")
        
        return "Insights generated successfully"
        
    except Exception as e:
        print(f"❌ Insight generation failed: {e}")
        raise

def validate_data_quality(**context):
    """
    Validate data quality and integrity.
    
    This function would:
    - Run data quality checks
    - Validate business rules
    - Check for anomalies
    """
    import sys
    import os
    
    # Add src directory to path
    sys.path.append("../src")
    
    try:
        from packagingco_insights.utils import load_esg_data, load_finance_data, check_data_quality
        
        # Load data
        esg_data = load_esg_data()
        finance_data = load_finance_data()
        
        # Check data quality
        esg_quality = check_data_quality(esg_data)
        finance_quality = check_data_quality(finance_data)
        
        print("✅ Data quality validation completed")
        print(f"ESG Data: {esg_quality['total_rows']} rows, {esg_quality['total_columns']} columns")
        print(f"Finance Data: {finance_quality['total_rows']} rows, {finance_quality['total_columns']} columns")
        
        # Check for data quality issues
        esg_missing = sum(esg_quality['missing_values'].values())
        finance_missing = sum(finance_quality['missing_values'].values())
        
        if esg_missing > 0 or finance_missing > 0:
            print(f"⚠️ Warning: {esg_missing + finance_missing} missing values found")
        
        return "Data quality validation completed"
        
    except Exception as e:
        print(f"❌ Data quality validation failed: {e}")
        raise

def send_daily_report(**context):
    """
    Send daily report to stakeholders.
    
    This function would:
    - Generate daily summary
    - Send email report
    - Update dashboard
    """
    from datetime import datetime
    
    # This is a placeholder for the actual reporting logic
    # In production, this would generate and send actual reports
    
    report_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📊 Daily report for {report_date} generated")
    print("📧 Report sent to stakeholders")
    
    return "Daily report sent successfully"

# Define tasks
load_data_task = PythonOperator(
    task_id='load_raw_data',
    python_callable=load_raw_data,
    dag=dag,
)

run_dbt_task = PythonOperator(
    task_id='run_dbt_transformations',
    python_callable=run_dbt_transformations,
    dag=dag,
)

validate_quality_task = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data_quality,
    dag=dag,
)

generate_insights_task = PythonOperator(
    task_id='generate_insights',
    python_callable=generate_insights,
    dag=dag,
)

send_report_task = PythonOperator(
    task_id='send_daily_report',
    python_callable=send_daily_report,
    dag=dag,
)

# Alternative: Use BashOperator for dbt commands
run_dbt_bash_task = BashOperator(
    task_id='run_dbt_bash',
    bash_command="""
    cd ../dbt && \
    dbt seed && \
    dbt run && \
    dbt test && \
    dbt docs generate
    """,
    dag=dag,
)

# Email notification task
email_notification_task = EmailOperator(
    task_id='send_completion_email',
    to=['data-team@packagingco.com'],
    subject='BI Portfolio Pipeline Completed - {{ ds }}',
    html_content="""
    <h3>PackagingCo BI Portfolio Pipeline Report</h3>
    <p><strong>Date:</strong> {{ ds }}</p>
    <p><strong>Status:</strong> ✅ Completed Successfully</p>
    
    <h4>Pipeline Summary:</h4>
    <ul>
        <li>✅ Raw data loaded</li>
        <li>✅ dbt transformations completed</li>
        <li>✅ Data quality validated</li>
        <li>✅ Insights generated</li>
        <li>✅ Daily report sent</li>
    </ul>
    
    <p><strong>Next Steps:</strong></p>
    <ul>
        <li>Review dashboard for latest insights</li>
        <li>Check ESG and Finance metrics</li>
        <li>Validate business recommendations</li>
    </ul>
    
    <p>Dashboard: <a href="http://localhost:8501">http://localhost:8501</a></p>
    """,
    dag=dag,
)

# Define task dependencies
load_data_task >> run_dbt_task >> validate_quality_task >> generate_insights_task >> send_report_task >> email_notification_task

# Alternative dependency chain using bash operator
# load_data_task >> run_dbt_bash_task >> validate_quality_task >> generate_insights_task >> send_report_task >> email_notification_task

# Documentation
dag.doc_md = __doc__

# Task documentation
load_data_task.doc_md = """
Load raw data from various sources including:
- ERP system data
- Sustainability tracking data
- Financial system data
- External data sources
"""

run_dbt_task.doc_md = """
Execute dbt transformations to:
- Load seed data
- Run staging models
- Run intermediate models
- Run mart models
- Execute tests
- Generate documentation
"""

validate_quality_task.doc_md = """
Validate data quality by:
- Checking for missing values
- Validating data types
- Checking for duplicates
- Running business rule validations
- Identifying anomalies
"""

generate_insights_task.doc_md = """
Generate business insights including:
- ESG performance metrics
- Financial performance analysis
- Trend analysis
- Forecasting
- Key recommendations
"""

send_report_task.doc_md = """
Send daily report to stakeholders with:
- Executive summary
- Key metrics
- Trend analysis
- Recommendations
- Action items
""" 