{{
  config(
    materialized='table',
    description='ESG summary mart for dashboard insights and KPI tracking'
  )
}}

with esg_monthly as (
    select * from {{ ref('fact_esg_monthly') }}
),

-- Pre-calculate company-wide averages for the latest month
overall_averages as (
    select
        max(date) as latest_date,
        avg(overall_emissions_per_unit) as avg_emissions_per_unit,
        avg(avg_recycled_material_pct) as avg_recycled_material_pct,
        avg(avg_renewable_energy_pct) as avg_renewable_energy_pct
    from esg_monthly
    where date = (select max(date) from esg_monthly)
),

-- Latest month summary
latest_summary as (
    select
        'Latest Month' as period_type,
        e.date,
        e.year,
        e.month,
        e.quarter,
        
        -- Overall company metrics
        sum(e.total_emissions_kg_co2) as total_emissions_kg_co2,
        sum(e.total_energy_consumption_kwh) as total_energy_consumption_kwh,
        sum(e.total_water_usage_liters) as total_water_usage_liters,
        sum(e.total_waste_generated_kg) as total_waste_generated_kg,
        sum(e.total_batch_size) as total_production_units,
        
        -- Average sustainability metrics
        avg(e.avg_recycled_material_pct) as avg_recycled_material_pct,
        avg(e.avg_renewable_energy_pct) as avg_renewable_energy_pct,
        avg(e.overall_water_recycling_pct) as avg_water_recycling_pct,
        avg(e.sustainability_score) as avg_sustainability_score,
        
        -- Performance indicators
        avg(e.overall_emissions_per_unit) as avg_emissions_per_unit,
        avg(e.overall_energy_per_unit) as avg_energy_per_unit,
        avg(e.overall_water_per_unit) as avg_water_per_unit,
        avg(e.overall_waste_per_unit) as avg_waste_per_unit,
        
        -- Risk assessment based on sustainability score
        count(case when e.sustainability_score < 30 then 1 end) as high_risk_facilities,
        count(case when e.sustainability_score >= 30 and e.sustainability_score < 70 then 1 end) as medium_risk_facilities,
        count(case when e.sustainability_score >= 70 then 1 end) as low_risk_facilities,
        
        -- Performance indicators based on pre-calculated averages
        count(case when e.overall_emissions_per_unit < a.avg_emissions_per_unit then 1 end) as below_avg_emissions_facilities,
        count(case when e.avg_recycled_material_pct > a.avg_recycled_material_pct then 1 end) as above_avg_recycled_facilities,
        count(case when e.avg_renewable_energy_pct > a.avg_renewable_energy_pct then 1 end) as above_avg_renewable_facilities,
        
        -- Total facilities
        count(distinct e.facility) as total_facilities
        
    from esg_monthly e
    cross join overall_averages a
    where e.date = a.latest_date
    group by 1, 2, 3, 4, 5
),

-- Pre-calculate company-wide averages for the latest year
ytd_averages as (
    select
        max(year) as latest_year,
        avg(overall_emissions_per_unit) as avg_emissions_per_unit,
        avg(avg_recycled_material_pct) as avg_recycled_material_pct,
        avg(avg_renewable_energy_pct) as avg_renewable_energy_pct
    from esg_monthly
    where year = (select max(year) from esg_monthly)
),

-- Year-to-date summary
ytd_summary as (
    select
        'Year to Date' as period_type,
        date_trunc('year', e.date) as date,
        e.year,
        null as month,
        null as quarter,
        
        -- Overall company metrics
        sum(e.total_emissions_kg_co2) as total_emissions_kg_co2,
        sum(e.total_energy_consumption_kwh) as total_energy_consumption_kwh,
        sum(e.total_water_usage_liters) as total_water_usage_liters,
        sum(e.total_waste_generated_kg) as total_waste_generated_kg,
        sum(e.total_batch_size) as total_production_units,
        
        -- Average sustainability metrics
        avg(e.avg_recycled_material_pct) as avg_recycled_material_pct,
        avg(e.avg_renewable_energy_pct) as avg_renewable_energy_pct,
        avg(e.overall_water_recycling_pct) as avg_water_recycling_pct,
        avg(e.sustainability_score) as avg_sustainability_score,
        
        -- Performance indicators
        avg(e.overall_emissions_per_unit) as avg_emissions_per_unit,
        avg(e.overall_energy_per_unit) as avg_energy_per_unit,
        avg(e.overall_water_per_unit) as avg_water_per_unit,
        avg(e.overall_waste_per_unit) as avg_waste_per_unit,
        
        -- Risk assessment based on sustainability score
        count(case when e.sustainability_score < 30 then 1 end) as high_risk_facilities,
        count(case when e.sustainability_score >= 30 and e.sustainability_score < 70 then 1 end) as medium_risk_facilities,
        count(case when e.sustainability_score >= 70 then 1 end) as low_risk_facilities,
        
        -- Performance indicators based on pre-calculated averages
        count(case when e.overall_emissions_per_unit < a.avg_emissions_per_unit then 1 end) as below_avg_emissions_facilities,
        count(case when e.avg_recycled_material_pct > a.avg_recycled_material_pct then 1 end) as above_avg_recycled_facilities,
        count(case when e.avg_renewable_energy_pct > a.avg_renewable_energy_pct then 1 end) as above_avg_renewable_facilities,
        
        -- Total facilities
        count(distinct e.facility) as total_facilities
        
    from esg_monthly e
    cross join ytd_averages a
    where e.year = a.latest_year
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
        below_avg_emissions_facilities,
        above_avg_recycled_facilities,
        above_avg_renewable_facilities,
        total_facilities,
        -- Calculated metrics
        round(high_risk_facilities * 100.0 / nullif(total_facilities, 0), 1) as high_risk_pct,
        round(below_avg_emissions_facilities * 100.0 / nullif(total_facilities, 0), 1) as below_avg_emissions_pct,
        round(above_avg_recycled_facilities * 100.0 / nullif(total_facilities, 0), 1) as above_avg_recycled_pct,
        round(above_avg_renewable_facilities * 100.0 / nullif(total_facilities, 0), 1) as above_avg_renewable_pct
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
        below_avg_emissions_facilities,
        above_avg_recycled_facilities,
        above_avg_renewable_facilities,
        total_facilities,
        -- Calculated metrics
        round(high_risk_facilities * 100.0 / nullif(total_facilities, 0), 1) as high_risk_pct,
        round(below_avg_emissions_facilities * 100.0 / nullif(total_facilities, 0), 1) as below_avg_emissions_pct,
        round(above_avg_recycled_facilities * 100.0 / nullif(total_facilities, 0), 1) as above_avg_recycled_pct,
        round(above_avg_renewable_facilities * 100.0 / nullif(total_facilities, 0), 1) as above_avg_renewable_pct
    from ytd_summary
)

select * from final 