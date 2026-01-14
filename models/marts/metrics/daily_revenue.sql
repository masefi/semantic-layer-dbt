{{
    config(
        materialized='table'
    )
}}

with orders as (

    select * from {{ ref('fct_orders') }}

),

daily_metrics as (

    select
        order_date,
        count(distinct order_id) as order_count,
        sum(total_revenue) as total_revenue,
        sum(item_count) as total_items_sold,
        avg(total_revenue) as avg_order_value
    from orders
    where order_status not in ('Cancelled', 'Returned')
    group by order_date

)

select * from daily_metrics
order by order_date
