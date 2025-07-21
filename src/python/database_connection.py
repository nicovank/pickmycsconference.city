import psycopg2


def open_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(
        database="urv",
        host="157.230.67.84",
        user="urv",
        password="urv-summer-2025",
        port=5432,
    )
