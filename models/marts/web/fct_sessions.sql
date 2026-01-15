with events as (
    select * from {{ ref('stg_events') }}
),

session_agg as (
    select
        session_id,
        user_id,
        min(created_at) as session_start_at,
        max(created_at) as session_end_at,
        count(*) as total_events,
        countif(event_type in ('product', 'home', 'department')) as page_views,
        
        -- Dimensions (First value approach or max)
        max(browser) as browser,
        max(traffic_source) as traffic_source,
        max(city) as city,
        max(state) as state,
        
        -- Conversion Flags
        countif(event_type = 'cart') > 0 as has_cart,
        countif(event_type = 'purchase') > 0 as has_purchase,
        countif(event_type = 'cancel') > 0 as has_cancel

    from events
    group by 1, 2
)

select
    *,
    timestamp_diff(session_end_at, session_start_at, second) as session_duration_seconds
from session_agg
