WITH src AS (
  SELECT
    product_id,
    name,
    category,
    CAST(price AS NUMERIC(10,2)) AS price,
    updated_at
  FROM {{ source('raw', 'products') }}
)
SELECT * FROM src
