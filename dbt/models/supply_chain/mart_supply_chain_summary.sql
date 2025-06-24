{{ config(materialized='table') }}

with supply_chain_daily as (
    select * from {{ ref('stg_supply_chain_data') }}
),

supplier_summary as (
    select
        supplier,
        count(*) as total_orders,
        sum(order_value) as total_order_value,
        sum(order_quantity) as total_quantity,
        avg(unit_cost) as avg_unit_cost,
        
        -- Delivery performance
        sum(case when on_time_delivery then 1 else 0 end) as on_time_orders,
        round(
            sum(case when on_time_delivery then 1 else 0 end) * 100.0 / nullif(count(*), 0), 
            2
        ) as on_time_delivery_rate_pct,
        avg(delivery_variance_days) as avg_delivery_variance,
        
        -- Quality metrics
        sum(case when quality_issues then 1 else 0 end) as orders_with_quality_issues,
        sum(defect_quantity) as total_defect_quantity,
        avg(defect_rate_pct) as avg_defect_rate,
        
        -- Supplier ratings
        avg(supplier_reliability) as avg_supplier_reliability,
        avg(sustainability_rating) as avg_sustainability_rating,
        
        -- Performance categories
        case 
            when avg(supplier_reliability) >= 0.95 then 'High Reliability'
            when avg(supplier_reliability) >= 0.90 then 'Medium Reliability'
            else 'Low Reliability'
        end as reliability_category,
        
        case 
            when avg(sustainability_rating) >= 4 then 'High Sustainability'
            when avg(sustainability_rating) >= 3 then 'Medium Sustainability'
            else 'Low Sustainability'
        end as sustainability_category,
        
        case 
            when sum(case when on_time_delivery then 1 else 0 end) * 100.0 / nullif(count(*), 0) >= 95 then 'Excellent'
            when sum(case when on_time_delivery then 1 else 0 end) * 100.0 / nullif(count(*), 0) >= 85 then 'Good'
            when sum(case when on_time_delivery then 1 else 0 end) * 100.0 / nullif(count(*), 0) >= 70 then 'Fair'
            else 'Poor'
        end as delivery_performance_category,
        
        case 
            when avg(defect_rate_pct) <= 2 then 'Excellent'
            when avg(defect_rate_pct) <= 5 then 'Good'
            when avg(defect_rate_pct) <= 10 then 'Fair'
            else 'Poor'
        end as quality_performance_category
        
    from supply_chain_daily
    group by supplier
),

monthly_trends as (
    select
        date_trunc('month', date) as month_start,
        count(*) as total_orders,
        sum(order_value) as total_order_value,
        sum(order_quantity) as total_quantity,
        avg(unit_cost) as avg_unit_cost,
        
        -- Delivery performance
        sum(case when on_time_delivery then 1 else 0 end) as on_time_orders,
        round(
            sum(case when on_time_delivery then 1 else 0 end) * 100.0 / nullif(count(*), 0), 
            2
        ) as on_time_delivery_rate_pct,
        
        -- Quality metrics
        sum(case when quality_issues then 1 else 0 end) as orders_with_quality_issues,
        avg(defect_rate_pct) as avg_defect_rate,
        
        -- Supplier ratings
        avg(supplier_reliability) as avg_supplier_reliability,
        avg(sustainability_rating) as avg_sustainability_rating
        
    from supply_chain_daily
    group by date_trunc('month', date)
),

delivery_performance_breakdown as (
    select
        delivery_performance,
        count(*) as order_count,
        sum(order_value) as total_order_value,
        avg(delivery_variance_days) as avg_variance_days,
        round(
            count(*) * 100.0 / sum(count(*)) over (), 
            2
        ) as percentage_of_orders
        
    from supply_chain_daily
    group by delivery_performance
),

