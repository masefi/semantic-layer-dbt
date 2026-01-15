with cohorts as (
    select * from {{ ref('fct_customer_cohorts') }}
),

agg as (
    select
        signup_cohort,
        months_since_signup,
        count(distinct user_id) as cohort_size,
        count(distinct case when is_active then user_id end) as active_customers,
        sum(revenue_in_month) as total_revenue,
        sum(cumulative_revenue) as total_cumulative_revenue
    from cohorts
    group by 1, 2
),

final as (
    select
        signup_cohort,
        months_since_signup,
        cohort_size,
        active_customers,
        safe_divide(active_customers, cohort_size) as retention_rate,
        total_revenue,
        safe_divide(total_revenue, active_customers) as avg_revenue_per_active_customer,
        safe_divide(total_cumulative_revenue, cohort_size) as cumulative_revenue_per_customer
    from agg
)

select * from final
order by 1, 2
