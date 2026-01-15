with sessions as (
    select * from {{ ref('fct_sessions') }}
),

daily as (
    select
        date(session_start_at) as event_date,
        traffic_source,
        
        count(*) as total_sessions,
        countif(page_views > 0) as sessions_with_product_view,
        countif(has_cart) as sessions_with_cart,
        countif(has_purchase) as sessions_with_purchase,
        avg(session_duration_seconds) as avg_session_duration

    from sessions
    group by 1, 2
)

select
    *,
    safe_divide(sessions_with_product_view, total_sessions) as product_view_rate,
    safe_divide(sessions_with_cart, total_sessions) as cart_rate,
    safe_divide(sessions_with_purchase, total_sessions) as purchase_rate,
    safe_divide(sessions_with_purchase, sessions_with_cart) as cart_to_purchase_rate
from daily
order by event_date desc, total_sessions desc
