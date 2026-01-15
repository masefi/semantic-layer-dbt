with sessions as (
    select * from {{ ref('fct_sessions') }}
),

orders as (
    select user_id, created_at, total_revenue from {{ ref('fct_orders') }}
),

session_revenue as (
    select
        s.session_id,
        s.traffic_source,
        s.session_start_at,
        s.total_events,
        s.has_purchase,
        coalesce(o.total_revenue, 0) as attribution_revenue
    from sessions s
    left join orders o 
        on s.user_id = o.user_id 
        and date(s.session_start_at) = date(o.created_at) -- Same day attribution
),

monthly as (
    select
        traffic_source,
        date_trunc(session_start_at, month) as event_month,
        
        count(*) as total_sessions,
        count(distinct session_id) as unique_users, -- Proxy if user_id is null? session_id is unique.
        countif(has_purchase) as conversions,
        sum(attribution_revenue) as revenue,
        countif(total_events = 1) as bounce_sessions,
        avg(total_events) as avg_events_per_session

    from session_revenue
    group by 1, 2
)

select
    *,
    safe_divide(conversions, total_sessions) as conversion_rate,
    safe_divide(revenue, total_sessions) as revenue_per_session,
    safe_divide(bounce_sessions, total_sessions) as bounce_rate
from monthly
order by event_month desc, revenue desc
