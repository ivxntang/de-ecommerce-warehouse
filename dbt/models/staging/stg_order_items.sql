WITH src AS (
  SELECT
    order_id,
    line_number,
    product_id,
    quantity,
    CAST(unit_price AS NUMERIC(10,2)) AS unit_price,
    CAST(amount AS NUMERIC(12,2)) AS amount
  FROM raw_order_items
)
SELECT * FROM src
