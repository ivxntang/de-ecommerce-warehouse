import os, random
from datetime import datetime, timedelta, timezone
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
ENGINE = create_engine(os.getenv("DATABASE_URL"))

random.seed(42)

CITIES = ["Singapore","Johor Bahru","Kuala Lumpur","Bangkok","Jakarta","Manila","Ho Chi Minh City","Hanoi","Taipei","Hong Kong"]
SEGMENTS = ["consumer","smb","enterprise"]
CATEGORIES = ["electronics","home","beauty","sports","toys","books"]
PRODUCTS = [{"product_id": f"P{1000+i}", "name": f"Product {i}", "category": random.choice(CATEGORIES), "price": round(random.uniform(5,500),2)} for i in range(200)]

def ensure_products():
    df = pd.DataFrame(PRODUCTS)
    df["updated_at"] = datetime.now(timezone.utc)
    with ENGINE.begin() as conn:
        tmp = "tmp_products"
        conn.execute(text(f"DROP TABLE IF EXISTS {tmp};"))
        df.to_sql(tmp, conn, if_exists="replace", index=False)
        conn.execute(text(f"""
            INSERT INTO raw_products (product_id,name,category,price,updated_at)
            SELECT product_id,name,category,price,updated_at FROM {tmp}
            ON CONFLICT (product_id) DO UPDATE SET
              name=EXCLUDED.name,
              category=EXCLUDED.category,
              price=EXCLUDED.price,
              updated_at=EXCLUDED.updated_at;
            DROP TABLE {tmp};
        """))

def random_name():
    first = random.choice(["Alex","Jamie","Taylor","Jordan","Chris","Morgan","Riley","Casey","Avery","Kai","Jin","Wei","Sam","Evan","Noah","Maya","Ivy","Mei","Hana","Yuna"])
    last = random.choice(["Tan","Lim","Ng","Lee","Wong","Chan","Chong","Goh","Chew","Tay","Koh","Ho","Toh","Yap","Sim"])
    return f"{first} {last}"

def random_email(name):
    base = "".join(ch for ch in name.lower() if ch.isalpha())
    domain = random.choice(["example.com","shop.com","mail.com"])
    return f"{base}{random.randint(10,9999)}@{domain}"

def ensure_customers(n_seed=1000):
    with ENGINE.begin() as conn:
        cnt = conn.execute(text("SELECT COUNT(*) FROM raw_customers")).scalar()
    if cnt == 0:
        rows = []
        for i in range(n_seed):
            cid = f"C{100000+i}"
            nm = random_name()
            rows.append({
                "customer_id": cid,
                "full_name": nm,
                "email": random_email(nm),
                "city": random.choice(CITIES),
                "segment": random.choice(SEGMENTS),
                "updated_at": datetime.now(timezone.utc) - timedelta(days=random.randint(1,365))
            })
        df = pd.DataFrame(rows)
    else:
        with ENGINE.begin() as conn:
            df = pd.read_sql("SELECT * FROM raw_customers", conn.connection)
        mutate_idx = df.sample(frac=0.05, random_state=random.randint(0,9999)).index
        for i in mutate_idx:
            if random.random() < 0.5:
                df.loc[i,"city"] = random.choice(CITIES)
            if random.random() < 0.4:
                df.loc[i,"segment"] = random.choice(SEGMENTS)
            if random.random() < 0.3:
                df.loc[i,"email"] = random_email(df.loc[i,"full_name"])
            df.loc[i,"updated_at"] = datetime.now(timezone.utc)

    with ENGINE.begin() as conn:
        tmp = "tmp_customers"
        conn.execute(text(f"DROP TABLE IF EXISTS {tmp};"))
        df.to_sql(tmp, conn, if_exists="replace", index=False)
        conn.execute(text(f"""
            INSERT INTO raw_customers (customer_id,full_name,email,city,segment,updated_at)
            SELECT customer_id,full_name,email,city,segment,updated_at FROM {tmp}
            ON CONFLICT (customer_id) DO UPDATE SET
              full_name=EXCLUDED.full_name,
              email=EXCLUDED.email,
              city=EXCLUDED.city,
              segment=EXCLUDED.segment,
              updated_at=EXCLUDED.updated_at;
            DROP TABLE {tmp};
        """))

def generate_orders(n_orders=300):
    order_rows, item_rows = [], []
    now = datetime.now(timezone.utc)
    for _ in range(n_orders):
        order_id = f"O{random.randint(10_000_000,99_999_999)}"
        ts = now - timedelta(days=random.randint(0,3), hours=random.randint(0,23), minutes=random.randint(0,59))
        status = random.choices(["paid","shipped","cancelled","refunded"], weights=[0.8,0.15,0.03,0.02])[0]
        customer_id = f"C{100000+random.randint(0,999)}"
        n_items = random.randint(1,5)
        total = 0.0
        for ln in range(1, n_items+1):
            p = random.choice(PRODUCTS)
            qty = random.randint(1,3)
            unit = p["price"]
            amt = round(qty*unit, 2)
            total += amt
            item_rows.append({
                "order_id": order_id,
                "line_number": ln,
                "product_id": p["product_id"],
                "quantity": qty,
                "unit_price": unit,
                "amount": amt
            })
        order_rows.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_ts": ts,
            "status": status,
            "total_amount": round(total,2)
        })
    return pd.DataFrame(order_rows), pd.DataFrame(item_rows)

def load_orders(df_orders, df_items):
    with ENGINE.begin() as conn:
        tmpo = "tmp_orders"
        conn.execute(text(f"DROP TABLE IF EXISTS {tmpo};"))
        df_orders.to_sql(tmpo, conn, if_exists="replace", index=False)
        conn.execute(text(f"""
            INSERT INTO raw_orders (order_id,customer_id,order_ts,status,total_amount)
            SELECT order_id,customer_id,order_ts,status,total_amount FROM {tmpo}
            ON CONFLICT (order_id) DO NOTHING;
            DROP TABLE {tmpo};
        """))
        tmpi = "tmp_items"
        conn.execute(text(f"DROP TABLE IF EXISTS {tmpi};"))
        df_items.to_sql(tmpi, conn, if_exists="replace", index=False)
        conn.execute(text(f"""
            INSERT INTO raw_order_items (order_id,line_number,product_id,quantity,unit_price,amount)
            SELECT order_id,line_number,product_id,quantity,unit_price,amount FROM {tmpi}
            ON CONFLICT (order_id, line_number) DO NOTHING;
            DROP TABLE {tmpi};
        """))

def main():
    ensure_products()
    ensure_customers()
    df_orders, df_items = generate_orders(n_orders=300)
    load_orders(df_orders, df_items)
    print(f"Loaded {len(df_orders)} new orders and {len(df_items)} items.")

if __name__ == "__main__":
    main()
