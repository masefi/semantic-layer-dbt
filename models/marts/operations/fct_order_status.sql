with orders as (
    select * from {{ ref('fct_orders') }}
),

monthly as (
    select
        date_trunc(created_at, month) as order_month,
        count(*) as total_month_orders,
        sum(total_revenue) as total_month_revenue
    from orders
    group by 1
),

status_grouped as (
    select
        date_trunc(created_at, month) as order_month,
        status as order_status,
        count(*) as order_count,
        sum(item_count) as item_count,
        sum(total_revenue) as revenue
    from orders
    group by 1, 2
)

select
    s.order_month,
    s.order_status,
    s.order_count,
    s.item_count,
    s.revenue,
    
    -- Funnel %
    safe_divide(s.order_count, m.total_month_orders) as pct_of_month_orders,
    safe_divide(s.revenue, m.total_month_revenue) as pct_of_month_revenue,
    
    safe_divide(s.revenue, s.order_count) as avg_order_value

from status_grouped s
join monthly m on s.order_month = m.order_month
order by 1 desc, 3 desc
