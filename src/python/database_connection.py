import os

import psycopg2


def open_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(
        database=os.getenv("DATABASE_NAME"),
        host=os.getenv("DATABASE_HOST"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        port=int(os.getenv("DATABASE_PORT", "5432")),
    )
