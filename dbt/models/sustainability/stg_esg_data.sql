{{
  config(
    materialized='table',
    description='Staged ESG data from raw CSV files'
  )
}}

with source as (
    select * from {{ ref('sample_esg_data') }}
),

cleaned as (
    select
        date,
        product_line,
        facility,
        emissions_kg_co2,
        energy_consumption_kwh,
        water_usage_liters,
        recycled_material_pct,
        virgin_material_pct,
        waste_generated_kg,
        recycling_rate_pct,
        -- Add calculated fields
        round(emissions_kg_co2 / nullif(energy_consumption_kwh, 0), 4) as emissions_per_kwh,
        round(waste_generated_kg / nullif(energy_consumption_kwh, 0), 4) as waste_per_kwh,
        -- Add date parts for analysis
        extract(year from date) as year,
        extract(month from date) as month,
        extract(quarter from date) as quarter
    from source
    where date is not null
      and product_line is not null
      and facility is not null
)

select * from cleaned 