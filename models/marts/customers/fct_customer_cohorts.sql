with users as (
    select * from {{ ref('dim_users') }}
),

months as (
    select distinct 
        date_trunc(date_key, month) as activity_month
    from {{ ref('dim_date') }}
),

user_months as (
    select 
        u.user_id,
        u.signup_cohort,
        m.activity_month
    from users u
    cross join months m
    where m.activity_month >= date_trunc(u.created_at, month)
      and m.activity_month <= date_trunc(current_date, month)
),

orders as (
    select 
        user_id, 
        date_trunc(created_at, month) as order_month,
        count(*) as monthly_orders,
        sum(item_count) as monthly_items,
        Coalesce(sum(total_revenue), 0) as monthly_revenue
    from {{ ref('fct_orders') }}
    group by 1, 2
),

joined as (
    select
        um.user_id,
        um.signup_cohort,
        um.activity_month,
        date_diff(um.activity_month, date_trunc(u.created_at, month), month) as months_since_signup,
        
        coalesce(o.monthly_orders, 0) as orders_in_month,
        coalesce(o.monthly_items, 0) as items_in_month,
        coalesce(o.monthly_revenue, 0) as revenue_in_month,
        
        case when coalesce(o.monthly_orders, 0) > 0 then true else false end as is_active
        
    from user_months um
    join users u on um.user_id = u.user_id
    left join orders o on um.user_id = o.user_id and um.activity_month = o.order_month
),

cumulative as (
    select
        *,
        sum(orders_in_month) over (partition by user_id order by activity_month) as cumulative_orders,
        sum(revenue_in_month) over (partition by user_id order by activity_month) as cumulative_revenue
    from joined
)

select * from cumulative
