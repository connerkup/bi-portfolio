{{
  config(
    materialized='table',
    description='ESG summary mart for dashboard insights and KPI tracking'
  )
}}

with esg_monthly as (
    select * from {{ ref('fact_esg_monthly') }}
),

-- Latest month summary
latest_summary as (
    select
        'Latest Month' as period_type,
        date,
        year,
        month,
        quarter,
        
        -- Overall company metrics
        sum(total_emissions_kg_co2) as total_emissions_kg_co2,
        sum(total_energy_consumption_kwh) as total_energy_consumption_kwh,
        sum(total_water_usage_liters) as total_water_usage_liters,
        sum(total_waste_generated_kg) as total_waste_generated_kg,
        sum(total_batch_size) as total_production_units,
        
        -- Average sustainability metrics
        avg(avg_recycled_material_pct) as avg_recycled_material_pct,
        avg(avg_renewable_energy_pct) as avg_renewable_energy_pct,
        avg(overall_water_recycling_pct) as avg_water_recycling_pct,
        avg(sustainability_score) as avg_sustainability_score,
        
        -- Performance indicators
        avg(overall_emissions_per_unit) as avg_emissions_per_unit,
        avg(overall_energy_per_unit) as avg_energy_per_unit,
        avg(overall_water_per_unit) as avg_water_per_unit,
        avg(overall_waste_per_unit) as avg_waste_per_unit,
        
        -- Risk assessment
        count(case when sustainability_risk_level = 'High Risk' then 1 end) as high_risk_facilities,
        count(case when sustainability_risk_level = 'Medium Risk' then 1 end) as medium_risk_facilities,
        count(case when sustainability_risk_level = 'Low Risk' then 1 end) as low_risk_facilities,
        
        -- Trend indicators
        count(case when emissions_trend = 'Improving' then 1 end) as improving_emissions_facilities,
        count(case when emissions_trend = 'Declining' then 1 end) as declining_emissions_facilities,
        count(case when recycled_content_trend = 'Improving' then 1 end) as improving_recycled_facilities,
        count(case when renewable_energy_trend = 'Improving' then 1 end) as improving_renewable_facilities,
        
        -- Benchmark performance
        count(case when emissions_benchmark = 'Industry Leader' then 1 end) as industry_leader_emissions,
        count(case when recycled_content_benchmark = 'Industry Leader' then 1 end) as industry_leader_recycled,
        count(case when renewable_energy_benchmark = 'Industry Leader' then 1 end) as industry_leader_renewable,
        
        -- Total facilities
        count(distinct facility) as total_facilities
        
    from esg_monthly
    where date = (select max(date) from esg_monthly)
    group by 1, 2, 3, 4, 5
),

-- Year-to-date summary
ytd_summary as (
    select
        'Year to Date' as period_type,
        date_trunc('year', date) as date,
        year,
        null as month,
        null as quarter,
        
        -- Overall company metrics
        sum(total_emissions_kg_co2) as total_emissions_kg_co2,
        sum(total_energy_consumption_kwh) as total_energy_consumption_kwh,
        sum(total_water_usage_liters) as total_water_usage_liters,
        sum(total_waste_generated_kg) as total_waste_generated_kg,
        sum(total_batch_size) as total_production_units,
        
        -- Average sustainability metrics
        avg(avg_recycled_material_pct) as avg_recycled_material_pct,
        avg(avg_renewable_energy_pct) as avg_renewable_energy_pct,
        avg(overall_water_recycling_pct) as avg_water_recycling_pct,
        avg(sustainability_score) as avg_sustainability_score,
        
        -- Performance indicators
        avg(overall_emissions_per_unit) as avg_emissions_per_unit,
        avg(overall_energy_per_unit) as avg_energy_per_unit,
        avg(overall_water_per_unit) as avg_water_per_unit,
        avg(overall_waste_per_unit) as avg_waste_per_unit,
        
        -- Risk assessment
        count(case when sustainability_risk_level = 'High Risk' then 1 end) as high_risk_facilities,
        count(case when sustainability_risk_level = 'Medium Risk' then 1 end) as medium_risk_facilities,
        count(case when sustainability_risk_level = 'Low Risk' then 1 end) as low_risk_facilities,
        
        -- Trend indicators
        count(case when emissions_trend = 'Improving' then 1 end) as improving_emissions_facilities,
        count(case when emissions_trend = 'Declining' then 1 end) as declining_emissions_facilities,
        count(case when recycled_content_trend = 'Improving' then 1 end) as improving_recycled_facilities,
        count(case when renewable_energy_trend = 'Improving' then 1 end) as improving_renewable_facilities,
        
        -- Benchmark performance
        count(case when emissions_benchmark = 'Industry Leader' then 1 end) as industry_leader_emissions,
        count(case when recycled_content_benchmark = 'Industry Leader' then 1 end) as industry_leader_recycled,
        count(case when renewable_energy_benchmark = 'Industry Leader' then 1 end) as industry_leader_renewable,
        
        -- Total facilities
        count(distinct facility) as total_facilities
        
    from esg_monthly
    where year = (select max(year) from esg_monthly)
    group by 1, 2, 3, 4, 5
),

