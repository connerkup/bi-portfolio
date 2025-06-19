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
        round(total_emissions_kg_co2 / nullif(total_batch_size, 0), 4) as calculated_emissions_per_unit,
        abs(overall_emissions_per_unit - round(total_emissions_kg_co2 / nullif(total_batch_size, 0), 4)) as difference
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
    where difference > 0.0001  -- Allow for small rounding differences
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