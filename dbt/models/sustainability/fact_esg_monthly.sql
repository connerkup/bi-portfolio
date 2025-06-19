{{
  config(
    materialized='table',
    description='Monthly ESG metrics fact table for trend analysis'
  )
}}

with monthly_metrics as (
    select
        date_trunc('month', date) as month,
        product_line,
        facility,
        sum(emissions_kg_co2) as total_emissions_kg_co2,
        sum(energy_consumption_kwh) as total_energy_kwh,
        sum(water_usage_liters) as total_water_liters,
        avg(recycled_material_pct) as avg_recycled_material_pct,
        avg(virgin_material_pct) as avg_virgin_material_pct,
        sum(waste_generated_kg) as total_waste_kg,
        avg(recycling_rate_pct) as avg_recycling_rate_pct,
        -- Efficiency metrics
        avg(emissions_per_kwh) as avg_emissions_per_kwh,
        avg(waste_per_kwh) as avg_waste_per_kwh,
        -- Count of records for averaging
        count(*) as record_count
    from {{ ref('stg_esg_data') }}
    group by 1, 2, 3
),

monthly_totals as (
    select
        month,
        sum(total_emissions_kg_co2) as company_total_emissions,
        sum(total_energy_kwh) as company_total_energy,
        sum(total_water_liters) as company_total_water,
        sum(total_waste_kg) as company_total_waste
    from monthly_metrics
    group by 1
),

final as (
    select
        m.month,
        m.product_line,
        m.facility,
        m.total_emissions_kg_co2,
        m.total_energy_kwh,
        m.total_water_liters,
        m.avg_recycled_material_pct,
        m.avg_virgin_material_pct,
        m.total_waste_kg,
        m.avg_recycling_rate_pct,
        m.avg_emissions_per_kwh,
        m.avg_waste_per_kwh,
        -- Company totals for percentage calculations
        t.company_total_emissions,
        t.company_total_energy,
        t.company_total_water,
        t.company_total_waste,
        -- Percentage of company total
        round(m.total_emissions_kg_co2 / nullif(t.company_total_emissions, 0) * 100, 2) as emissions_pct_of_total,
        round(m.total_energy_kwh / nullif(t.company_total_energy, 0) * 100, 2) as energy_pct_of_total,
        round(m.total_waste_kg / nullif(t.company_total_waste, 0) * 100, 2) as waste_pct_of_total,
        -- Month-over-month change (will be calculated in BI tool)
        m.record_count
    from monthly_metrics m
    left join monthly_totals t on m.month = t.month
)

select * from final 