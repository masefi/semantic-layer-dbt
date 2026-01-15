with items as (
    select * from {{ ref('int_order_items_enriched') }}
),

agg as (
    select
        product_id,
        product_name,
        brand,
        category,
        department,
        product_retail_price,
        cost,
        
        -- Sales Metrics
        count(order_item_id) as total_units_sold,
        sum(sale_price) as total_revenue,
        sum(item_profit) as total_profit,
        count(distinct order_id) as total_orders_containing,
        avg(sale_price) as avg_sale_price,
        
        -- Dates
        min(order_created_at) as first_sold_at,
        max(order_created_at) as last_sold_at,
        
        -- Returns
        countif(order_status = 'Returned') as units_returned,
        sum(case when order_status = 'Returned' then sale_price else 0 end) as revenue_lost_to_returns
        
    from items
    where order_status not in ('Cancelled') -- Exclude cancelled from sales performance? Prompt says "Only include products with 1 sale".
    group by 1, 2, 3, 4, 5, 6, 7
)

select
    *,
    safe_divide(units_returned, total_units_sold) as return_rate,
    safe_divide(total_profit, total_revenue) as profit_margin_pct,
    date_diff(current_date, date(last_sold_at), day) as days_since_last_sale
from agg
where total_units_sold > 0
