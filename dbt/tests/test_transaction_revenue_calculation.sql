-- Test that transaction-level revenue calculations are consistent
-- Note: Revenue may include additional factors like taxes, discounts, or fees
-- so we allow for larger differences
with transaction_validation as (
    select
        transaction_id,
        units_sold,
        revenue,
        unit_price,
        (unit_price * units_sold) as calculated_revenue,
        abs(revenue - (unit_price * units_sold)) as difference,
        round((abs(revenue - (unit_price * units_sold)) / revenue) * 100, 2) as difference_pct
    from {{ ref('stg_sales_transactions') }}
),

transaction_errors as (
    select
        transaction_id,
        units_sold,
        revenue,
        unit_price,
        calculated_revenue,
        difference,
        difference_pct
    from transaction_validation
    where difference_pct > 20  -- Allow for up to 20% difference due to taxes, discounts, fees, etc.
)

select *
from transaction_errors 