{{
    config(
        materialized='table'
    )
}}

with orders as (

    select * from {{ ref('stg_orders') }}

),

order_items_enriched as (

    select * from {{ ref('int_order_items_enriched') }}

),

users as (

    select * from {{ ref('stg_users') }}

),

order_metrics as (

    select
        order_id,
        sum(sale_price) as total_revenue,
        sum(item_profit) as total_profit,
        count(*) as line_item_count
    from order_items_enriched
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
        coalesce(m.total_revenue, 0) as total_revenue,
        coalesce(m.total_profit, 0) as total_profit,
        coalesce(m.line_item_count, 0) as line_item_count,
        
        -- Business logic
        row_number() over (partition by o.user_id order by o.created_at) = 1 as is_first_order
        
    from orders o
    left join order_metrics m on o.order_id = m.order_id
    left join users u on o.user_id = u.user_id

)

select * from final
