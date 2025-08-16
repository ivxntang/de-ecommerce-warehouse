with oi as (select * from {{ ref('stg_order_items') }}),
o as (select * from {{ ref('stg_orders') }})
select
  o.order_ts::date as order_date,
  oi.order_id,
  oi.line_number,
  o.customer_id,
  oi.product_id,
  oi.quantity,
  oi.unit_price,
  oi.amount
from oi join o using(order_id)
