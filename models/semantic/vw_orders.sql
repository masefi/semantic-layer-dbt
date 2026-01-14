with source as (

    select * from {{ ref('fct_orders') }}

),

final as (

    select
        order_id,
        order_date,
        user_country,
        order_status,
        total_revenue as revenue,
        item_count
    from source
    where order_status not in ('Cancelled', 'Returned') -- Example business logic for public view

)

select * from final
