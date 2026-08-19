with item_totals as (
    select order_id, sum(amount) as item_total
    from {{ ref('stg_order_items') }}
    group by order_id
), mismatches as (
    select o.order_id
    from {{ ref('stg_orders') }} o
    join item_totals i using (order_id)
    where o.total_amount <> i.item_total
)
select * from mismatches