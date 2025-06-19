{{
  config(
    materialized='table',
    description='Monthly financial metrics fact table for analysis and forecasting'
  )
}}

with monthly_metrics as (
    select
        date_trunc('month', date) as month,
        product_line,
        region,
        customer_segment,
        sum(units_sold) as total_units_sold,
        sum(revenue) as total_revenue,
        sum(cost_of_goods) as total_cost_of_goods,
        sum(operating_cost) as total_operating_cost,
        sum(profit_margin) as total_profit_margin,
        sum(gross_profit) as total_gross_profit,
        -- Average metrics
        avg(gross_margin_pct) as avg_gross_margin_pct,
        avg(net_margin_pct) as avg_net_margin_pct,
        avg(cost_per_unit) as avg_cost_per_unit,
        avg(revenue_per_unit) as avg_revenue_per_unit,
        -- Count of records for averaging
        count(*) as record_count
    from {{ ref('stg_sales_data') }}
    group by 1, 2, 3, 4
),

monthly_totals as (
    select
        month,
        sum(total_revenue) as company_total_revenue,
        sum(total_cost_of_goods) as company_total_cogs,
        sum(total_operating_cost) as company_total_opex,
        sum(total_profit_margin) as company_total_profit,
        sum(total_units_sold) as company_total_units
    from monthly_metrics
    group by 1
),

final as (
    select
        m.month,
        m.product_line,
        m.region,
        m.customer_segment,
        m.total_units_sold,
        m.total_revenue,
        m.total_cost_of_goods,
        m.total_operating_cost,
        m.total_profit_margin,
        m.total_gross_profit,
        m.avg_gross_margin_pct,
        m.avg_net_margin_pct,
        m.avg_cost_per_unit,
        m.avg_revenue_per_unit,
        -- Company totals for percentage calculations
        t.company_total_revenue,
        t.company_total_cogs,
        t.company_total_opex,
        t.company_total_profit,
        t.company_total_units,
        -- Percentage of company total
        round(m.total_revenue / nullif(t.company_total_revenue, 0) * 100, 2) as revenue_pct_of_total,
        round(m.total_profit_margin / nullif(t.company_total_profit, 0) * 100, 2) as profit_pct_of_total,
        round(m.total_units_sold / nullif(t.company_total_units, 0) * 100, 2) as units_pct_of_total,
        -- Company-level margins
        round((t.company_total_revenue - t.company_total_cogs) / nullif(t.company_total_revenue, 0) * 100, 2) as company_gross_margin_pct,
        round(t.company_total_profit / nullif(t.company_total_revenue, 0) * 100, 2) as company_net_margin_pct,
        m.record_count
    from monthly_metrics m
    left join monthly_totals t on m.month = t.month
)

select * from final 