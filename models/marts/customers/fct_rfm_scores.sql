with user_summary as (

    select * from {{ ref('int_user_order_summary') }}

),

scored as (

    select
        user_id,
        date_diff(current_date, date(last_order_at), day) as recency_days,
        total_orders as frequency,
        total_revenue as monetary,
        
        -- Scores (1-5)
        ntile(5) over (order by date_diff(current_date, date(last_order_at), day) desc) as recency_score,
        ntile(5) over (order by total_orders asc) as frequency_score,
        ntile(5) over (order by total_revenue asc) as monetary_score

    from user_summary

),

segmented as (

    select
        *,
        concat(recency_score, frequency_score, monetary_score) as rfm_code,
        
        case
            when recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4 then 'Champions'
            when recency_score >= 3 and frequency_score >= 4 and monetary_score >= 3 then 'Loyal Customers'
            when recency_score >= 4 and frequency_score >= 2 and monetary_score >= 2 then 'Potential Loyalists'
            when recency_score >= 4 and frequency_score = 1 then 'Recent Customers'
            when recency_score >= 3 and frequency_score = 1 then 'Promising'
            when recency_score >= 2 and frequency_score >= 2 then 'Needs Attention'
            when recency_score <= 2 and frequency_score >= 4 then 'Can\'t Lose'
            when recency_score <= 2 and frequency_score >= 2 then 'At Risk'
            else 'Lost'
        end as rfm_segment

    from scored

)

select * from segmented
