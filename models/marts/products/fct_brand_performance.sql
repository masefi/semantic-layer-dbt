with items as (
    select * from {{ ref('int_order_items_enriched') }}
),

monthly as (
    select
        brand,
        date_trunc(order_created_at, month) as order_month,
        
        count(*) as total_units_sold,
        sum(sale_price) as total_revenue,
        sum(item_profit) as total_profit,
        avg(sale_price) as avg_sale_price,
        count(distinct order_id) as order_count,
        count(distinct user_id) as unique_customers,
        count(distinct product_id) as distinct_products_sold,
        countif(order_status = 'Returned') as items_returned

    from items
    where order_status not in ('Cancelled')
    group by 1, 2
)

select
    *,
    safe_divide(items_returned, total_units_sold) as return_rate,
    rank() over (partition by order_month order by total_revenue desc) as brand_rank_by_revenue
from monthly
order by order_month desc, total_revenue desc
