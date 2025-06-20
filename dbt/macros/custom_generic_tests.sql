-- Custom generic tests for PackagingCo BI Portfolio
-- These tests can be applied to any model using the test: macro_name syntax

-- Test that recycled + virgin material percentages equal 100%
{% test material_percentages_sum_to_100(model) %}

with validation as (
    select
        date,
        product_line,
        facility,
        avg_recycled_material_pct,
        avg_virgin_material_pct,
        abs(avg_recycled_material_pct + avg_virgin_material_pct - 100) as difference
    from {{ model }}
),

validation_errors as (
    select
        date,
        product_line,
        facility,
        avg_recycled_material_pct,
        avg_virgin_material_pct,
        difference
    from validation
    where difference > 1  -- Allow for small rounding differences
)

select *
from validation_errors

{% endtest %}

-- Test that water usage equals recycled + fresh water
{% test water_usage_consistency(model) %}

with validation as (
    select
        date,
        product_line,
        facility,
        total_water_usage_liters,
        total_water_recycled_liters,
        total_water_fresh_liters,
        abs(total_water_usage_liters - (total_water_recycled_liters + total_water_fresh_liters)) as difference
    from {{ model }}
),

validation_errors as (
    select
        date,
        product_line,
        facility,
        total_water_usage_liters,
        total_water_recycled_liters,
        total_water_fresh_liters,
        difference
    from validation
    where difference > 15000  -- Allow for reasonable measurement differences in water usage (process losses, steam, etc.)
)

select *
from validation_errors

{% endtest %}

-- Test that overall metrics match calculated totals
{% test overall_metrics_consistency(model) %}

with validation as (
    select
        date,
        product_line,
        facility,
        total_emissions_kg_co2,
        total_batch_size,
        overall_emissions_per_unit,
        round(total_emissions_kg_co2 / nullif(total_batch_size, 0), 6) as calculated_emissions_per_unit,
        abs(overall_emissions_per_unit - round(total_emissions_kg_co2 / nullif(total_batch_size, 0), 6)) as difference
    from {{ model }}
),

validation_errors as (
    select
        date,
        product_line,
        facility,
        total_emissions_kg_co2,
        total_batch_size,
        overall_emissions_per_unit,
        calculated_emissions_per_unit,
        difference
    from validation
    where difference > 0.000001  -- Allow for small rounding differences
)

select *
from validation_errors

{% endtest %}

-- Test that batch counts are consistent
{% test batch_count_consistency(model) %}

with validation as (
    select
        date,
        product_line,
        facility,
        total_batches,
        high_recycled_content_batches,
        high_renewable_energy_batches,
        high_efficiency_batches,
        excellent_quality_batches,
        (high_recycled_content_batches + high_renewable_energy_batches + high_efficiency_batches + excellent_quality_batches) as sum_special_batches
    from {{ model }}
),

validation_errors as (
    select
        date,
        product_line,
        facility,
        total_batches,
        high_recycled_content_batches,
        high_renewable_energy_batches,
        high_efficiency_batches,
        excellent_quality_batches,
        sum_special_batches
    from validation
    where sum_special_batches > total_batches  -- Special batches should not exceed total batches
)

select *
from validation_errors

{% endtest %}

-- Test that percentage rates are within valid ranges (0-100)
{% test percentage_ranges(model) %}

with validation as (
    select
        date,
        product_line,
        facility,
        avg_recycled_material_pct,
        avg_virgin_material_pct,
        avg_recycling_rate_pct,
        avg_renewable_energy_pct,
        avg_defect_rate_pct,
        overall_water_recycling_pct,
        overall_water_conservation_pct,
        high_recycled_content_rate_pct,
        high_renewable_energy_rate_pct,
        high_efficiency_rate_pct,
        excellent_quality_rate_pct
    from {{ model }}
),

validation_errors as (
    select
        date,
        product_line,
        facility,
        avg_recycled_material_pct,
        avg_virgin_material_pct,
        avg_recycling_rate_pct,
        avg_renewable_energy_pct,
        avg_defect_rate_pct,
        overall_water_recycling_pct,
        overall_water_conservation_pct,
        high_recycled_content_rate_pct,
        high_renewable_energy_rate_pct,
        high_efficiency_rate_pct,
        excellent_quality_rate_pct
    from validation
    where avg_recycled_material_pct < 0 or avg_recycled_material_pct > 100
       or avg_virgin_material_pct < 0 or avg_virgin_material_pct > 100
       or avg_recycling_rate_pct < 0 or avg_recycling_rate_pct > 100
       or avg_renewable_energy_pct < 0 or avg_renewable_energy_pct > 100
       or avg_defect_rate_pct < 0 or avg_defect_rate_pct > 100
       or overall_water_recycling_pct < 0 or overall_water_recycling_pct > 100
       or overall_water_conservation_pct < 0 or overall_water_conservation_pct > 100
       or high_recycled_content_rate_pct < 0 or high_recycled_content_rate_pct > 100
       or high_renewable_energy_rate_pct < 0 or high_renewable_energy_rate_pct > 100
       or high_efficiency_rate_pct < 0 or high_efficiency_rate_pct > 100
       or excellent_quality_rate_pct < 0 or excellent_quality_rate_pct > 100
)

