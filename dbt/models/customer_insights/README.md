# Customer Insights Models

**Future Module - Coming Soon**

This directory will contain dbt models for customer insights and segmentation analysis.

## Planned Models

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

## Integration with ESG & Finance

These models will integrate with existing ESG and Finance models to provide:
- Customer response to sustainable products
- Revenue impact of ESG initiatives
- Customer-driven sustainability insights
- Market opportunity analysis

## Data Sources

- Customer transaction data
- Customer demographic information
- Survey and feedback data
- Loyalty program data
- Market research data
- CRM systems

## Next Steps

1. **Data Collection**: Gather customer data from CRM and other sources
2. **Model Development**: Create dbt models for customer metrics
3. **Testing**: Implement data quality tests
4. **Documentation**: Document models and metrics
5. **Integration**: Connect with existing ESG and Finance models

---

*This module is part of the vertical slice approach, focusing first on ESG and Finance while planning for future expansion.* 