with source as (

    select * from {{ source('thelook_ecommerce', 'events') }}

),

renamed as (

    select
        id as event_id,
        user_id,
        session_id,
        sequence_number,
        event_type,
        uri,
        browser,
        traffic_source,
        city,
        state,
        postal_code,
        ip_address,
        created_at,
        date(created_at) as event_date
    from source

)

select * from renamed
where event_id is not null
