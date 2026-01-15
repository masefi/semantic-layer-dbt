with items as (
    select * from {{ ref('int_order_items_enriched') }}
),

dcs as (
    select * from {{ ref('dim_distribution_centers') }}
),

monthly as (
    select
        distribution_center_id,
        date_trunc(order_created_at, month) as order_month,
        
        count(order_item_id) as items_shipped,
        sum(sale_price) as total_revenue,
        count(distinct product_id) as unique_products,
        
        avg(timestamp_diff(order_shipped_at, order_created_at, hour)) as avg_processing_hours,
        countif(order_status = 'Returned') as items_returned

    from items
    where order_status not in ('Cancelled')
    group by 1, 2
)

select
    m.*,
    d.distribution_center_name,
    d.latitude,
    d.longitude,
    safe_divide(m.items_returned, m.items_shipped) as return_rate
from monthly m
join dcs d on m.distribution_center_id = d.distribution_center_id
order by m.order_month desc, m.total_revenue desc
