with users as (

    select * from {{ ref('stg_users') }}

),

final as (

    select
        user_id,
        email,
        first_name,
        last_name,
        age,
        gender,
        city,
        country,
        latitude,
        longitude,
        traffic_source,
        created_at,
        
        -- Cohort & Tenure
        format_date('%Y-%m', date(created_at)) as signup_cohort,
        date_diff(current_date, date(created_at), day) as tenure_days,
        
        -- Age Segmentation
        case 
            when age < 18 then 'Under 18'
            when age >= 18 and age <= 24 then '18-24'
            when age >= 25 and age <= 34 then '25-34'
            when age >= 35 and age <= 44 then '35-44'
            when age >= 45 and age <= 54 then '45-54'
            when age >= 55 and age <= 64 then '55-64'
            else '65+'
        end as age_group

    from users

)

select * from final
