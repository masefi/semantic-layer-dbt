with orders as (
    select * from {{ ref('stg_orders') }} -- Use staging for timestamps
),

fct_orders as (
    select order_id, total_revenue, item_count from {{ ref('fct_orders') }}
),

computed as (
    select
        o.order_id,
        o.user_id,
        o.status,
        o.created_at,
        o.shipped_at,
        o.delivered_at,
        o.returned_at,
        
        f.total_revenue,
        f.item_count,
        
        -- Timing (Hours)
        timestamp_diff(o.shipped_at, o.created_at, hour) as processing_hours,
        timestamp_diff(o.delivered_at, o.shipped_at, hour) as shipping_hours,
        timestamp_diff(o.delivered_at, o.created_at, hour) as total_fulfillment_hours,
        
        -- SLAs
        timestamp_diff(o.shipped_at, o.created_at, day) = 0 as is_shipped_same_day,
        timestamp_diff(o.delivered_at, o.created_at, day) <= 3 as is_delivered_within_3_days,
        timestamp_diff(o.delivered_at, o.created_at, day) <= 7 as is_delivered_within_7_days

    from orders o
    left join fct_orders f on o.order_id = f.order_id
)

select * from computed
