import psycopg2
from psycopg2.extensions import cursor
# --- SQL STATEMENTS FOR TABLE CREATION ---
# Tables are defined in an order that respects dependencies.
# Ex: 'affiliations' and 'conferences' are created before tables that reference them.

TABLES_SQL: list[str] = [
    """
    CREATE TABLE conferences (
        short_name VARCHAR(50) PRIMARY KEY,
        long_name VARCHAR(255)
    );
    """,
    """
    CREATE TABLE conference_happenings (
        conference_short_name VARCHAR(50) NOT NULL REFERENCES conferences(short_name),
        year INTEGER NOT NULL,
        location VARCHAR(100),
        start_date DATE,
        end_date DATE,
        PRIMARY KEY (conference_short_name, year)
    );
    """,
    """
    CREATE TABLE papers (
	    doi VARCHAR(255) PRIMARY KEY,
		title TEXT,
		conference_short_name VARCHAR(50),
		conference_year INTEGER,
		manually_edited BOOLEAN DEFAULT FALSE NOT NULL,
		FOREGIN KEY(conference_short_name, conference_year) REFERENCES conference_happenings(conference_short_name, year)
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
    # Can make these into args or env if needed
    db_name = "urv"
    db_user = "urv"
    db_password = "urv-summer-2025"
    db_host = "157.230.67.84"
    db_port = "5432"

    conn = None
    try:
        conn = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
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
