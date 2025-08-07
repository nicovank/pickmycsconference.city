import psycopg2
from psycopg2.extensions import cursor

from database_connection import open_connection

# --- SQL STATEMENTS FOR TABLE CREATION ---
# Tables are defined in an order that respects dependencies.
# Ex: 'affiliations' and 'conferences' are created before tables that reference them.

TABLES_SQL: list[str] = [
    """
    CREATE TABLE conference_happenings (
        conference_short_name VARCHAR(50) NOT NULL,
        year INTEGER NOT NULL,
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION,
        PRIMARY KEY (conference_short_name, year)
    );
    """,
    """
    CREATE TABLE papers (
        doi VARCHAR(255) PRIMARY KEY,
        title TEXT,
        conference_short_name VARCHAR(50),
        conference_year INTEGER,
        dblp_xml_url VARCHAR(255),
        manually_edited BOOLEAN DEFAULT FALSE NOT NULL,
        FOREIGN KEY(conference_short_name, conference_year) REFERENCES conference_happenings(conference_short_name, year)
    );
    """,
    """
    CREATE TABLE affiliations (
        affiliation_name VARCHAR(255) PRIMARY KEY,
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION,
        manually_edited BOOLEAN DEFAULT FALSE NOT NULL
    );
    """,
    """
    CREATE TABLE paper_affiliations (
        paper_doi VARCHAR(255) REFERENCES papers(doi),
        author_name VARCHAR(255),
        affiliation_name VARCHAR(255) REFERENCES affiliations(affiliation_name),
        PRIMARY KEY (paper_doi, author_name)
    );
    """,
]


def create_tables(conn: cursor) -> None:
    for tbl in TABLES_SQL:
        try:
            conn.execute(tbl)
            print("Table created successfully.")
        except psycopg2.Error as e:
            print(f"Error: {e}")
            # conn.rollback() --- Change as needed for decided error handling
            raise e


def main() -> None:
    conn = None
    try:
        conn = open_connection()
        cur = conn.cursor()
        create_tables(cur)
        print("Creating tables")

        conn.commit()
        print("Tables created")
    except psycopg2.Error as e:
        print(f"Database/Connection error: {e}")

    if conn:
        conn.close()
        print("DB conn closed")


if __name__ == "__main__":
    main()
