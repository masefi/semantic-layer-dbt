with source as (

    select * from {{ ref('dim_users') }}

),

final as (

    select
        user_id,
        country,
        city,
        total_orders,
        first_order_at
    from source

)

select * from final
