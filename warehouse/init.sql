-- Schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS snapshots;

-- Raw tables
CREATE TABLE IF NOT EXISTS raw_customers (
  customer_id TEXT PRIMARY KEY,
  full_name TEXT,
  email TEXT,
  city TEXT,
  segment TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw_products (
  product_id TEXT PRIMARY KEY,
  name TEXT,
  category TEXT,
  price NUMERIC(10,2),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw_orders (
  order_id TEXT PRIMARY KEY,
  customer_id TEXT NOT NULL REFERENCES raw_customers(customer_id),
  order_ts TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL,
  total_amount NUMERIC(12,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_order_items (
  order_id TEXT NOT NULL REFERENCES raw_orders(order_id) ON DELETE CASCADE,
  line_number INT NOT NULL,
  product_id TEXT NOT NULL REFERENCES raw_products(product_id),
  quantity INT NOT NULL,
  unit_price NUMERIC(10,2) NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  PRIMARY KEY (order_id, line_number)
);
