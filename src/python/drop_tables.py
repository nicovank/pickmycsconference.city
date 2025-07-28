from database_connection import open_connection

if __name__ == "__main__":
    try:
        conn = open_connection()
        cur = conn.cursor()

        cur.execute(
            """
                DROP TABLE IF EXISTS paper_affiliations;
                DROP TABLE IF EXISTS affiliations;
                DROP TABLE IF EXISTS papers;
                DROP TABLE IF EXISTS conference_happenings;
                DROP TABLE IF EXISTS conferences;
            """
        )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database/Connection error: {e}")
