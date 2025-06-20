-- Test that material percentages sum to 100% in ESG data
with material_validation as (
    select
        batch_id,
        recycled_material_pct,
        virgin_material_pct,
        (recycled_material_pct + virgin_material_pct) as total_material_pct,
        abs((recycled_material_pct + virgin_material_pct) - 100) as difference
    from {{ ref('stg_esg_transactions') }}
),

material_errors as (
    select
        batch_id,
        recycled_material_pct,
        virgin_material_pct,
        total_material_pct,
        difference
    from material_validation
    where difference > 1  -- Allow for small rounding differences
)

select *
from material_errors 