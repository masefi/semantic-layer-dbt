with user_summary as (

    select * from {{ ref('int_user_order_summary') }}

),

users as (

    select * from {{ ref('dim_users') }}

),

final as (

    select
        u.user_id,
        
        -- Lifetime Metrics
        s.first_order_at,
        s.last_order_at,
        date_diff(date(s.last_order_at), date(s.first_order_at), day) as customer_lifespan_days,
        date_diff(current_date, date(s.last_order_at), day) as days_since_last_order,
        
        s.total_orders,
        s.total_revenue,
        s.total_profit,
        s.total_items,
        
        -- Returns
        s.total_returns,
        safe_divide(s.total_returns, s.total_orders) as return_rate,
        
        -- Averages
        safe_divide(s.total_revenue, s.total_orders) as avg_order_value,
        safe_divide(s.total_items, s.total_orders) as avg_items_per_order,
        
        -- Segmentation
        case
            when s.total_orders = 1 then 'New'
            when s.total_orders between 2 and 5 then 'Repeat'
            else 'Loyal'
        end as customer_status,
        
        u.signup_cohort,
        u.age_group,
        u.country

    from user_summary s
    left join users u on s.user_id = u.user_id

)

select * from final
