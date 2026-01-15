with sessions as (
    select * from {{ ref('fct_sessions') }}
),

orders as (
    select user_id, created_at, total_revenue from {{ ref('fct_orders') }}
),

session_revenue as (
    select
        s.session_id,
        s.browser,
        s.session_start_at,
        s.has_purchase,
        coalesce(o.total_revenue, 0) as attribution_revenue
    from sessions s
    left join orders o 
        on s.user_id = o.user_id 
        and date(s.session_start_at) = date(o.created_at)
),

monthly as (
    select
        browser,
        date_trunc(session_start_at, month) as event_month,
        
        count(*) as total_sessions,
        countif(has_purchase) as conversions,
        sum(attribution_revenue) as revenue

    from session_revenue
    group by 1, 2
)

select
    *,
    safe_divide(conversions, total_sessions) as conversion_rate,
    safe_divide(revenue, total_sessions) as revenue_per_session
from monthly
order by event_month desc, revenue desc