quality_breakdown as (
    select
        quality_status,
        count(*) as order_count,
        sum(order_value) as total_order_value,
        sum(defect_quantity) as total_defect_quantity,
        avg(defect_rate_pct) as avg_defect_rate,
        round(
            count(*) * 100.0 / sum(count(*)) over (), 
            2
        ) as percentage_of_orders
        
    from supply_chain_daily
    group by quality_status
),

sustainability_breakdown as (
    select
        sustainability_category,
        count(*) as order_count,
        sum(order_value) as total_order_value,
        avg(sustainability_rating) as avg_sustainability_rating,
        avg(supplier_reliability) as avg_supplier_reliability,
        round(
            count(*) * 100.0 / sum(count(*)) over (), 
            2
        ) as percentage_of_orders
        
    from supply_chain_daily
    group by sustainability_category
),

final as (
    select
        'supplier_summary' as summary_type,
        supplier as dimension_value,
        total_orders,
        total_order_value,
        total_quantity,
        avg_unit_cost,
        on_time_orders,
        on_time_delivery_rate_pct,
        avg_delivery_variance,
        orders_with_quality_issues,
        total_defect_quantity,
        avg_defect_rate,
        avg_supplier_reliability,
        avg_sustainability_rating,
        reliability_category,
        sustainability_category,
        delivery_performance_category,
        quality_performance_category,
        null as percentage_of_orders
        
    from supplier_summary
    
    union all
    
    select
        'monthly_trends' as summary_type,
        cast(month_start as varchar) as dimension_value,
        total_orders,
        total_order_value,
        total_quantity,
        avg_unit_cost,
        on_time_orders,
        on_time_delivery_rate_pct,
        null as avg_delivery_variance,
        orders_with_quality_issues,
        null as total_defect_quantity,
        avg_defect_rate,
        avg_supplier_reliability,
        avg_sustainability_rating,
        null as reliability_category,
        null as sustainability_category,
        null as delivery_performance_category,
        null as quality_performance_category,
        null as percentage_of_orders
        
    from monthly_trends
    
    union all
    
    select
        'delivery_performance' as summary_type,
        delivery_performance as dimension_value,
        order_count as total_orders,
        total_order_value,
        null as total_quantity,
        null as avg_unit_cost,
        null as on_time_orders,
        null as on_time_delivery_rate_pct,
        avg_variance_days as avg_delivery_variance,
        null as orders_with_quality_issues,
        null as total_defect_quantity,
        null as avg_defect_rate,
        null as avg_supplier_reliability,
        null as avg_sustainability_rating,
        null as reliability_category,
        null as sustainability_category,
        null as delivery_performance_category,
        null as quality_performance_category,
        percentage_of_orders
        
    from delivery_performance_breakdown
    
    union all
    
    select
        'quality_breakdown' as summary_type,
        quality_status as dimension_value,
        order_count as total_orders,
        total_order_value,
        null as total_quantity,
        null as avg_unit_cost,
        null as on_time_orders,
        null as on_time_delivery_rate_pct,
        null as avg_delivery_variance,
        null as orders_with_quality_issues,
        total_defect_quantity,
        avg_defect_rate,
        null as avg_supplier_reliability,
        null as avg_sustainability_rating,
        null as reliability_category,
        null as sustainability_category,
        null as delivery_performance_category,
        null as quality_performance_category,
        percentage_of_orders
        
    from quality_breakdown
    
    union all
    
    select
        'sustainability_breakdown' as summary_type,
        sustainability_category as dimension_value,
        order_count as total_orders,
        total_order_value,
        null as total_quantity,
        null as avg_unit_cost,
        null as on_time_orders,
        null as on_time_delivery_rate_pct,
        null as avg_delivery_variance,
        null as orders_with_quality_issues,
        null as total_defect_quantity,
        null as avg_defect_rate,
        avg_supplier_reliability,
        avg_sustainability_rating,
        null as reliability_category,
        null as sustainability_category,
        null as delivery_performance_category,
        null as quality_performance_category,
        percentage_of_orders
        
    from sustainability_breakdown
)

select * from final
order by summary_type, dimension_value 