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

-- Test that profit margin equals revenue minus costs
{% test profit_margin_calculation(model) %}

with validation as (
    select
        date,
        product_line,
        region,
        customer_segment,
        revenue,
        cost_of_goods,
        operating_cost,
        profit_margin,
        (revenue - cost_of_goods - operating_cost) as calculated_profit,
        abs(profit_margin - (revenue - cost_of_goods - operating_cost)) as difference
    from {{ model }}
),

validation_errors as (
    select
        date,
        product_line,
        region,
        customer_segment,
        revenue,
        cost_of_goods,
        operating_cost,
        profit_margin,
        calculated_profit,
        difference
    from validation
    where difference > 1  -- Allow for small rounding differences
)

select *
from validation_errors

{% endtest %}

-- Test that revenue per unit * units sold equals total revenue
{% test revenue_consistency(model) %}

with validation as (
    select
        date,
        product_line,
        region,
        customer_segment,
        units_sold,
        revenue,
        revenue_per_unit,
        (revenue_per_unit * units_sold) as calculated_revenue,
        abs(revenue - (revenue_per_unit * units_sold)) as difference
    from {{ model }}
),

validation_errors as (
    select
        date,
        product_line,
        region,
        customer_segment,
        units_sold,
        revenue,
        revenue_per_unit,
        calculated_revenue,
        difference
    from validation
    where difference > 1  -- Allow for small rounding differences
)

select *
from validation_errors

{% endtest %} 