with order_items as (
    select * from {{ ref('stg_order_items') }}
),
orders as (
    select * from {{ ref('stg_orders') }}
),
products as (
    select * from {{ ref('stg_products') }}
),
users as (
    select * from {{ ref('stg_users') }}
)

select
    -- IDs
    oi.order_item_id,
    oi.order_id,
    oi.user_id,
    oi.product_id,
    p.distribution_center_id,
    
    -- Status & Timestamps
    o.status as order_status,
    o.created_at as order_created_at,
    o.shipped_at as order_shipped_at,
    o.delivered_at as order_delivered_at,
    o.returned_at as order_returned_at,
    date(o.created_at) as order_date,
    
    -- Financials
    oi.sale_price,
    p.cost,
    (oi.sale_price - p.cost) as item_profit,
    
    -- Details
    p.product_name,
    p.brand,
    p.category,
    p.department,
    p.retail_price as product_retail_price,
    
    -- User Context
    u.country as user_country,
    u.city as user_city,
    u.traffic_source as user_traffic_source,
    u.created_at as user_signup_at

from order_items oi
left join orders o on oi.order_id = o.order_id
left join products p on oi.product_id = p.product_id
left join users u on oi.user_id = u.user_id
