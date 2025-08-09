# Frontend Data Format

This document defines the JSON structure that the `db_to_json.py` script produces.

Each conference will have its own JSON file, named after its short name (ex, `FSE.json`, `OSDI.json`)

## Structure

```json
{
  "conference_short_name": "FSE",
  "happenings": [
    {
      "year": 2025,
      "location": {
        "city": "xxxx",
        "latitude": 0000,
        "longitude": 0000
      },
      "submissions": [
        {
          "author_name": "xxx yyy",
          "affiliation_name": "zzzzz",
          "location": {
            "latitude": 0000,
            "longitude": 0000
          }
        }
      ]
    }
  ]
}
```

## Definitions

* **`conference_short_name`** (`string`): The unique short name/acronym for the conference.
* **`happenings`** (`array` of `object`): A list of each year the conference was held.
    * **`year`** (`integer`): The year of the conference happening.
    * **`location`** (`object`): The geographic location of the conference venue for that year.
    * **`submissions`** (`array` of `object`): A list of all paper submissions for that happening.
        * **`author_name`** (`string`): The name of the author.
        * **`affiliation_name`** (`string`): The name of the author's institution.
        * **`location`** (`object`): The geographic coordinates of the affiliation.