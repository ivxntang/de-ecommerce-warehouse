import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine


load_dotenv()


REQUIRED_VARS = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")


def database_settings():
    missing = [name for name in REQUIRED_VARS if not os.getenv(name)]
    if missing:
        names = ", ".join(missing)
        raise RuntimeError(f"Missing database environment variables: {names}")

    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.environ["DB_PORT"]),
        "database": os.environ["DB_NAME"],
        "username": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
    }


def create_database_engine():
    settings = database_settings()
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=settings["username"],
        password=settings["password"],
        host=settings["host"],
        port=settings["port"],
        database=settings["database"],
    )
    return create_engine(url, pool_pre_ping=True)