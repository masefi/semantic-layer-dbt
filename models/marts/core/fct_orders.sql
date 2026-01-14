{{
    config(
        materialized='table'
    )
}}

with orders as (

    select * from {{ ref('stg_orders') }}

),

order_items as (

    select * from {{ ref('stg_order_items') }}

),

users as (

    select * from {{ ref('stg_users') }}

),

order_revenue as (

    select
        order_id,
        sum(sale_price) as total_revenue,
        count(*) as line_item_count
    from order_items
    group by order_id

),

final as (

    select
        o.order_id,
        o.user_id,
        u.country as user_country,
        u.city as user_city,
        o.status as order_status,
        date(o.created_at) as order_date,
        o.created_at as order_created_at,
        o.shipped_at,
        o.delivered_at,
        o.returned_at,
        o.item_count,
        coalesce(r.total_revenue, 0) as total_revenue,
        coalesce(r.line_item_count, 0) as line_item_count
    from orders o
    left join order_revenue r on o.order_id = r.order_id
    left join users u on o.user_id = u.user_id

)

select * from final
