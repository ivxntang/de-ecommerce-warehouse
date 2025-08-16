-- 1) Raw table counts
select 'raw_orders' t, count(*) c from public.raw_orders
union all select 'raw_order_items', count(*) from public.raw_order_items
union all select 'raw_customers', count(*) from public.raw_customers
union all select 'raw_products', count(*) from public.raw_products;

-- 2) Daily sales (last 10 days)
select order_date, gross_sales
from staging_marts.fct_daily_sales
where order_date >= current_date - interval '9 days'
order by order_date;

-- 3) Customers with SCD2 history (>1 version)
select customer_id, count(*) versions
from staging_marts.dim_customer
group by 1
having count(*) > 1
order by versions desc
limit 10;

-- 4) History for one customer (example)
select customer_id, city, segment, valid_from, valid_to, is_current
from staging_marts.dim_customer
where customer_id = 'C100001'
order by valid_from;

-- 5) Top categories by sales (30d)
select dp.category, sum(oi.amount) as sales
from staging_marts.fct_order_items oi
join staging_marts.dim_product dp using (product_id)
where oi.order_date >= current_date - interval '30 days'
group by 1
order by sales desc
limit 5;

-- 6) Data freshness (latest order date)
select max(order_date) as latest_order_date
from public.raw_orders;
