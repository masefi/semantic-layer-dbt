with fulfillment as (
    select * from {{ ref('fct_fulfillment') }}
),

agg as (
    select
        date_trunc(created_at, month) as order_month,
        
        count(*) as total_orders,
        countif(shipped_at is not null) as orders_shipped,
        countif(delivered_at is not null) as orders_delivered,
        countif(returned_at is not null) as orders_returned,
        
        avg(processing_hours) as avg_processing_hours,
        avg(shipping_hours) as avg_shipping_hours,
        avg(total_fulfillment_hours) as avg_total_fulfillment_hours,
        
        countif(is_shipped_same_day) as same_day_ships,
        countif(is_delivered_within_3_days) as delivered_3_days,
        countif(is_delivered_within_7_days) as delivered_7_days

    from fulfillment
    group by 1
)

select
    *,
    safe_divide(same_day_ships, orders_shipped) as pct_shipped_same_day,
    safe_divide(delivered_3_days, orders_delivered) as pct_delivered_within_3_days,
    safe_divide(delivered_7_days, orders_delivered) as pct_delivered_within_7_days,
    safe_divide(orders_returned, orders_delivered) as return_rate
from agg
order by order_month desc
