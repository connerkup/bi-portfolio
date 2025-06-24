{{ config(materialized='table') }}

with supply_chain_daily as (
    select * from {{ ref('stg_supply_chain_data') }}
),

monthly_aggregations as (
    select
        -- Time dimensions
        date_trunc('month', date) as month_start,
        extract(year from date) as year,
        extract(month from date) as month,
        extract(quarter from date) as quarter,
        
        -- Supplier dimensions
        supplier,
        reliability_category,
        sustainability_category,
        
        -- Aggregated metrics
        count(*) as total_orders,
        sum(order_quantity) as total_quantity,
        sum(order_value) as total_order_value,
        avg(unit_cost) as avg_unit_cost,
        
        -- Delivery performance
        sum(case when on_time_delivery then 1 else 0 end) as on_time_orders,
        count(*) as total_orders_for_delivery,
        avg(delivery_variance_days) as avg_delivery_variance,
        avg(actual_delivery_days) as avg_actual_delivery_days,
        avg(expected_delivery_days) as avg_expected_delivery_days,
        
        -- Quality metrics
        sum(case when quality_issues then 1 else 0 end) as orders_with_quality_issues,
        sum(defect_quantity) as total_defect_quantity,
        avg(defect_rate_pct) as avg_defect_rate,
        
        -- Supplier ratings
        avg(supplier_reliability) as avg_supplier_reliability,
        avg(sustainability_rating) as avg_sustainability_rating,
        
        -- Calculated KPIs
        round(
            sum(case when on_time_delivery then 1 else 0 end) * 100.0 / nullif(count(*), 0), 
            2
        ) as on_time_delivery_rate_pct,
        
        round(
            sum(case when quality_issues then 1 else 0 end) * 100.0 / nullif(count(*), 0), 
            2
        ) as quality_issue_rate_pct,
        
        round(
            sum(order_value) / nullif(sum(order_quantity), 0), 
            2
        ) as effective_unit_cost
        
    from supply_chain_daily
    group by 
        date_trunc('month', date),
        extract(year from date),
        extract(month from date),
        extract(quarter from date),
        supplier,
        reliability_category,
        sustainability_category
),

final as (
    select
        month_start as date,
        year,
        month,
        quarter,
        supplier,
        reliability_category,
        sustainability_category,
        total_orders,
        total_quantity,
        total_order_value,
        avg_unit_cost,
        effective_unit_cost,
        on_time_orders,
        total_orders_for_delivery,
        on_time_delivery_rate_pct,
        avg_delivery_variance,
        avg_actual_delivery_days,
        avg_expected_delivery_days,
        orders_with_quality_issues,
        quality_issue_rate_pct,
        total_defect_quantity,
        avg_defect_rate,
        avg_supplier_reliability,
        avg_sustainability_rating,
        
        -- Additional calculated fields for analysis
        case 
            when on_time_delivery_rate_pct >= 95 then 'Excellent'
            when on_time_delivery_rate_pct >= 85 then 'Good'
            when on_time_delivery_rate_pct >= 70 then 'Fair'
            else 'Poor'
        end as delivery_performance_category,
        
        case 
            when quality_issue_rate_pct <= 2 then 'Excellent'
            when quality_issue_rate_pct <= 5 then 'Good'
            when quality_issue_rate_pct <= 10 then 'Fair'
            else 'Poor'
        end as quality_performance_category,
        
        case 
            when avg_supplier_reliability >= 0.95 then 'High'
            when avg_supplier_reliability >= 0.90 then 'Medium'
            else 'Low'
        end as reliability_level,
        
        case 
            when avg_sustainability_rating >= 4.5 then 'Excellent'
            when avg_sustainability_rating >= 4.0 then 'Good'
            when avg_sustainability_rating >= 3.0 then 'Fair'
            else 'Poor'
        end as sustainability_level
        
    from monthly_aggregations
)

select * from final
order by date desc, supplier 