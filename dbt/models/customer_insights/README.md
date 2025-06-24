# Customer Insights Models

**🔄 In Development - Streamlit App Implemented**

This directory will contain dbt models for customer insights and segmentation analysis. While the dbt models are in development, the customer insights functionality is fully implemented in the Streamlit application.

## Current Status

### ✅ Streamlit Implementation
- **Customer Insights Dashboard**: Fully functional customer analytics page
- **Customer Segmentation**: Behavioral and demographic analysis
- **Sustainability Preferences**: Customer ESG awareness tracking
- **Lifetime Value Analysis**: Customer profitability calculations
- **Market Opportunity Analysis**: Growth potential identification

### 🔄 Planned dbt Models

### Staging Models
- `stg_customer_data.sql` - Customer demographic and transaction data
- `stg_survey_data.sql` - Customer survey and feedback data
- `stg_loyalty_data.sql` - Loyalty program and retention data
- `stg_market_data.sql` - Market research and competitive data

### Intermediate Models
- `int_customer_segments.sql` - Customer segmentation logic
- `int_customer_behavior.sql` - Customer behavior patterns
- `int_sustainability_perception.sql` - Customer ESG perception analysis
- `int_customer_lifetime_value.sql` - CLV calculations

### Mart Models
- `mart_customer_daily.sql` - Daily customer KPIs
- `mart_customer_segments.sql` - Customer segment profiles
- `mart_customer_retention.sql` - Customer retention metrics
- `mart_sustainability_preferences.sql` - Customer ESG preferences

## Current Implementation

The customer insights functionality is currently implemented in the Streamlit application (`ecometrics/pages/4_Customer_Insights.py`) with:

### Key Features
- **Customer Segmentation**: Behavioral clustering and demographic analysis
- **Sustainability Preferences**: Customer ESG awareness and preferences
- **Lifetime Value Analysis**: Customer profitability and retention metrics
- **Market Opportunities**: Growth potential and market analysis
- **Interactive Visualizations**: Real-time charts and filtering
- **Export Capabilities**: Report generation and data export

### Data Sources
- Customer transaction data (from sales models)
- Customer demographic information
- Survey and feedback data
- Loyalty program data
- Market research data
- CRM systems

## Integration with ESG & Finance

The customer insights functionality integrates with existing ESG and Finance models to provide:
- Customer response to sustainable products
- Revenue impact of ESG initiatives
- Customer-driven sustainability insights
- Market opportunity analysis
- Financial impact of customer segments

## Next Steps

1. **Data Collection**: Gather comprehensive customer data from CRM and other sources
2. **Model Development**: Create dbt models for customer metrics
3. **Testing**: Implement data quality tests
4. **Documentation**: Document models and metrics
5. **Integration**: Connect with existing ESG and Finance models

## Usage

### Current Access
Access customer insights through the Streamlit application:
1. Navigate to the Customer Insights page
2. Explore customer segments and behaviors
3. Analyze sustainability preferences
4. Generate customer reports

### Future dbt Integration
Once dbt models are implemented:
```sql
-- Example future queries
SELECT 
    customer_segment,
    avg_lifetime_value,
    sustainability_score,
    retention_rate
FROM {{ ref('mart_customer_segments') }}
ORDER BY avg_lifetime_value DESC
```

---

*This module follows the vertical slice approach, with the Streamlit implementation providing immediate value while dbt models are developed for enhanced data processing and analytics.* 