with items as (
    select * from {{ ref('int_order_items_enriched') }}
),

returns as (
    select
        product_id,
        product_name,
        brand,
        category,
        department,
        
        count(distinct order_id) as total_orders,
        count(order_item_id) as total_units_sold,
        sum(sale_price) as total_revenue,
        
        countif(order_status = 'Returned') as returned_orders,
        countif(order_status = 'Returned') as returned_units, -- item level
        
        sum(case when order_status = 'Returned' then sale_price else 0 end) as revenue_lost_to_returns,
        
        avg(case when order_status = 'Returned' then 
            timestamp_diff(order_returned_at, order_delivered_at, day) 
        end) as avg_days_to_return

    from items
    group by 1, 2, 3, 4, 5
)

select
    *,
    safe_divide(returned_orders, total_orders) as return_rate
from returns
where total_orders >= 10
order by return_rate desc
