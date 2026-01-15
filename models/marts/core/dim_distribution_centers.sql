with distribution_centers as (

    select * from {{ ref('stg_distribution_centers') }}

)

select
    distribution_center_id,
    distribution_center_name,
    latitude,
    longitude
from distribution_centers
