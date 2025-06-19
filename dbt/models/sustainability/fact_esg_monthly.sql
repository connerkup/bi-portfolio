{{
  config(
    materialized='table',
    description='Monthly ESG metrics fact table for trend analysis'
  )
}}

with esg_staged as (
    select * from {{ ref('stg_esg_data') }}
),

monthly_esg as (
    select
        -- Time dimensions
        month_start as date,
        year,
        month,
        quarter,
        
        -- Business dimensions
        product_line,
        facility,
        facility_region,
        technology_level,
        
        -- Aggregated production metrics
        sum(batch_size) as total_batch_size,
        sum(production_hours) as total_production_hours,
        
        -- Aggregated environmental metrics
        sum(emissions_kg_co2) as total_emissions_kg_co2,
        sum(energy_consumption_kwh) as total_energy_consumption_kwh,
        sum(water_usage_liters) as total_water_usage_liters,
        sum(water_recycled_liters) as total_water_recycled_liters,
        sum(water_fresh_liters) as total_water_fresh_liters,
        sum(waste_generated_kg) as total_waste_generated_kg,
        
        -- Average material composition
        avg(recycled_material_pct) as avg_recycled_material_pct,
        avg(virgin_material_pct) as avg_virgin_material_pct,
        avg(recycling_rate_pct) as avg_recycling_rate_pct,
        avg(renewable_energy_pct) as avg_renewable_energy_pct,
        
        -- Average quality and efficiency
        avg(efficiency_rating) as avg_efficiency_rating,
        avg(quality_score) as avg_quality_score,
        avg(defect_rate_pct) as avg_defect_rate_pct,
        
        -- Average per-unit metrics
        avg(emissions_per_unit) as avg_emissions_per_unit,
        avg(energy_per_unit) as avg_energy_per_unit,
        avg(water_per_unit) as avg_water_per_unit,
        avg(waste_per_unit) as avg_waste_per_unit,
        
        -- Average efficiency metrics
        avg(units_per_hour) as avg_units_per_hour,
        avg(emissions_per_kwh) as avg_emissions_per_kwh,
        avg(water_per_kwh) as avg_water_per_kwh,
        
        -- Average sustainability ratios
        avg(water_recycling_efficiency_pct) as avg_water_recycling_efficiency_pct,
        avg(water_conservation_pct) as avg_water_conservation_pct,
        
        -- Business logic aggregations
        count(case when recycled_content_category = 'High Recycled Content' then 1 end) as high_recycled_content_batches,
        count(case when renewable_energy_category = 'High Renewable Energy' then 1 end) as high_renewable_energy_batches,
        count(case when efficiency_category = 'High Efficiency' then 1 end) as high_efficiency_batches,
        count(case when quality_category = 'Excellent Quality' then 1 end) as excellent_quality_batches,
        
        -- Batch counts
        count(*) as total_batches,
        
        -- Calculated derived metrics
        round(total_emissions_kg_co2 / nullif(total_batch_size, 0), 4) as overall_emissions_per_unit,
        round(total_energy_consumption_kwh / nullif(total_batch_size, 0), 4) as overall_energy_per_unit,
        round(total_water_usage_liters / nullif(total_batch_size, 0), 4) as overall_water_per_unit,
        round(total_waste_generated_kg / nullif(total_batch_size, 0), 4) as overall_waste_per_unit,
        
        -- Efficiency ratios
        round(total_batch_size / nullif(total_production_hours, 0), 2) as overall_units_per_hour,
        round(total_emissions_kg_co2 / nullif(total_energy_consumption_kwh, 0), 4) as overall_emissions_per_kwh,
        round(total_water_usage_liters / nullif(total_energy_consumption_kwh, 0), 4) as overall_water_per_kwh,
        
        -- Sustainability ratios
        round(total_water_recycled_liters / nullif(total_water_usage_liters, 0) * 100, 2) as overall_water_recycling_pct,
        round((total_water_usage_liters - total_water_fresh_liters) / nullif(total_water_usage_liters, 0) * 100, 2) as overall_water_conservation_pct,
        
        -- Business health indicators
        round(high_recycled_content_batches * 100.0 / nullif(total_batches, 0), 2) as high_recycled_content_rate_pct,
        round(high_renewable_energy_batches * 100.0 / nullif(total_batches, 0), 2) as high_renewable_energy_rate_pct,
        round(high_efficiency_batches * 100.0 / nullif(total_batches, 0), 2) as high_efficiency_rate_pct,
        round(excellent_quality_batches * 100.0 / nullif(total_batches, 0), 2) as excellent_quality_rate_pct
        
    from esg_staged
    group by 1, 2, 3, 4, 5, 6, 7, 8
),

