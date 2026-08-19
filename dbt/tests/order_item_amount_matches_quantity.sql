select order_id, line_number
from {{ ref('stg_order_items') }}
where amount <> quantity * unit_price