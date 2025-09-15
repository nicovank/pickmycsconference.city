# URV Summer 2025

# [Pick My CS Conference City](https://pickmycsconference.city)

[![Poster](https://pickmycsconference.city/poster.jpg)](https://pickmycsconference.city/poster.pdf)

## Adding conference data

Use the following workflow to add a new conference (example for FSE 2024):

```bash
# 1. Gather all papers DOI and metadata.
# (Repeat in case there are multiple DBLP links for a single conference.)
python3 src/python/dblpscrape.py \
  --conference FSE \
  --year 2024 \
  --url https://dblp.org/db/conf/sigsoft/fse2024c.html \
  --city 'Porto de Galinhas' \
  --latitude -35.00119080181853 \
  --longitude -8.485919959103136

# 2. Download all PDFs (requires Windows).
# For ACM conferences:
python3 src/python/gather_acm_pdfs.py \
  --conference FSE \
  --year 2024

# 3. Populate affiliations in database
python3 src/python/fill_affiliations.py --conference FSE --year 2024 --pdf-directory '.pdfs/FSE 2024'
```

## Development

### Code formatting

All code should be run through the formatter. To format Python code, run Black:

```bash
python3 -m black src/python
```

Python code also needs to pass the typechecker:

```bash
python3 -m pip install mypy
python3 -m mypy --strict src/python
```

For HTML/CSS/JS/other code, run [Prettier](https://prettier.io):

```bash
npm install --global prettier
prettier --write "**/*.{css,html,js,json,md,yaml}"
```
