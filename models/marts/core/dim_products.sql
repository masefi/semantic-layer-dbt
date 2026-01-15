with products as (

    select * from {{ ref('stg_products') }}

),

calculated as (

    select
        product_id,
        product_name,
        brand,
        category,
        department,
        cost,
        retail_price,
        sku,
        distribution_center_id,
        
        -- Margin Analysis
        (retail_price - cost) as margin_amount,
        safe_divide((retail_price - cost), retail_price) as margin_percentage,
        
        -- Price Tiering (Quartiles)
        ntile(4) over (order by retail_price) as price_quartile

    from products

),

final as (

    select
        *,
        -- Margin Segments
        case
            when margin_percentage < 0.20 then 'Low'
            when margin_percentage >= 0.20 and margin_percentage < 0.40 then 'Medium'
            else 'High'
        end as margin_tier,
        
        -- Price Labels
        case 
            when price_quartile = 1 then 'Budget'
            when price_quartile = 2 then 'Mid-Range'
            when price_quartile = 3 then 'Premium'
            else 'Luxury'
        end as price_tier
        
    from calculated

)

select * from final
