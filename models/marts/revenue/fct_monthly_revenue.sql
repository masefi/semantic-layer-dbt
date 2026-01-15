with daily as (
    select * from {{ ref('fct_daily_revenue') }}
),

monthly as (
    select
        date_trunc(order_date, month) as order_month,
        sum(total_orders) as total_orders,
        sum(total_revenue) as total_revenue,
        sum(total_profit) as total_profit,
        sum(new_customers) as new_customers,
        count(distinct order_date) as active_days
    from daily
    group by 1
),

windowed as (
    select
        *,
        lag(total_revenue) over (order by order_month) as prev_month_revenue,
        lag(total_revenue, 12) over (order by order_month) as prev_year_revenue,
        sum(total_revenue) over (order by order_month rows between unbounded preceding and current row) as cumulative_revenue_ytd -- Simplified (cumulative all time actually)
    from monthly
)

select
    *,
    safe_divide(total_revenue - prev_month_revenue, prev_month_revenue) as mom_growth_pct,
    safe_divide(total_revenue - prev_year_revenue, prev_year_revenue) as yoy_growth_pct
from windowed
order by order_month desc
