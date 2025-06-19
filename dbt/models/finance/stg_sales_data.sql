{{
  config(
    materialized='view',
    description='Staged sales data from raw CSV files'
  )
}}

with source as (
    select * from {{ ref('sample_sales_data') }}
),

staged as (
    select
        -- Primary keys and identifiers
        date,
        product_line,
        region,
        customer_segment,
        
        -- Sales metrics
        units_sold,
        revenue,
        cost_of_goods,
        operating_cost,
        profit_margin,
        
        -- Physical metrics
        weight_kg,
        volume_liters,
        
        -- Calculated metrics
        round(revenue / nullif(units_sold, 0), 2) as unit_price,
        round(cost_of_goods / nullif(units_sold, 0), 2) as unit_cost,
        round(operating_cost / nullif(units_sold, 0), 2) as unit_operating_cost,
        round(profit_margin / nullif(units_sold, 0), 2) as unit_profit,
        
        -- Profitability ratios
        round(profit_margin / nullif(revenue, 0) * 100, 2) as profit_margin_pct,
        round(cost_of_goods / nullif(revenue, 0) * 100, 2) as cost_of_goods_pct,
        round(operating_cost / nullif(revenue, 0) * 100, 2) as operating_cost_pct,
        
        -- Efficiency metrics
        round(revenue / nullif(weight_kg, 0), 2) as revenue_per_kg,
        round(revenue / nullif(volume_liters, 0), 2) as revenue_per_liter,
        round(profit_margin / nullif(weight_kg, 0), 2) as profit_per_kg,
        round(profit_margin / nullif(volume_liters, 0), 2) as profit_per_liter,
        
        -- Date dimensions
        extract(year from date) as year,
        extract(month from date) as month,
        extract(quarter from date) as quarter,
        date_trunc('month', date) as month_start,
        date_trunc('quarter', date) as quarter_start,
        date_trunc('year', date) as year_start,
        
        -- Business logic flags
        case 
            when profit_margin > 0 then 'Profitable'
            when profit_margin = 0 then 'Break-even'
            else 'Loss-making'
        end as profitability_status,
        
        case 
            when profit_margin_pct >= 20 then 'High Margin'
            when profit_margin_pct >= 10 then 'Medium Margin'
            when profit_margin_pct >= 0 then 'Low Margin'
            else 'Negative Margin'
        end as margin_category,
        
        case 
            when customer_segment in ('Pharmaceutical', 'Food & Beverage') then 'Premium'
            when customer_segment in ('Wholesale', 'Retail') then 'Standard'
            else 'Value'
        end as customer_tier,
        
        case 
            when region in ('Europe', 'North America') then 'Developed'
            else 'Emerging'
        end as market_type
        
    from source
)

select * from staged 