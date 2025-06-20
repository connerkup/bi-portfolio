{{
  config(
    materialized='table',
    description='Monthly ESG metrics fact table built from transaction-level data',
    tests=[
      'test_positive_values',
      'material_percentages_sum_to_100',
      'water_usage_consistency',
      'overall_metrics_consistency',
      'batch_count_consistency',
      'percentage_ranges',
      'score_ranges'
    ]
  )
}}

with esg_transactions as (
    select * from {{ ref('stg_esg_transactions') }}
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
        count(case when sustainability_performance = 'Sustainability Leader' then 1 end) as sustainability_leader_batches,
        count(case when sustainability_performance = 'Sustainability Performer' then 1 end) as sustainability_performer_batches,
        
        -- Batch size and timing analysis
        count(case when batch_size_category = 'Large Batch' then 1 end) as large_batches,
        count(case when batch_size_category = 'Medium Batch' then 1 end) as medium_batches,
        count(case when batch_size_category = 'Small Batch' then 1 end) as small_batches,
        count(case when day_type = 'Weekend' then 1 end) as weekend_batches,
        count(case when day_type = 'Weekday' then 1 end) as weekday_batches,
        
        -- Environmental impact analysis
        count(case when emissions_category = 'Low Emissions' then 1 end) as low_emissions_batches,
        count(case when emissions_category = 'Medium Emissions' then 1 end) as medium_emissions_batches,
        count(case when emissions_category = 'High Emissions' then 1 end) as high_emissions_batches,
        count(case when water_recycling_category = 'High Water Recycling' then 1 end) as high_water_recycling_batches,
        count(case when water_recycling_category = 'Medium Water Recycling' then 1 end) as medium_water_recycling_batches,
        count(case when water_recycling_category = 'Low Water Recycling' then 1 end) as low_water_recycling_batches,
        
        -- Product sustainability analysis
        count(case when sustainability_category = 'Sustainable' then 1 end) as sustainable_product_batches,
        count(case when sustainability_category = 'Recyclable' then 1 end) as recyclable_product_batches,
        count(case when sustainability_category = 'Traditional' then 1 end) as traditional_product_batches,
        
        -- Batch counts
        count(*) as total_batches,
        
        -- Calculated derived metrics
        round(total_emissions_kg_co2 / nullif(total_batch_size, 0), 6) as overall_emissions_per_unit,
        round(total_energy_consumption_kwh / nullif(total_batch_size, 0), 6) as overall_energy_per_unit,
        round(total_water_usage_liters / nullif(total_batch_size, 0), 6) as overall_water_per_unit,
        round(total_waste_generated_kg / nullif(total_batch_size, 0), 6) as overall_waste_per_unit,
        
        -- Efficiency ratios
        round(total_batch_size / nullif(total_production_hours, 0), 2) as overall_units_per_hour,
        round(total_emissions_kg_co2 / nullif(total_energy_consumption_kwh, 0), 6) as overall_emissions_per_kwh,
        round(total_water_usage_liters / nullif(total_energy_consumption_kwh, 0), 4) as overall_water_per_kwh,
        
        -- Sustainability ratios
        round(total_water_recycled_liters / nullif(total_water_usage_liters, 0) * 100, 2) as overall_water_recycling_pct,
        round((total_water_usage_liters - total_water_fresh_liters) / nullif(total_water_usage_liters, 0) * 100, 2) as overall_water_conservation_pct,
        
        -- Business health indicators
        round(high_recycled_content_batches * 100.0 / nullif(total_batches, 0), 2) as high_recycled_content_rate_pct,
        round(high_renewable_energy_batches * 100.0 / nullif(total_batches, 0), 2) as high_renewable_energy_rate_pct,
        round(high_efficiency_batches * 100.0 / nullif(total_batches, 0), 2) as high_efficiency_rate_pct,
        round(excellent_quality_batches * 100.0 / nullif(total_batches, 0), 2) as excellent_quality_rate_pct,
        round(sustainability_leader_batches * 100.0 / nullif(total_batches, 0), 2) as sustainability_leader_rate_pct,
        round(sustainability_performer_batches * 100.0 / nullif(total_batches, 0), 2) as sustainability_performer_rate_pct,
        
        -- Batch mix analysis
        round(large_batches * 100.0 / nullif(total_batches, 0), 2) as large_batch_rate_pct,
        round(sustainable_product_batches * 100.0 / nullif(total_batches, 0), 2) as sustainable_product_rate_pct,
        round(low_emissions_batches * 100.0 / nullif(total_batches, 0), 2) as low_emissions_rate_pct,
        round(high_water_recycling_batches * 100.0 / nullif(total_batches, 0), 2) as high_water_recycling_rate_pct,
        
        -- Production timing analysis
        round(weekend_batches * 100.0 / nullif(total_batches, 0), 2) as weekend_rate_pct
        
    from esg_transactions
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
        
        -- Transaction-level sustainability insights
        case 
            when sustainability_leader_rate_pct >= 25 then 'High Sustainability Leadership'
            when sustainability_leader_rate_pct >= 10 then 'Medium Sustainability Leadership'
            else 'Low Sustainability Leadership'
        end as sustainability_leadership_category,
        
        case 
            when sustainable_product_rate_pct >= 50 then 'High Sustainable Product Mix'
            when sustainable_product_rate_pct >= 25 then 'Medium Sustainable Product Mix'
            else 'Low Sustainable Product Mix'
        end as sustainable_product_mix_category,
        
        case 
            when low_emissions_rate_pct >= 60 then 'High Low Emissions Performance'
            when low_emissions_rate_pct >= 30 then 'Medium Low Emissions Performance'
            else 'Low Low Emissions Performance'
        end as low_emissions_performance_category,
        
        case 
            when high_water_recycling_rate_pct >= 70 then 'High Water Recycling Performance'
            when high_water_recycling_rate_pct >= 40 then 'Medium Water Recycling Performance'
            else 'Low Water Recycling Performance'
        end as water_recycling_performance_category,
        
        -- Composite sustainability score (0-100)
        round(
            -- Emissions component (25% weight) - lower is better
            (25 * (1 - least(overall_emissions_per_unit / 2.0, 1.0))) +
            -- Recycled material component (20% weight) - higher is better
            (20 * least(avg_recycled_material_pct / 100.0, 1.0)) +
            -- Renewable energy component (20% weight) - higher is better
            (20 * least(avg_renewable_energy_pct / 100.0, 1.0)) +
            -- Water recycling component (15% weight) - higher is better
            (15 * least(overall_water_recycling_pct / 100.0, 1.0)) +
            -- Efficiency component (10% weight) - higher is better
            (10 * avg_efficiency_rating) +
            -- Quality component (10% weight) - higher is better
            (10 * avg_quality_score)
        , 2) as sustainability_score
        
    from trend_analysis
)

select * from final 