WITH src AS (
  SELECT
    customer_id,
    full_name,
    email,
    city,
    segment,
    updated_at
  FROM raw_customers
)
SELECT * FROM src
