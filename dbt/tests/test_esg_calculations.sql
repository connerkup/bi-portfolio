-- Test that ESG batch-level calculations are consistent
with esg_validation as (
    select
        batch_id,
        batch_size,
        emissions_kg_co2,
        emissions_per_unit,
        round(emissions_kg_co2 / nullif(batch_size, 0), 6) as calculated_emissions_per_unit,
        abs(emissions_per_unit - round(emissions_kg_co2 / nullif(batch_size, 0), 6)) as difference
    from {{ ref('stg_esg_transactions') }}
),

esg_errors as (
    select
        batch_id,
        batch_size,
        emissions_kg_co2,
        emissions_per_unit,
        calculated_emissions_per_unit,
        difference
    from esg_validation
    where difference > 0.000001  -- Allow for small rounding differences
)

select *
from esg_errors 