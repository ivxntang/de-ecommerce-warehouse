WITH src AS (
  SELECT
    customer_id,
    full_name,
    email,
    city,
    segment,
    updated_at
  FROM {{ source('raw', 'customers') }}
)
SELECT * FROM src
