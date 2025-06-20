-- Test that profit margin equals revenue minus costs
-- This test is for the fact_financial_monthly model
with validation as (
    select
        date,
        product_line,
        region,
        customer_segment,
        total_revenue,
        total_cost_of_goods,
        total_operating_cost,
        total_profit_margin,
        (total_revenue - total_cost_of_goods - total_operating_cost) as calculated_profit,
        abs(total_profit_margin - (total_revenue - total_cost_of_goods - total_operating_cost)) as difference
    from {{ ref('fact_financial_monthly') }}
),

validation_errors as (
    select
        date,
        product_line,
        region,
        customer_segment,
        total_revenue,
        total_cost_of_goods,
        total_operating_cost,
        total_profit_margin,
        calculated_profit,
        difference
    from validation
    where difference > 1  -- Allow for small rounding differences
)

select *
from validation_errors 