-- Facility performance ranking
facility_ranking as (
    select
        facility,
        facility_region,
        technology_level,
        sustainability_score,
        overall_emissions_per_unit,
        avg_recycled_material_pct,
        avg_renewable_energy_pct,
        sustainability_risk_level,
        emissions_trend,
        recycled_content_trend,
        renewable_energy_trend,
        row_number() over (order by sustainability_score desc) as sustainability_rank,
        row_number() over (order by overall_emissions_per_unit asc) as emissions_rank,
        row_number() over (order by avg_recycled_material_pct desc) as recycled_rank,
        row_number() over (order by avg_renewable_energy_pct desc) as renewable_rank
    from esg_monthly
    where date = (select max(date) from esg_monthly)
),

-- Product line performance
product_performance as (
    select
        product_line,
        sum(total_emissions_kg_co2) as total_emissions_kg_co2,
        sum(total_energy_consumption_kwh) as total_energy_consumption_kwh,
        sum(total_water_usage_liters) as total_water_usage_liters,
        sum(total_waste_generated_kg) as total_waste_generated_kg,
        sum(total_batch_size) as total_production_units,
        avg(avg_recycled_material_pct) as avg_recycled_material_pct,
        avg(avg_renewable_energy_pct) as avg_renewable_energy_pct,
        avg(sustainability_score) as avg_sustainability_score,
        avg(overall_emissions_per_unit) as avg_emissions_per_unit,
        count(distinct facility) as facilities_count,
        row_number() over (order by avg_sustainability_score desc) as sustainability_rank,
        row_number() over (order by avg_emissions_per_unit asc) as emissions_rank
    from esg_monthly
    where date = (select max(date) from esg_monthly)
    group by 1
),

-- Combine all summaries
final as (
    select 
        period_type,
        date,
        year,
        month,
        quarter,
        total_emissions_kg_co2,
        total_energy_consumption_kwh,
        total_water_usage_liters,
        total_waste_generated_kg,
        total_production_units,
        avg_recycled_material_pct,
        avg_renewable_energy_pct,
        avg_water_recycling_pct,
        avg_sustainability_score,
        avg_emissions_per_unit,
        avg_energy_per_unit,
        avg_water_per_unit,
        avg_waste_per_unit,
        high_risk_facilities,
        medium_risk_facilities,
        low_risk_facilities,
        improving_emissions_facilities,
        declining_emissions_facilities,
        improving_recycled_facilities,
        improving_renewable_facilities,
        industry_leader_emissions,
        industry_leader_recycled,
        industry_leader_renewable,
        total_facilities,
        -- Calculated metrics
        round(high_risk_facilities * 100.0 / nullif(total_facilities, 0), 1) as high_risk_pct,
        round(improving_emissions_facilities * 100.0 / nullif(total_facilities, 0), 1) as improving_emissions_pct,
        round(industry_leader_emissions * 100.0 / nullif(total_facilities, 0), 1) as industry_leader_emissions_pct,
        round(industry_leader_recycled * 100.0 / nullif(total_facilities, 0), 1) as industry_leader_recycled_pct,
        round(industry_leader_renewable * 100.0 / nullif(total_facilities, 0), 1) as industry_leader_renewable_pct
    from latest_summary
    
    union all
    
    select 
        period_type,
        date,
        year,
        month,
        quarter,
        total_emissions_kg_co2,
        total_energy_consumption_kwh,
        total_water_usage_liters,
        total_waste_generated_kg,
        total_production_units,
        avg_recycled_material_pct,
        avg_renewable_energy_pct,
        avg_water_recycling_pct,
        avg_sustainability_score,
        avg_emissions_per_unit,
        avg_energy_per_unit,
        avg_water_per_unit,
        avg_waste_per_unit,
        high_risk_facilities,
        medium_risk_facilities,
        low_risk_facilities,
        improving_emissions_facilities,
        declining_emissions_facilities,
        improving_recycled_facilities,
        improving_renewable_facilities,
        industry_leader_emissions,
        industry_leader_recycled,
        industry_leader_renewable,
        total_facilities,
        -- Calculated metrics
        round(high_risk_facilities * 100.0 / nullif(total_facilities, 0), 1) as high_risk_pct,
        round(improving_emissions_facilities * 100.0 / nullif(total_facilities, 0), 1) as improving_emissions_pct,
        round(industry_leader_emissions * 100.0 / nullif(total_facilities, 0), 1) as industry_leader_emissions_pct,
        round(industry_leader_recycled * 100.0 / nullif(total_facilities, 0), 1) as industry_leader_recycled_pct,
        round(industry_leader_renewable * 100.0 / nullif(total_facilities, 0), 1) as industry_leader_renewable_pct
    from ytd_summary
)

select * from final 