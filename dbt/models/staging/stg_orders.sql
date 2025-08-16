WITH src AS (
  SELECT
    order_id,
    customer_id,
    order_ts,
    status,
    CAST(total_amount AS NUMERIC(12,2)) AS total_amount
  FROM raw_orders
)
SELECT * FROM src
