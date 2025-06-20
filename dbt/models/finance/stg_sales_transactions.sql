{{
  config(
    materialized='view',
    description='Staged transaction-level sales data with enhanced business logic',
    tests=[
      'test_positive_values',
      'revenue_consistency',
      'timestamp_reasonableness'
    ]
  )
}}

with source as (
    select * from {{ source('raw_data', 'sales_transactions') }}
),

staged as (
    select
        -- Primary keys and identifiers
        transaction_id,
        date,
        customer_id,
        order_id,
        sku,
        
        -- Business dimensions
        product_line,
        region,
        customer_segment,
        supplier,
        
        -- Transaction metrics
        units_sold,
        unit_price,
        revenue,
        unit_cost,
        cost_of_goods,
        operating_cost,
        profit_margin,
        
        -- Additional fields
        delivery_date,
        payment_terms,
        payment_status,
        currency,
        weight_kg,
        volume_liters,
        
        -- Enhanced calculated metrics
        round(revenue / nullif(units_sold, 0), 4) as calculated_unit_price,
        round(cost_of_goods / nullif(units_sold, 0), 4) as calculated_unit_cost,
        round(operating_cost / nullif(units_sold, 0), 4) as calculated_unit_operating_cost,
        round((revenue - cost_of_goods - operating_cost), 2) as calculated_profit_margin,
        
        -- Profitability ratios
        round((revenue - cost_of_goods - operating_cost) / nullif(revenue, 0) * 100, 2) as profit_margin_pct,
        round(cost_of_goods / nullif(revenue, 0) * 100, 2) as cost_of_goods_pct,
        round(operating_cost / nullif(revenue, 0) * 100, 2) as operating_cost_pct,
        
        -- Efficiency metrics
        round(revenue / nullif(weight_kg, 0), 2) as revenue_per_kg,
        round(revenue / nullif(volume_liters, 0), 2) as revenue_per_liter,
        round((revenue - cost_of_goods - operating_cost) / nullif(weight_kg, 0), 2) as profit_per_kg,
        round((revenue - cost_of_goods - operating_cost) / nullif(volume_liters, 0), 2) as profit_per_liter,
        
        -- Date dimensions
        extract(year from date) as year,
        extract(month from date) as month,
        extract(quarter from date) as quarter,
        extract(dow from date) as day_of_week,
        date_trunc('month', date) as month_start,
        date_trunc('quarter', date) as quarter_start,
        date_trunc('year', date) as year_start,
        date_trunc('week', date) as week_start,
        date_trunc('day', date) as day_start,
        
        -- Time-based business logic
        case 
            when extract(dow from date) in (0, 6) then 'Weekend'
            else 'Weekday'
        end as day_type,
        
        -- Business logic flags
        case 
            when (revenue - cost_of_goods - operating_cost) > 0 then 'Profitable'
            when (revenue - cost_of_goods - operating_cost) = 0 then 'Break-even'
            else 'Loss-making'
        end as profitability_status,
        
        case 
            when (revenue - cost_of_goods - operating_cost) / nullif(revenue, 0) * 100 >= 20 then 'High Margin'
            when (revenue - cost_of_goods - operating_cost) / nullif(revenue, 0) * 100 >= 10 then 'Medium Margin'
            when (revenue - cost_of_goods - operating_cost) / nullif(revenue, 0) * 100 >= 0 then 'Low Margin'
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
        end as market_type,
        
        case 
            when units_sold >= 1000 then 'Large'
            when units_sold >= 100 then 'Medium'
            else 'Small'
        end as transaction_size,
        
        case 
            when revenue >= 10000 then 'High Value'
            when revenue >= 1000 then 'Medium Value'
            else 'Low Value'
        end as transaction_value_tier,
        
        -- Product characteristics
        case 
            when product_line in ('Biodegradable Packaging', 'Paper Packaging') then 'Sustainable'
            when product_line in ('Glass Bottles', 'Aluminum Cans') then 'Recyclable'
            else 'Traditional'
        end as sustainability_category,
        
        -- Data quality flags
        case 
            when abs(unit_price - (revenue / nullif(units_sold, 0))) > 0.01 then 'Price Mismatch'
            when abs(unit_cost - (cost_of_goods / nullif(units_sold, 0))) > 0.01 then 'Cost Mismatch'
            when revenue <= 0 or cost_of_goods <= 0 or units_sold <= 0 then 'Invalid Values'
            else 'Valid'
        end as data_quality_flag
        
    from source
),

final as (
    select 
        *,
        -- Additional derived insights
        case 
            when profitability_status = 'Profitable' and margin_category = 'High Margin' then 'Star Performer'
            when profitability_status = 'Profitable' and margin_category in ('Medium Margin', 'Low Margin') then 'Solid Performer'
            when profitability_status = 'Break-even' then 'Marginal Performer'
            else 'Poor Performer'
        end as performance_category,
        
        case 
            when customer_tier = 'Premium' and transaction_value_tier = 'High Value' then 'Premium High Value'
            when customer_tier = 'Premium' then 'Premium Standard'
            when transaction_value_tier = 'High Value' then 'High Value'
            else 'Standard'
        end as strategic_segment
        
    from staged
)

select * from final
where data_quality_flag = 'Valid'  -- Filter out data quality issues 