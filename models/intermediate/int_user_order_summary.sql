with enriched_items as (
    select * from {{ ref('int_order_items_enriched') }}
),

user_agg as (
    select
        user_id,
        count(distinct order_id) as total_orders,
        sum(sale_price) as total_revenue,
        sum(item_profit) as total_profit,
        count(*) as total_items,
        min(order_created_at) as first_order_at,
        max(order_created_at) as last_order_at,
        countif(order_status = 'Returned') as total_returns
    from enriched_items
    group by 1
)

select * from user_agg
