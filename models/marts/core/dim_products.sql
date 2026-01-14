{{
    config(
        materialized='table'
    )
}}

with products as (

    select * from {{ ref('stg_products') }}

),

final as (

    select
        product_id,
        product_name,
        brand,
        category,
        department,
        sku,
        retail_price,
        cost,
        retail_price - cost as profit_margin
    from products

)

select * from final
