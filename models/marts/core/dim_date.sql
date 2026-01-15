with date_spine as (

    select *
    from unnest(generate_date_array('2019-01-01', '2026-12-31', interval 1 day)) as date_day

),

calculated as (

    select
        date_day as date_key,
        extract(dayofweek from date_day) as day_of_week,
        format_date('%A', date_day) as day_name,
        case when extract(dayofweek from date_day) in (1, 7) then true else false end as is_weekend,
        extract(week from date_day) as week_of_year,
        extract(month from date_day) as month_number,
        format_date('%B', date_day) as month_name,
        extract(quarter from date_day) as quarter,
        extract(year from date_day) as year,
        date_day = date_trunc(date_day, month) as is_month_start,
        date_day = last_day(date_day, month) as is_month_end,
        date_day = date_trunc(date_day, quarter) as is_quarter_start,
        date_day = last_day(date_day, quarter) as is_quarter_end
    from date_spine

)

select * from calculated
