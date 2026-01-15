with source as (

    select * from {{ source('thelook_ecommerce', 'inventory_items') }}

),

renamed as (

    select
        id as inventory_item_id,
        product_id,
        cost,
        sold_at,
        created_at,
        product_category,
        product_name,
        product_brand,
        product_retail_price,
        product_department,
        product_sku,
        product_distribution_center_id,
        case when sold_at is not null then true else false end as is_sold
    from source

)

select * from renamed
