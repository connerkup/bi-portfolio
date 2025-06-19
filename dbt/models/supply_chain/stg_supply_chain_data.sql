{{ config(materialized='view') }}

with source as (
    select * from {{ ref('supply_chain_data') }}
),

staged as (
    select
        -- Primary keys and identifiers
        date,
        supplier,
        order_id,
        
        -- Order metrics
        order_quantity,
        order_value,
        
        -- Delivery performance
        expected_delivery,
        actual_delivery,
        on_time_delivery,
        
        -- Quality metrics
        quality_issues,
        defect_quantity,
        
        -- Supplier ratings
        supplier_reliability,
        sustainability_rating,
        
        -- Calculated metrics
        round(order_value / nullif(order_quantity, 0), 2) as unit_cost,
        round(defect_quantity / nullif(order_quantity, 0) * 100, 2) as defect_rate_pct,
        
        -- Delivery performance metrics
        date_diff('day', date, actual_delivery) as actual_delivery_days,
        date_diff('day', date, expected_delivery) as expected_delivery_days,
        date_diff('day', expected_delivery, actual_delivery) as delivery_variance_days,
        
        -- Date dimensions
        extract(year from date) as year,
        extract(month from date) as month,
        extract(quarter from date) as quarter,
        date_trunc('month', date) as month_start,
        date_trunc('quarter', date) as quarter_start,
        date_trunc('year', date) as year_start,
        
        -- Business logic flags
        case 
            when on_time_delivery then 'On Time'
            when delivery_variance_days <= 2 then 'Slightly Late'
            when delivery_variance_days <= 5 then 'Late'
            else 'Very Late'
        end as delivery_performance,
        
        case 
            when supplier_reliability >= 0.95 then 'High Reliability'
            when supplier_reliability >= 0.90 then 'Medium Reliability'
            else 'Low Reliability'
        end as reliability_category,
        
        case 
            when sustainability_rating >= 4 then 'High Sustainability'
            when sustainability_rating >= 3 then 'Medium Sustainability'
            else 'Low Sustainability'
        end as sustainability_category,
        
        case 
            when quality_issues then 'Quality Issues'
            else 'No Quality Issues'
        end as quality_status,
        
        case 
            when defect_rate_pct >= 5 then 'High Defect Rate'
            when defect_rate_pct >= 2 then 'Medium Defect Rate'
            when defect_rate_pct > 0 then 'Low Defect Rate'
            else 'No Defects'
        end as defect_category
        
    from source
)

select * from staged 