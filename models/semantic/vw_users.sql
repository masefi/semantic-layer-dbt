with users as (
    select * from {{ ref('dim_users') }}
),

orders as (
    select * from {{ ref('fct_customer_orders') }}
),

final as (
    select
        u.user_id,
        u.country,
        u.city,
        u.age,
        u.gender,
        coalesce(o.total_orders, 0) as total_orders,
        o.first_order_date as first_order_at,
        coalesce(o.total_revenue, 0) as lifetime_revenue
    from users u
    left join orders o on u.user_id = o.user_id
)

select * from final
