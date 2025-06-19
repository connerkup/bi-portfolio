{{
  config(
    materialized='table',
    description='Staged sales data from raw CSV files'
  )
}}

with source as (
    select * from {{ ref('sample_sales_data') }}
),

cleaned as (
    select
        date,
        product_line,
        region,
        customer_segment,
        units_sold,
        revenue,
        cost_of_goods,
        operating_cost,
        profit_margin,
        -- Add calculated fields
        revenue - cost_of_goods as gross_profit,
        round((revenue - cost_of_goods) / nullif(revenue, 0) * 100, 2) as gross_margin_pct,
        round(profit_margin / nullif(revenue, 0) * 100, 2) as net_margin_pct,
        round(cost_of_goods / nullif(units_sold, 0), 2) as cost_per_unit,
        round(revenue / nullif(units_sold, 0), 2) as revenue_per_unit,
        -- Add date parts for analysis
        extract(year from date) as year,
        extract(month from date) as month,
        extract(quarter from date) as quarter
    from source
    where date is not null
      and product_line is not null
      and region is not null
      and customer_segment is not null
)

select * from cleaned 