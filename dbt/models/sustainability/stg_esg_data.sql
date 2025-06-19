{{
  config(
    materialized='view',
    description='Staged ESG data from raw CSV files'
  )
}}

with source as (
    select * from {{ ref('sample_esg_data') }}
),

staged as (
    select
        -- Primary keys and identifiers
        date,
        product_line,
        facility,
        
        -- Production metrics
        batch_size,
        production_hours,
        
        -- Environmental metrics
        emissions_kg_co2,
        energy_consumption_kwh,
        water_usage_liters,
        water_recycled_liters,
        water_fresh_liters,
        waste_generated_kg,
        
        -- Material composition
        recycled_material_pct,
        virgin_material_pct,
        recycling_rate_pct,
        renewable_energy_pct,
        
        -- Quality and efficiency
        efficiency_rating,
        quality_score,
        defect_rate_pct,
        
        -- Calculated environmental metrics
        round(emissions_kg_co2 / nullif(batch_size, 0), 4) as emissions_per_unit,
        round(energy_consumption_kwh / nullif(batch_size, 0), 4) as energy_per_unit,
        round(water_usage_liters / nullif(batch_size, 0), 4) as water_per_unit,
        round(waste_generated_kg / nullif(batch_size, 0), 4) as waste_per_unit,
        
        -- Efficiency metrics
        round(batch_size / nullif(production_hours, 0), 2) as units_per_hour,
        round(emissions_kg_co2 / nullif(energy_consumption_kwh, 0), 4) as emissions_per_kwh,
        round(water_usage_liters / nullif(energy_consumption_kwh, 0), 4) as water_per_kwh,
        
        -- Sustainability ratios
        round(water_recycled_liters / nullif(water_usage_liters, 0) * 100, 2) as water_recycling_efficiency_pct,
        round((water_usage_liters - water_fresh_liters) / nullif(water_usage_liters, 0) * 100, 2) as water_conservation_pct,
        
        -- Date dimensions
        extract(year from date) as year,
        extract(month from date) as month,
        extract(quarter from date) as quarter,
        date_trunc('month', date) as month_start,
        date_trunc('quarter', date) as quarter_start,
        date_trunc('year', date) as year_start,
        
        -- Business logic flags
        case 
            when recycled_material_pct >= 80 then 'High Recycled Content'
            when recycled_material_pct >= 50 then 'Medium Recycled Content'
            else 'Low Recycled Content'
        end as recycled_content_category,
        
        case 
            when renewable_energy_pct >= 70 then 'High Renewable Energy'
            when renewable_energy_pct >= 40 then 'Medium Renewable Energy'
            else 'Low Renewable Energy'
        end as renewable_energy_category,
        
        case 
            when efficiency_rating >= 0.95 then 'High Efficiency'
            when efficiency_rating >= 0.90 then 'Medium Efficiency'
            else 'Low Efficiency'
        end as efficiency_category,
        
        case 
            when quality_score >= 0.98 then 'Excellent Quality'
            when quality_score >= 0.95 then 'Good Quality'
            when quality_score >= 0.90 then 'Acceptable Quality'
            else 'Poor Quality'
        end as quality_category,
        
        case 
            when facility like '%North America%' then 'North America'
            when facility like '%Europe%' then 'Europe'
            when facility like '%Asia Pacific%' then 'Asia Pacific'
            else 'Other'
        end as facility_region,
        
        case 
            when facility like '%sustainability_initiative%' or facility like '%Advanced%' or facility like '%Cutting-edge%' then 'Advanced'
            when facility like '%Standard%' then 'Standard'
            else 'Basic'
        end as technology_level
        
    from source
)

select * from staged 