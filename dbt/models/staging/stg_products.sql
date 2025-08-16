WITH src AS (
  SELECT
    product_id,
    name,
    category,
    CAST(price AS NUMERIC(10,2)) AS price,
    updated_at
  FROM raw_products
)
SELECT * FROM src
