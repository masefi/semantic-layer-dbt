with source as (

    select * from {{ ref('daily_revenue') }}

),

final as (

    select
        order_date,
        total_revenue as daily_revenue,
        order_count,
        avg_order_value
    from source

)

select * from final