-- Add trend analysis using window functions
trend_analysis as (
    select
        *,
        -- Month-over-month changes
        lag(overall_emissions_per_unit, 1) over (
            partition by product_line, facility 
            order by date
        ) as prev_month_emissions_per_unit,
        
        lag(overall_energy_per_unit, 1) over (
            partition by product_line, facility 
            order by date
        ) as prev_month_energy_per_unit,
        
        lag(overall_water_per_unit, 1) over (
            partition by product_line, facility 
            order by date
        ) as prev_month_water_per_unit,
        
        lag(avg_recycled_material_pct, 1) over (
            partition by product_line, facility 
            order by date
        ) as prev_month_recycled_pct,
        
        lag(avg_renewable_energy_pct, 1) over (
            partition by product_line, facility 
            order by date
        ) as prev_month_renewable_pct,
        
        -- 3-month moving averages for trend analysis
        avg(overall_emissions_per_unit) over (
            partition by product_line, facility 
            order by date 
            rows between 2 preceding and current row
        ) as emissions_3m_avg,
        
        avg(overall_energy_per_unit) over (
            partition by product_line, facility 
            order by date 
            rows between 2 preceding and current row
        ) as energy_3m_avg,
        
        avg(avg_recycled_material_pct) over (
            partition by product_line, facility 
            order by date 
            rows between 2 preceding and current row
        ) as recycled_3m_avg,
        
        -- Year-over-year comparison (if we have enough data)
        lag(overall_emissions_per_unit, 12) over (
            partition by product_line, facility 
            order by date
        ) as yoy_emissions_per_unit,
        
        lag(avg_recycled_material_pct, 12) over (
            partition by product_line, facility 
            order by date
        ) as yoy_recycled_pct
        
    from monthly_esg
),

