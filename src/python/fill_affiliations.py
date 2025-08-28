import argparse

from database_connection import open_connection

from dblpscrape import get_details_from_xml
from coords_entry import insert_affiliation
from get_affiliation import get_affiliations


# This function has some printing for debugging purposes, in case something goes wrong.
def main(args: argparse.Namespace) -> None:
    connection = open_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT doi, dblp_pub_id FROM papers WHERE conference_short_name = %s AND conference_year = %s",
        (args.conference, args.year),
    )

    print(f"Processing {cursor.rowcount} papers...")

    errors: list[str] = []

    for entry in cursor.fetchall():
        print("\n")
        doi, dblp_pub_id = entry
        print(f"Processing DOI: {doi}")

        details = get_details_from_xml(dblp_pub_id)
        if not details:
            print(f"[WARNING] Skipping {doi} due to failed DBLP parsing.")
            continue
        authors = details["authors"]
        print("Authors according to DBLP:")
        for i, author in enumerate(authors):
            print(f" {i + 1}. {author}")

        # If paper exists with same number of authors in the database, skip it.
        cursor.execute(
            "SELECT COUNT(*) FROM paper_affiliations WHERE paper_doi = %s",
            (doi,),
        )
        if cursor.fetchone()[0] == len(authors):
            print(f"Paper already has affiliations in database. Skipping.")
            continue

        pdf_path = f"{args.pdf_directory}/{doi.replace('/', '_')}.pdf"
        try:
            affiliations = get_affiliations(pdf_path)
        except Exception as e:
            print("[ERROR] Some error getting info from OpenAI.")
            errors.append(f"{doi} / {str(e)}")
            continue
        print("Authors and affiliations according to OpenAI:")
        for i, (author_name, affiliation) in enumerate(affiliations):
            print(f" {i + 1}. {author_name}: {affiliation}")

        # Map dblp authors to affiliations authors using cosine similarity matrix.
        # Copilot wrote this part.
        matrix = [
            [
                (
                    sum(a * b for a, b in zip(author_vector, affiliation_vector))
                    / (
                        (sum(a * a for a in author_vector) ** 0.5)
                        * (sum(b * b for b in affiliation_vector) ** 0.5)
                    )
                    if (
                        sum(a * a for a in author_vector) > 0
                        and sum(b * b for b in affiliation_vector) > 0
                    )
                    else 0.0
                )
                for affiliation_vector in [
                    affiliation_name.encode("utf-8")
                    for affiliation_name, _ in affiliations
                ]
            ]
            for author_vector in [
                author_name.encode("utf-8") for author_name in authors
            ]
        ]

        print("Cosine similarity matrix:")
        for row in matrix:
            print(" ", ["{0:.2f}".format(value) for value in row])
        # Assert max in unique in both dimensions.
        assert all(row.count(max(row)) == 1 for row in matrix)
        for col_index in range(len(matrix[0])):
            col = [matrix[row_index][col_index] for row_index in range(len(matrix))]
            assert col.count(max(col)) == 1
        # Now, for each author, find the affiliation with the highest cosine similarity.
        author_to_affiliation = {}
        for author_index, row in enumerate(matrix):
            max_index = row.index(max(row))
            author_to_affiliation[authors[author_index]] = affiliations[max_index][1]
        print("Mapped authors to affiliations:")
        for author, affiliation in author_to_affiliation.items():
            print(f" {author}: {affiliation}")

        for author, affiliation in author_to_affiliation.items():
            # First, insert into affiliations with location.
            try:
                insert_affiliation(cursor, affiliation)
            except:
                print(f"[ERROR] Failed to map affiliation: {affiliation}")
                errors.append(f"{doi} / {author} / {affiliation}")
                continue

            # Then, insert into paper_affiliations.
            cursor.execute(
                """
                    INSERT INTO paper_affiliations (paper_doi, author_name, affiliation_name)
                    VALUES (%s, %s, %s)
                """,
                (doi, author, affiliation),
            )
            assert cursor.rowcount == 1
            print(f"Inserted entry for {doi}/{author}: {affiliation}")

        # Commit.
        connection.commit()

    print("\n\n")
    print("LIST OF ERRORS, PLEASE ADD MANUALLY:")
    for e in errors:
        print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--conference", type=str, required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--pdf-directory", type=str, required=True)
    main(parser.parse_args())
