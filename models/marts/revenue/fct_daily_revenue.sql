with orders as (
    select * from {{ ref('fct_orders') }}
),

daily as (
    select
        date(created_at) as order_date,
        
        count(*) as total_orders,
        sum(item_count) as total_items,
        sum(total_revenue) as total_revenue,
        sum(total_profit) as total_profit,
        
        count(distinct user_id) as unique_customers,
        count(distinct case when is_first_order then user_id end) as new_customers,
        
        countif(status = 'Returned') as orders_returned,
        countif(status = 'Cancelled') as orders_cancelled

    from orders
    group by 1
)

select
    *,
    unique_customers - new_customers as repeat_customers,
    safe_divide(total_revenue, total_orders) as avg_order_value,
    safe_divide(orders_returned, total_orders) as return_rate
from daily
