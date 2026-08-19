{% snapshot snap_customers %}

{{
  config(
    target_schema='snapshots',
    unique_key='customer_id',
    strategy='timestamp',
    updated_at='updated_at'
  )
}}

-- Take history from the cleaned staging model
select
  customer_id,
  full_name,
  email,
  city,
  segment,
  updated_at at time zone 'UTC' as updated_at
from {{ ref('stg_customers') }}

{% endsnapshot %}
