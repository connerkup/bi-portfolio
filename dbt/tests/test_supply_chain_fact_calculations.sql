-- Test supply chain fact table calculations and aggregations
-- All SELECTs must have the same columns in the same order and types for UNION ALL
-- Columns: test_name, date, supplier, detail1, detail2, detail3, detail4, detail5

with 
daily_totals as (
    select 
        date_trunc('month', date) as month_start,
        supplier,
        sum(order_value) as daily_total_value,
        sum(order_quantity) as daily_total_quantity,
        count(*) as daily_order_count
    from {{ ref('stg_supply_chain_data') }}
    group by date_trunc('month', date), supplier
),
fact_totals as (
    select 
        date,
        supplier,
        total_order_value,
        total_quantity,
        total_orders
    from {{ ref('fact_supply_chain_monthly') }}
),
daily_delivery as (
    select 
        date_trunc('month', date) as month_start,
        supplier,
        sum(case when on_time_delivery then 1 else 0 end) as on_time_count,
        count(*) as total_count
    from {{ ref('stg_supply_chain_data') }}
    group by date_trunc('month', date), supplier
),
fact_delivery as (
    select 
        date,
        supplier,
        on_time_orders,
        total_orders_for_delivery,
        on_time_delivery_rate_pct
    from {{ ref('fact_supply_chain_monthly') }}
),
daily_quality as (
    select 
        date_trunc('month', date) as month_start,
        supplier,
        sum(case when quality_issues then 1 else 0 end) as quality_issue_count,
        count(*) as total_count
    from {{ ref('stg_supply_chain_data') }}
    group by date_trunc('month', date), supplier
),
fact_quality as (
    select 
        date,
        supplier,
        orders_with_quality_issues,
        total_orders,
        quality_issue_rate_pct
    from {{ ref('fact_supply_chain_monthly') }}
)
select 'monthly_aggregations' as test_name, cast(d.month_start as varchar) as date, d.supplier, 
    cast(d.daily_total_value as varchar) as detail1, cast(f.total_order_value as varchar) as detail2, cast(abs(d.daily_total_value - f.total_order_value) as varchar) as detail3, cast(d.daily_total_quantity as varchar) as detail4, cast(f.total_quantity as varchar) as detail5
from daily_totals d
join fact_totals f on d.month_start = f.date and d.supplier = f.supplier
where abs(d.daily_total_value - f.total_order_value) > 0.01
   or abs(d.daily_total_quantity - f.total_quantity) > 0.01
   or abs(d.daily_order_count - f.total_orders) > 0

union all

select 'on_time_delivery_rate', cast(d.month_start as varchar), d.supplier, 
    cast(d.on_time_count as varchar), cast(f.on_time_orders as varchar), cast(abs(d.on_time_count - f.on_time_orders) as varchar), cast(d.total_count as varchar), cast(f.total_orders_for_delivery as varchar)
from daily_delivery d
join fact_delivery f on d.month_start = f.date and d.supplier = f.supplier
where abs(d.on_time_count - f.on_time_orders) > 0
   or abs(d.total_count - f.total_orders_for_delivery) > 0
   or abs(round(d.on_time_count * 100.0 / nullif(d.total_count, 0), 2) - f.on_time_delivery_rate_pct) > 0.01

union all

select 'quality_issue_rate', cast(d.month_start as varchar), d.supplier, 
    cast(d.quality_issue_count as varchar), cast(f.orders_with_quality_issues as varchar), cast(abs(d.quality_issue_count - f.orders_with_quality_issues) as varchar), cast(d.total_count as varchar), cast(f.total_orders as varchar)
from daily_quality d
join fact_quality f on d.month_start = f.date and d.supplier = f.supplier
where abs(d.quality_issue_count - f.orders_with_quality_issues) > 0
   or abs(d.total_count - f.total_orders) > 0
   or abs(round(d.quality_issue_count * 100.0 / nullif(d.total_count, 0), 2) - f.quality_issue_rate_pct) > 0.01

union all

select 'effective_unit_cost', cast(date as varchar), supplier, 
    cast(total_order_value as varchar), cast(total_quantity as varchar), cast(effective_unit_cost as varchar), cast(round(total_order_value / nullif(total_quantity, 0), 2) as varchar), cast(abs(effective_unit_cost - round(total_order_value / nullif(total_quantity, 0), 2)) as varchar)
from {{ ref('fact_supply_chain_monthly') }}
where abs(effective_unit_cost - round(total_order_value / nullif(total_quantity, 0), 2)) > 0.01 and total_quantity > 0

union all

select 'delivery_performance_category', cast(date as varchar), supplier, 
    cast(on_time_delivery_rate_pct as varchar), cast(delivery_performance_category as varchar),
    case 
        when on_time_delivery_rate_pct >= 95 then 'Excellent'
        when on_time_delivery_rate_pct >= 85 then 'Good'
        when on_time_delivery_rate_pct >= 70 then 'Fair'
        else 'Poor'
    end as detail4, NULL, NULL
from {{ ref('fact_supply_chain_monthly') }}
where delivery_performance_category != 
    case 
        when on_time_delivery_rate_pct >= 95 then 'Excellent'
        when on_time_delivery_rate_pct >= 85 then 'Good'
        when on_time_delivery_rate_pct >= 70 then 'Fair'
        else 'Poor'
    end

union all

select 'quality_performance_category', cast(date as varchar), supplier, 
    cast(quality_issue_rate_pct as varchar), cast(quality_performance_category as varchar),
    case 
        when quality_issue_rate_pct <= 2 then 'Excellent'
        when quality_issue_rate_pct <= 5 then 'Good'
        when quality_issue_rate_pct <= 10 then 'Fair'
        else 'Poor'
    end as detail4, NULL, NULL
from {{ ref('fact_supply_chain_monthly') }}
where quality_performance_category != 
    case 
        when quality_issue_rate_pct <= 2 then 'Excellent'
        when quality_issue_rate_pct <= 5 then 'Good'
        when quality_issue_rate_pct <= 10 then 'Fair'
        else 'Poor'
    end

union all

select 'reliability_level', cast(date as varchar), supplier, 
    cast(avg_supplier_reliability as varchar), cast(reliability_level as varchar),
    case 
        when avg_supplier_reliability >= 0.95 then 'High'
        when avg_supplier_reliability >= 0.90 then 'Medium'
        else 'Low'
    end as detail4, NULL, NULL
from {{ ref('fact_supply_chain_monthly') }}
where reliability_level != 
    case 
        when avg_supplier_reliability >= 0.95 then 'High'
        when avg_supplier_reliability >= 0.90 then 'Medium'
        else 'Low'
    end

union all

select 'sustainability_level', cast(date as varchar), supplier, 
    cast(avg_sustainability_rating as varchar), cast(sustainability_level as varchar),
    case 
        when avg_sustainability_rating >= 4.5 then 'Excellent'
        when avg_sustainability_rating >= 4.0 then 'Good'
        when avg_sustainability_rating >= 3.0 then 'Fair'
        else 'Poor'
    end as detail4, NULL, NULL
from {{ ref('fact_supply_chain_monthly') }}
where sustainability_level != 
    case 
        when avg_sustainability_rating >= 4.5 then 'Excellent'
        when avg_sustainability_rating >= 4.0 then 'Good'
        when avg_sustainability_rating >= 3.0 then 'Fair'
        else 'Poor'
    end 