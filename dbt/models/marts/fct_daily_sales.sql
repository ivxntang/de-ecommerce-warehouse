with f as (select * from {{ ref('fct_order_items') }})
select
  order_date,
  sum(amount) as gross_sales,
  count(distinct order_id) as orders,
  sum(quantity) as units
from f
group by 1
order by 1
