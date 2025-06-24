-- Test supply chain calculations and data quality
-- All SELECTs must have the same columns in the same order and types for UNION ALL
-- Columns: test_name, order_id, supplier, detail1, detail2, detail3, detail4, detail5

select 'unit_cost_calculation' as test_name, order_id, supplier, 
    cast(order_value as varchar) as detail1, cast(order_quantity as varchar) as detail2, cast(unit_cost as varchar) as detail3, cast(round(order_value / nullif(order_quantity, 0), 2) as varchar) as detail4, cast(abs(unit_cost - round(order_value / nullif(order_quantity, 0), 2)) as varchar) as detail5
from {{ ref('stg_supply_chain_data') }}
where abs(unit_cost - round(order_value / nullif(order_quantity, 0), 2)) > 0.01 and order_quantity > 0

union all

select 'defect_rate_calculation', order_id, supplier, 
    cast(defect_quantity as varchar), cast(order_quantity as varchar), cast(defect_rate_pct as varchar), cast(round(defect_quantity / nullif(order_quantity, 0) * 100, 2) as varchar), cast(abs(defect_rate_pct - round(defect_quantity / nullif(order_quantity, 0) * 100, 2)) as varchar)
from {{ ref('stg_supply_chain_data') }}
where abs(defect_rate_pct - round(defect_quantity / nullif(order_quantity, 0) * 100, 2)) > 0.01 and order_quantity > 0

union all

select 'delivery_variance_calculation', order_id, supplier, 
    cast(expected_delivery as varchar), cast(actual_delivery as varchar), cast(delivery_variance_days as varchar), cast(date_diff('day', expected_delivery, actual_delivery) as varchar), cast(abs(delivery_variance_days - date_diff('day', expected_delivery, actual_delivery)) as varchar)
from {{ ref('stg_supply_chain_data') }}
where abs(delivery_variance_days - date_diff('day', expected_delivery, actual_delivery)) > 0

union all

select 'on_time_delivery_flag', order_id, supplier, 
    cast(expected_delivery as varchar), cast(actual_delivery as varchar), cast(on_time_delivery as varchar), cast((actual_delivery <= expected_delivery) as varchar), NULL
from {{ ref('stg_supply_chain_data') }}
where on_time_delivery != (actual_delivery <= expected_delivery)

union all

select 'supplier_reliability_range', order_id, supplier, 
    cast(supplier_reliability as varchar), NULL, NULL, NULL, NULL
from {{ ref('stg_supply_chain_data') }}
where supplier_reliability < 0 or supplier_reliability > 1

union all

select 'sustainability_rating_range', order_id, supplier, 
    cast(sustainability_rating as varchar), NULL, NULL, NULL, NULL
from {{ ref('stg_supply_chain_data') }}
where sustainability_rating < 1 or sustainability_rating > 5

union all

select 'delivery_performance_categories', order_id, supplier, 
    cast(delivery_performance as varchar), NULL, NULL, NULL, NULL
from {{ ref('stg_supply_chain_data') }}
where delivery_performance not in ('On Time', 'Slightly Late', 'Late', 'Very Late')

union all

select 'quality_status_categories', order_id, supplier, 
    cast(quality_status as varchar), NULL, NULL, NULL, NULL
from {{ ref('stg_supply_chain_data') }}
where quality_status not in ('Quality Issues', 'No Quality Issues')

union all

select 'defect_categories', order_id, supplier, 
    cast(defect_category as varchar), NULL, NULL, NULL, NULL
from {{ ref('stg_supply_chain_data') }}
where defect_category not in ('No Defects', 'Low Defect Rate', 'Medium Defect Rate', 'High Defect Rate')

union all

select 'sustainability_categories', order_id, supplier, 
    cast(sustainability_category as varchar), NULL, NULL, NULL, NULL
from {{ ref('stg_supply_chain_data') }}
where sustainability_category not in ('Low Sustainability', 'Medium Sustainability', 'High Sustainability')

union all

select 'reliability_categories', order_id, supplier, 
    cast(reliability_category as varchar), NULL, NULL, NULL, NULL
from {{ ref('stg_supply_chain_data') }}
where reliability_category not in ('Low Reliability', 'Medium Reliability', 'High Reliability') 