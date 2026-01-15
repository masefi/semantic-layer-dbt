with cohort_activity as (
    select * from {{ ref('fct_customer_cohorts') }}
),

agg as (
    select
        signup_cohort,
        activity_month as order_month,
        months_since_signup,
        
        count(distinct user_id) as total_cohort_users, -- This varies per month if filter is active? No spine has all users.
        count(distinct case when is_active then user_id end) as active_customers,
        sum(orders_in_month) as total_orders,
        sum(revenue_in_month) as total_revenue,
        sum(cumulative_revenue) as cumulative_revenue_total
        
    from cohort_activity
    group by 1, 2, 3
)

select
    *,
    safe_divide(active_customers, total_cohort_users) as active_pct, -- Retention
    safe_divide(total_revenue, active_customers) as avg_revenue_per_active_user,
    safe_divide(cumulative_revenue_total, total_cohort_users) as ltv_to_date
from agg
order by signup_cohort, months_since_signup
