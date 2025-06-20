{{
  config(
    materialized='view',
    description='Staged transaction-level ESG data with enhanced sustainability metrics',
    tests=[
      'test_positive_values',
      'batch_size_reasonableness',
      'environmental_impact_reasonableness'
    ]
  )
}}

with source as (
    select * from {{ source('raw_data', 'esg_transactions') }}
),

staged as (
    select
        -- Primary keys and identifiers
        batch_id,
        date,
        
        -- Business dimensions
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
        
        -- Additional fields
        operator_id,
        equipment_id,
        energy_source,
        maintenance_status,
        temperature_celsius,
        humidity_pct,
        
        -- Calculated environmental metrics per unit
        round(emissions_kg_co2 / nullif(batch_size, 0), 6) as emissions_per_unit,
        round(energy_consumption_kwh / nullif(batch_size, 0), 6) as energy_per_unit,
        round(water_usage_liters / nullif(batch_size, 0), 6) as water_per_unit,
        round(waste_generated_kg / nullif(batch_size, 0), 6) as waste_per_unit,
        
        -- Production efficiency metrics
        round(batch_size / nullif(production_hours, 0), 2) as units_per_hour,
        round(energy_consumption_kwh / nullif(production_hours, 0), 2) as energy_per_hour,
        round(emissions_kg_co2 / nullif(production_hours, 0), 4) as emissions_per_hour,
        round(water_usage_liters / nullif(production_hours, 0), 2) as water_per_hour,
        
        -- Resource efficiency ratios
        round(emissions_kg_co2 / nullif(energy_consumption_kwh, 0), 6) as emissions_per_kwh,
        round(water_usage_liters / nullif(energy_consumption_kwh, 0), 4) as water_per_kwh,
        round(waste_generated_kg / nullif(energy_consumption_kwh, 0), 6) as waste_per_kwh,
        
        -- Water management ratios
        round(water_recycled_liters / nullif(water_usage_liters, 0) * 100, 2) as water_recycling_efficiency_pct,
        round(water_fresh_liters / nullif(water_usage_liters, 0) * 100, 2) as fresh_water_dependency_pct,
        round((water_usage_liters - water_fresh_liters) / nullif(water_usage_liters, 0) * 100, 2) as water_conservation_pct,
        
        -- Material sustainability ratios
        round(100 - virgin_material_pct, 2) as calculated_recycled_pct,
        round(recycled_material_pct + virgin_material_pct, 2) as total_material_pct,
        
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
        
        -- Shift and timing analysis
        case 
            when extract(dow from date) in (0, 6) then 'Weekend'
            else 'Weekday'
        end as day_type,
        
        -- Sustainability categorization
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
            when water_recycling_efficiency_pct >= 80 then 'High Water Recycling'
            when water_recycling_efficiency_pct >= 60 then 'Medium Water Recycling'
            else 'Low Water Recycling'
        end as water_recycling_category,
        
        -- Emissions categorization (per unit)
        case 
            when round(emissions_kg_co2 / nullif(batch_size, 0), 6) <= 0.5 then 'Low Emissions'
            when round(emissions_kg_co2 / nullif(batch_size, 0), 6) <= 1.0 then 'Medium Emissions'
            else 'High Emissions'
        end as emissions_category,
        
        -- Facility analysis
        case 
            when facility like '%North America%' then 'North America'
            when facility like '%Europe%' then 'Europe'
            when facility like '%Asia Pacific%' then 'Asia Pacific'
            else 'Other'
        end as facility_region,
        
        case 
            when facility like '%Advanced%' or facility like '%Cutting-edge%' then 'Advanced'
            when facility like '%Standard%' then 'Standard'
            else 'Basic'
        end as technology_level,
        
        -- Batch size categorization
        case 
            when batch_size >= 1000 then 'Large Batch'
            when batch_size >= 500 then 'Medium Batch'
            else 'Small Batch'
        end as batch_size_category,
        
        -- Product sustainability profile
        case 
            when product_line in ('Biodegradable Packaging', 'Paper Packaging') then 'Sustainable'
            when product_line in ('Glass Bottles', 'Aluminum Cans') then 'Recyclable'
            else 'Traditional'
        end as sustainability_category,
        
        -- Data quality flags
        case 
            when water_usage_liters != (water_recycled_liters + water_fresh_liters) 
                 and abs(water_usage_liters - (water_recycled_liters + water_fresh_liters)) > 10 then 'Water Balance Issue'
            when abs(recycled_material_pct + virgin_material_pct - 100) > 1 then 'Material Percentage Issue'
            when emissions_kg_co2 <= 0 or energy_consumption_kwh <= 0 or batch_size <= 0 then 'Invalid Values'
            when efficiency_rating > 1 or quality_score > 1 then 'Invalid Ratings'
            when recycled_material_pct > 100 or virgin_material_pct > 100 then 'Invalid Percentages'
            else 'Valid'
        end as data_quality_flag
        
    from source
),

final as (
    select 
        *,
        -- Comprehensive sustainability scoring
        case 
            when recycled_content_category = 'High Recycled Content' 
                 and renewable_energy_category = 'High Renewable Energy'
                 and efficiency_category = 'High Efficiency'
                 and water_recycling_category = 'High Water Recycling' then 'Sustainability Leader'
            when recycled_content_category in ('High Recycled Content', 'Medium Recycled Content')
                 and renewable_energy_category in ('High Renewable Energy', 'Medium Renewable Energy')
                 and efficiency_category in ('High Efficiency', 'Medium Efficiency') then 'Sustainability Performer'
            when recycled_content_category != 'Low Recycled Content'
                 or renewable_energy_category != 'Low Renewable Energy'
                 or efficiency_category != 'Low Efficiency' then 'Sustainability Improver'
            else 'Sustainability Laggard'
        end as sustainability_performance,
        
        -- Overall environmental impact score (lower is better)
        round(
            (emissions_per_unit * 10) +  -- Weight emissions heavily
            (energy_per_unit * 2) +      -- Weight energy consumption
            (water_per_unit * 0.1) +     -- Weight water usage
            (waste_per_unit * 5) -       -- Weight waste generation
            (recycled_material_pct * 0.01) - -- Reward recycled content
            (renewable_energy_pct * 0.005),  -- Reward renewable energy
            4
        ) as environmental_impact_score
        
    from staged
)

select * from final
where data_quality_flag = 'Valid'  -- Filter out data quality issues 