# URV Summer 2025

We'll find a good name for this later.

## Adding conference data

Use the following workflow to add a new conference (example for FSE 2024):

```bash
# 1. Gather all papers DOI and metadata:
python3 src/python/dblpscrape.py \
  --conference FSE \
  --year 2024 \
  --url https://dblp.org/db/conf/sigsoft/fse2024c.html \
  --longitude -8.485919959103136 \
  --latitude -35.00119080181853

# 2. Download all PDFs (requires Windows).
# For ACM conferences:
python3 src/python/gather_acm_pdfs.py \
  --conference FSE \
  --year 2024

# 3. Populate affiliations in database
[TODO]
```

## Development

Let's try to implement some common industry coding practices.

### Code formatting

All code should be run through the formatter. I've set up CI to auto-complain if something is not right.
To format Python code, run Black:

```bash
python3 -m black src/python
```

You might also want to run the typechecker. If this rings any issues you're not sure how to handle,
we'll look at it together!

```bash
python3 -m pip install mypy
python3 -m mypy src/python
```

For HTML/CSS/JS/other code, install and run [Prettier](https://prettier.io).

```bash
npm install --global prettier
prettier --write "**/*.{css,html,js,json,md,yaml}"
```

There's a [Prettier VS Code extension](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode).
If you use it with auto-formatting on, add this to your preferences:

```json
{
  "[css]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[html]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[json]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[markdown]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[yaml]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### Pull requests

Let's try and have changes go through pull requests and I'll go ahead and review and stamp them to give feedback.
One goal is to make you comfortable contributing code in a "professional" environment.

I use [Sapling](https://sapling-scm.com) personally.
There's a [Sapling VS Code extension](https://marketplace.visualstudio.com/items?itemName=meta.sapling-scm).
The VS Code extension has a pretty neat GUI. Select the `pr` workflow when submitting. I'll do a demo during a meeting.
On the command line it looks very similar to using vanilla git:

```bash
sl # Nice visual representation of where you are.
sl commit
sl pr submit
```

If using git, use branches, then use Github's website to submit a PR:

```bash
git switch -c my-branch
git commit
git push
```
