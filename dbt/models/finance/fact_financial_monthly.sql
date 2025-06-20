{{
  config(
    materialized='table',
    description='Monthly financial metrics fact table built from transaction-level data',
    tests=[
      'test_positive_values',
      'profit_margin_calculation'
    ]
  )
}}

with sales_transactions as (
    select * from {{ ref('stg_sales_transactions') }}
),

monthly_financials as (
    select
        -- Time dimensions
        month_start as date,
        year,
        month,
        quarter,
        
        -- Business dimensions
        product_line,
        region,
        customer_segment,
        customer_tier,
        market_type,
        
        -- Aggregated financial metrics
        sum(units_sold) as total_units_sold,
        sum(revenue) as total_revenue,
        sum(cost_of_goods) as total_cost_of_goods,
        sum(operating_cost) as total_operating_cost,
        sum(calculated_profit_margin) as total_profit_margin,
        
        -- Physical metrics
        sum(weight_kg) as total_weight_kg,
        sum(volume_liters) as total_volume_liters,
        
        -- Average metrics
        avg(unit_price) as avg_unit_price,
        avg(unit_cost) as avg_unit_cost,
        avg(calculated_unit_operating_cost) as avg_unit_operating_cost,
        avg(calculated_profit_margin / nullif(units_sold, 0)) as avg_unit_profit,
        
        -- Profitability ratios
        avg(profit_margin_pct) as avg_profit_margin_pct,
        avg(cost_of_goods_pct) as avg_cost_of_goods_pct,
        avg(operating_cost_pct) as avg_operating_cost_pct,
        
        -- Efficiency metrics
        avg(revenue_per_kg) as avg_revenue_per_kg,
        avg(revenue_per_liter) as avg_revenue_per_liter,
        avg(profit_per_kg) as avg_profit_per_kg,
        avg(profit_per_liter) as avg_profit_per_liter,
        
        -- Business logic aggregations
        count(case when profitability_status = 'Profitable' then 1 end) as profitable_transactions,
        count(case when profitability_status = 'Loss-making' then 1 end) as loss_making_transactions,
        count(case when margin_category = 'High Margin' then 1 end) as high_margin_transactions,
        count(case when margin_category = 'Negative Margin' then 1 end) as negative_margin_transactions,
        count(case when performance_category = 'Star Performer' then 1 end) as star_performer_transactions,
        count(case when strategic_segment = 'Premium High Value' then 1 end) as premium_high_value_transactions,
        
        -- Transaction size and value analysis
        count(case when transaction_size = 'Large' then 1 end) as large_transactions,
        count(case when transaction_size = 'Medium' then 1 end) as medium_transactions,
        count(case when transaction_size = 'Small' then 1 end) as small_transactions,
        count(case when transaction_value_tier = 'High Value' then 1 end) as high_value_transactions,
        count(case when transaction_value_tier = 'Medium Value' then 1 end) as medium_value_transactions,
        count(case when transaction_value_tier = 'Low Value' then 1 end) as low_value_transactions,
        
        -- Time-based analysis
        count(case when day_type = 'Weekend' then 1 end) as weekend_transactions,
        count(case when day_type = 'Weekday' then 1 end) as weekday_transactions,
        
        -- Sustainability analysis
        count(case when sustainability_category = 'Sustainable' then 1 end) as sustainable_product_transactions,
        count(case when sustainability_category = 'Recyclable' then 1 end) as recyclable_product_transactions,
        count(case when sustainability_category = 'Traditional' then 1 end) as traditional_product_transactions,
        
        -- Transaction counts
        count(*) as total_transactions,
        
        -- Calculated derived metrics
        round(total_profit_margin / nullif(total_revenue, 0) * 100, 2) as overall_profit_margin_pct,
        round(total_cost_of_goods / nullif(total_revenue, 0) * 100, 2) as overall_cost_of_goods_pct,
        round(total_operating_cost / nullif(total_revenue, 0) * 100, 2) as overall_operating_cost_pct,
        
        -- Efficiency ratios
        round(total_revenue / nullif(total_weight_kg, 0), 2) as overall_revenue_per_kg,
        round(total_revenue / nullif(total_volume_liters, 0), 2) as overall_revenue_per_liter,
        round(total_profit_margin / nullif(total_weight_kg, 0), 2) as overall_profit_per_kg,
        round(total_profit_margin / nullif(total_volume_liters, 0), 2) as overall_profit_per_liter,
        
        -- Business health indicators
        round(profitable_transactions * 100.0 / nullif(total_transactions, 0), 2) as profitability_rate_pct,
        round(high_margin_transactions * 100.0 / nullif(total_transactions, 0), 2) as high_margin_rate_pct,
        round(star_performer_transactions * 100.0 / nullif(total_transactions, 0), 2) as star_performer_rate_pct,
        round(premium_high_value_transactions * 100.0 / nullif(total_transactions, 0), 2) as premium_high_value_rate_pct,
        
        -- Transaction mix analysis
        round(large_transactions * 100.0 / nullif(total_transactions, 0), 2) as large_transaction_rate_pct,
        round(high_value_transactions * 100.0 / nullif(total_transactions, 0), 2) as high_value_rate_pct,
        round(sustainable_product_transactions * 100.0 / nullif(total_transactions, 0), 2) as sustainable_product_rate_pct,
        
        -- Time distribution analysis
        round(weekend_transactions * 100.0 / nullif(total_transactions, 0), 2) as weekend_rate_pct
        
    from sales_transactions
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9
),

final as (
    select
        *,
        -- Additional business insights
        case 
            when overall_profit_margin_pct >= 20 then 'Excellent Performance'
            when overall_profit_margin_pct >= 10 then 'Good Performance'
            when overall_profit_margin_pct >= 0 then 'Acceptable Performance'
            else 'Poor Performance'
        end as performance_category,
        
        case 
            when profitability_rate_pct >= 80 then 'High Profitability'
            when profitability_rate_pct >= 60 then 'Medium Profitability'
            else 'Low Profitability'
        end as profitability_category,
        
        case 
            when customer_tier = 'Premium' and overall_profit_margin_pct >= 15 then 'Premium Profitable'
            when customer_tier = 'Premium' then 'Premium Underperforming'
            when customer_tier = 'Standard' and overall_profit_margin_pct >= 10 then 'Standard Profitable'
            when customer_tier = 'Standard' then 'Standard Underperforming'
            when customer_tier = 'Value' and overall_profit_margin_pct >= 5 then 'Value Profitable'
            else 'Value Underperforming'
        end as segment_performance,
        
        -- Transaction-level insights
        case 
            when star_performer_rate_pct >= 30 then 'High Star Performer Rate'
            when star_performer_rate_pct >= 15 then 'Medium Star Performer Rate'
            else 'Low Star Performer Rate'
        end as star_performer_category,
        
        case 
            when premium_high_value_rate_pct >= 20 then 'High Premium High Value Rate'
            when premium_high_value_rate_pct >= 10 then 'Medium Premium High Value Rate'
            else 'Low Premium High Value Rate'
        end as premium_high_value_category,
        
        case 
            when sustainable_product_rate_pct >= 40 then 'High Sustainable Product Mix'
            when sustainable_product_rate_pct >= 20 then 'Medium Sustainable Product Mix'
            else 'Low Sustainable Product Mix'
        end as sustainability_mix_category
        
    from monthly_financials
)

select * from final 