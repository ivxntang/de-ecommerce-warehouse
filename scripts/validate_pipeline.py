from sqlalchemy import text

from db_config import create_database_engine


CHECKS = {
    "raw customers": "SELECT COUNT(*) FROM raw.raw_customers",
    "raw products": "SELECT COUNT(*) FROM raw.raw_products",
    "raw orders": "SELECT COUNT(*) FROM raw.raw_orders",
    "raw order items": "SELECT COUNT(*) FROM raw.raw_order_items",
    "mart daily sales": "SELECT COUNT(*) FROM staging_marts.fct_daily_sales",
    "mart order items": "SELECT COUNT(*) FROM staging_marts.fct_order_items",
}


def main():
    engine = create_database_engine()
    with engine.connect() as connection:
        for name, query in CHECKS.items():
            count = connection.execute(text(query)).scalar_one()
            if count == 0:
                raise RuntimeError(f"Validation failed: {name} is empty")
            print(f"OK {name}: {count}")

        orphan_items = connection.execute(text("""
            SELECT COUNT(*)
            FROM raw.raw_order_items oi
            LEFT JOIN raw.raw_orders o USING (order_id)
            LEFT JOIN raw.raw_products p USING (product_id)
            WHERE o.order_id IS NULL OR p.product_id IS NULL
        """)).scalar_one()
        if orphan_items:
            raise RuntimeError(f"Validation failed: {orphan_items} orphan order items")

    print("Warehouse validation passed.")


if __name__ == "__main__":
    main()