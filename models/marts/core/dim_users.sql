{{
    config(
        materialized='table'
    )
}}

with users as (

    select * from {{ ref('stg_users') }}

),

orders as (

    select * from {{ ref('stg_orders') }}

),

user_first_order as (

    select
        user_id,
        min(created_at) as first_order_at,
        count(*) as total_orders
    from orders
    group by user_id

),

final as (

    select
        u.user_id,
        u.first_name,
        u.last_name,
        u.email,
        u.age,
        u.gender,
        u.city,
        u.state,
        u.country,
        u.postal_code,
        u.traffic_source,
        u.created_at as user_created_at,
        fo.first_order_at,
        coalesce(fo.total_orders, 0) as total_orders
    from users u
    left join user_first_order fo on u.user_id = fo.user_id

)

select * from final
