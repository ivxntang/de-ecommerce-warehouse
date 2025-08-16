with snap as (
  select * from {{ ref('snap_customers') }}
),
final as (
  select
    customer_id,
    full_name,
    email,
    city,
    segment,
    dbt_valid_from as valid_from,
    dbt_valid_to   as valid_to,
    case when dbt_valid_to is null then true else false end as is_current
  from snap
)
select * from final