final as (
    select
        *,
        -- Additional sustainability insights
        case 
            when overall_emissions_per_unit <= 0.5 then 'Low Emissions'
            when overall_emissions_per_unit <= 1.0 then 'Medium Emissions'
            else 'High Emissions'
        end as emissions_category,
        
        case 
            when overall_water_recycling_pct >= 80 then 'High Water Recycling'
            when overall_water_recycling_pct >= 60 then 'Medium Water Recycling'
            else 'Low Water Recycling'
        end as water_recycling_category,
        
        case 
            when avg_recycled_material_pct >= 70 then 'High Recycled Content'
            when avg_recycled_material_pct >= 40 then 'Medium Recycled Content'
            else 'Low Recycled Content'
        end as recycled_content_category,
        
        case 
            when avg_renewable_energy_pct >= 60 then 'High Renewable Energy'
            when avg_renewable_energy_pct >= 30 then 'Medium Renewable Energy'
            else 'Low Renewable Energy'
        end as renewable_energy_category,
        
        case 
            when avg_efficiency_rating >= 0.95 then 'High Efficiency'
            when avg_efficiency_rating >= 0.90 then 'Medium Efficiency'
            else 'Low Efficiency'
        end as efficiency_category,
        
        case 
            when avg_quality_score >= 0.98 then 'Excellent Quality'
            when avg_quality_score >= 0.95 then 'Good Quality'
            when avg_quality_score >= 0.90 then 'Acceptable Quality'
            else 'Poor Quality'
        end as quality_category,
        
        case 
            when technology_level = 'Advanced' and avg_efficiency_rating >= 0.95 then 'Advanced High Performance'
            when technology_level = 'Advanced' then 'Advanced Standard Performance'
            when technology_level = 'Standard' and avg_efficiency_rating >= 0.90 then 'Standard High Performance'
            when technology_level = 'Standard' then 'Standard Performance'
            when technology_level = 'Basic' and avg_efficiency_rating >= 0.85 then 'Basic High Performance'
            else 'Basic Performance'
        end as technology_performance,
        
        -- Trend indicators
        case 
            when prev_month_emissions_per_unit is not null 
                 and overall_emissions_per_unit < prev_month_emissions_per_unit * 0.95 then 'Improving'
            when prev_month_emissions_per_unit is not null 
                 and overall_emissions_per_unit > prev_month_emissions_per_unit * 1.05 then 'Declining'
            else 'Stable'
        end as emissions_trend,
        
        case 
            when prev_month_recycled_pct is not null 
                 and avg_recycled_material_pct > prev_month_recycled_pct + 5 then 'Improving'
            when prev_month_recycled_pct is not null 
                 and avg_recycled_material_pct < prev_month_recycled_pct - 5 then 'Declining'
            else 'Stable'
        end as recycled_content_trend,
        
        case 
            when prev_month_renewable_pct is not null 
                 and avg_renewable_energy_pct > prev_month_renewable_pct + 5 then 'Improving'
            when prev_month_renewable_pct is not null 
                 and avg_renewable_energy_pct < prev_month_renewable_pct - 5 then 'Declining'
            else 'Stable'
        end as renewable_energy_trend,
        
        -- Performance benchmarks (industry standards)
        case 
            when overall_emissions_per_unit <= 0.3 then 'Industry Leader'
            when overall_emissions_per_unit <= 0.7 then 'Above Average'
            when overall_emissions_per_unit <= 1.2 then 'Average'
            else 'Below Average'
        end as emissions_benchmark,
        
        case 
            when avg_recycled_material_pct >= 80 then 'Industry Leader'
            when avg_recycled_material_pct >= 60 then 'Above Average'
            when avg_recycled_material_pct >= 40 then 'Average'
            else 'Below Average'
        end as recycled_content_benchmark,
        
        case 
            when avg_renewable_energy_pct >= 70 then 'Industry Leader'
            when avg_renewable_energy_pct >= 50 then 'Above Average'
            when avg_renewable_energy_pct >= 30 then 'Average'
            else 'Below Average'
        end as renewable_energy_benchmark,
        
        -- Sustainability score (composite metric)
        round(
            (case when overall_emissions_per_unit <= 0.5 then 100
                  when overall_emissions_per_unit <= 1.0 then 75
                  when overall_emissions_per_unit <= 1.5 then 50
                  else 25 end) * 0.3 +
            (case when avg_recycled_material_pct >= 70 then 100
                  when avg_recycled_material_pct >= 40 then 75
                  when avg_recycled_material_pct >= 20 then 50
                  else 25 end) * 0.3 +
            (case when avg_renewable_energy_pct >= 60 then 100
                  when avg_renewable_energy_pct >= 30 then 75
                  when avg_renewable_energy_pct >= 15 then 50
                  else 25 end) * 0.2 +
            (case when overall_water_recycling_pct >= 80 then 100
                  when overall_water_recycling_pct >= 60 then 75
                  when overall_water_recycling_pct >= 40 then 50
                  else 25 end) * 0.2, 1
        ) as sustainability_score,
        
        -- Risk assessment
        case 
            when overall_emissions_per_unit > 1.5 
                 or avg_recycled_material_pct < 20 
                 or avg_renewable_energy_pct < 10 
                 or overall_water_recycling_pct < 30 then 'High Risk'
            when overall_emissions_per_unit > 1.0 
                 or avg_recycled_material_pct < 40 
                 or avg_renewable_energy_pct < 20 
                 or overall_water_recycling_pct < 50 then 'Medium Risk'
            else 'Low Risk'
        end as sustainability_risk_level
        
    from trend_analysis
)

select * from final 