import os
import psycopg2

# --- SQL STATEMENTS FOR TABLE CREATION ---
# Tables are defined in an order that respects dependencies.
# Ex: 'affiliations' and 'conferences' are created before tables that reference them.

TABLES_SQL = [
    """
    CREATE TABLE affiliations (
        affiliation_id SERIAL PRIMARY KEY,
        organization_name VARCHAR(255) UNIQUE NOT NULL,
        latitude DECIMAL(9, 6),
        longitude DECIMAL(9, 6),
    );
    """,
    """
    CREATE TABLE affiliation_aliases (
        alias_id SERIAL PRIMARY KEY,
        alias_name VARCHAR(255) UNIQUE NOT NULL,
        affiliation_id INTEGER NOT NULL REFERENCES affiliations(affiliation_id)
    );
    """,
    """
    CREATE TABLE conferences (
        conference_id SERIAL PRIMARY KEY,
        short_name VARCHAR(50) UNIQUE NOT NULL,
        long_name VARCHAR(255)
    );
    """,
    """
    CREATE TABLE conference_happenings (
        conference_id INTEGER NOT NULL REFERENCES conferences(conference_id),
        year INTEGER NOT NULL,
        city VARCHAR(100),
        start_date DATE,
        end_date DATE,
    );
    """,
    """
    CREATE TABLE papers (
        paper_id SERIAL PRIMARY KEY,
        doi VARCHAR(255) UNIQUE NOT NULL,
        title TEXT,
        publication_year INTEGER,
        pdf_filepath TEXT,
        manually_edited BOOLEAN DEFAULT FALSE NOT NULL,
        last_auto_update TIMESTAMPTZ
    );
    """,
    """
    CREATE TABLE authors (
        author_id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) UNIQUE NOT NULL
    );
    """,
    """
    CREATE TABLE paper_authors (
        paper_author_id SERIAL PRIMARY KEY,
        paper_id INTEGER NOT NULL REFERENCES papers(paper_id),
        author_id INTEGER NOT NULL REFERENCES authors(author_id),
        affiliation_id INTEGER REFERENCES affiliations(affiliation_id),
        author_position SMALLINT NOT NULL CHECK (author_position > 0),
        UNIQUE(paper_id, author_id)
    );
    """
]

