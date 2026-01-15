with orders as (
    select * from {{ ref('fct_orders') }}
),

monthly as (
    select
        user_country as country,
        date_trunc(created_at, month) as order_month,
        
        count(*) as total_orders,
        sum(total_revenue) as total_revenue,
        sum(total_profit) as total_profit,
        count(distinct user_id) as unique_customers,
        avg(total_revenue) as avg_order_value

    from orders
    group by 1, 2
)

select 
    *,
    rank() over (partition by order_month order by total_revenue desc) as country_rank
from monthly
order by order_month desc, total_revenue desc