select *
from validation_errors

{% endtest %}

-- Test that efficiency and quality scores are within valid ranges (0-1)
{% test score_ranges(model) %}

with validation as (
    select
        date,
        product_line,
        facility,
        avg_efficiency_rating,
        avg_quality_score
    from {{ model }}
),

validation_errors as (
    select
        date,
        product_line,
        facility,
        avg_efficiency_rating,
        avg_quality_score
    from validation
    where avg_efficiency_rating < 0 or avg_efficiency_rating > 1
       or avg_quality_score < 0 or avg_quality_score > 1
)

select *
from validation_errors

{% endtest %}

-- Test that profit margin equals revenue minus costs (for financial models)
{% test profit_margin_calculation(model) %}

with validation as (
    select
        date,
        product_line,
        region,
        customer_segment,
        total_revenue,
        total_cost_of_goods,
        total_operating_cost,
        total_profit_margin,
        (total_revenue - total_cost_of_goods - total_operating_cost) as calculated_profit,
        abs(total_profit_margin - (total_revenue - total_cost_of_goods - total_operating_cost)) as difference
    from {{ model }}
),

validation_errors as (
    select
        date,
        product_line,
        region,
        customer_segment,
        total_revenue,
        total_cost_of_goods,
        total_operating_cost,
        total_profit_margin,
        calculated_profit,
        difference
    from validation
    where difference > 1  -- Allow for small rounding differences
)

select *
from validation_errors

{% endtest %}

-- Test that revenue per unit * units sold equals total revenue (for transaction-level models)
{% test revenue_consistency(model) %}

with validation as (
    select
        transaction_id,
        units_sold,
        revenue,
        unit_price,
        (unit_price * units_sold) as calculated_revenue,
        abs(revenue - (unit_price * units_sold)) as difference
    from {{ model }}
),

validation_errors as (
    select
        transaction_id,
        units_sold,
        revenue,
        unit_price,
        calculated_revenue,
        difference
    from validation
    where difference > 0.01  -- Allow for small rounding differences
)

select *
from validation_errors

{% endtest %}

-- Test that transaction timestamps are within reasonable ranges
{% test timestamp_reasonableness(model) %}

with validation as (
    select
        transaction_id,
        timestamp,
        date,
        extract(year from timestamp) as timestamp_year,
        extract(year from date) as date_year
    from {{ model }}
),

validation_errors as (
    select
        transaction_id,
        timestamp,
        date,
        timestamp_year,
        date_year
    from validation
    where timestamp_year < 2020 or timestamp_year > 2030  -- Reasonable year range
       or abs(timestamp_year - date_year) > 1  -- Timestamp and date should be in same year
)

select *
from validation_errors

{% endtest %}

-- Test that batch sizes are reasonable for production
{% test batch_size_reasonableness(model) %}

with validation as (
    select
        batch_id,
        batch_size,
        product_line
    from {{ model }}
),

validation_errors as (
    select
        batch_id,
        batch_size,
        product_line
    from validation
    where batch_size <= 0  -- Batch size should be positive
       or batch_size > 100000  -- Unreasonably large batch size
)

select *
from validation_errors

{% endtest %}

-- Test that environmental impact scores are reasonable
{% test environmental_impact_reasonableness(model) %}

with validation as (
    select
        batch_id,
        environmental_impact_score,
        emissions_per_unit,
        energy_per_unit,
        water_per_unit,
        waste_per_unit
    from {{ model }}
),

validation_errors as (
    select
        batch_id,
        environmental_impact_score,
        emissions_per_unit,
        energy_per_unit,
        water_per_unit,
        waste_per_unit
    from validation
    where environmental_impact_score < -100  -- Unreasonably low (too good to be true)
       or environmental_impact_score > 100   -- Unreasonably high
       or emissions_per_unit < 0
       or energy_per_unit < 0
       or water_per_unit < 0
       or waste_per_unit < 0
)

select *
from validation_errors

{% endtest %} 