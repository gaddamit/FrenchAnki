# French Anki Deck Generator

Generate an Anki package for learning French vocabulary. The generator reads noun and verb cards from CSV files, finds related Unsplash images, creates French audio with Microsoft Edge TTS, and exports the result as `FrenchVocabulary.apkg`.

## Deck structure

The generated package contains these subdecks:

```text
Learn French
├── Nouns
│   ├── People and Family
│   ├── Animals
│   ├── Food and Drink
│   ├── Places and Transport
│   ├── Nature and Time
│   ├── Objects
│   └── Abstract
└── Verbs
```

Each card asks for the French noun from an English word, image, and example sentence. The answer shows the article, French noun, translated sentence, and pronunciation.

## Project structure

```text
.
├── cards/
│   ├── nouns/              # Noun CSV files used by the generator
│   └── verbs/verbs.csv     # Verb vocabulary
├── audio/                  # Generated pronunciation files
├── anki_model.py           # Card data and Anki note template
├── config.py               # Paths, voices, schemas, and deck configuration
├── generate_deck.py        # Deck generation script
└── unsplash_cache.json     # Cached Unsplash API results
```

Generated audio, the Unsplash cache, `.env`, and `.apkg` packages are excluded from Git.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install python-dotenv edge-tts genanki requests
```

Create a `.env` file containing an [Unsplash API access key](https://unsplash.com/developers):

```dotenv
UNSPLASH_ACCESS_KEY=your_access_key
```

Do not commit the `.env` file.

## Generate the deck

Run:

```bash
.venv/bin/python generate_deck.py
```

The script validates the CSV files, processes every configured category, and writes:

```text
FrenchVocabulary.apkg
```

Import that package into Anki to install or update the decks.

## Noun CSV format

Every noun CSV must use this exact header:

```csv
french,article,gender,english,context,context_en,search_terms
```

Example:

```csv
"homme","un","m","man","L'homme marche dans la rue.","The man walks in the street.","man portrait person"
```

| Column | Purpose |
| --- | --- |
| `french` | French noun |
| `article` | Article displayed with the noun |
| `gender` | `m` or `f`; also selects the audio voice |
| `english` | English meaning and cache key |
| `context` | French example sentence |
| `context_en` | English translation of the example |
| `search_terms` | Query sent to Unsplash |

All fields are required. Invalid headers or empty values produce an error containing the CSV filename and row number.

## Add or change a category

Place the CSV in `cards/nouns/`, then add its filename, stable numeric deck ID, and display name to `CATEGORY_DECKS` in `config.py`:

```python
CATEGORY_DECKS = {
    "people_and_family.csv": (2059400111, "People and Family"),
}
```

Keep an existing deck ID unchanged. Anki uses it to recognize the same deck during later imports.

## Image cache and API usage

Unsplash results are stored in `unsplash_cache.json`, keyed by the English word. Subsequent runs reuse cached results instead of repeating API searches. A successful new image normally causes a search request followed by Unsplash's required download-tracking request.

The console messages distinguish cache and API behavior:

- `Using cached Unsplash result` means no new search was made.
- `No image found` means the API responded with no matches.
- `Image lookup failed` means a network, authentication, rate-limit, or API error occurred.

To retry a cached result, remove only that word's entry from `unsplash_cache.json`. Keep the JSON syntax valid.

## Audio cache

Audio is saved under `audio/`. Existing MP3 files are reused on later runs. Delete a specific MP3 only when you want the script to regenerate that pronunciation.

## Verb CSV format

Verb cards use a separate parser and Anki model. The CSV must use this exact header:

```csv
infinitive,group,english,context,context_en,search_terms
```

The `group` value must be `1`, `2`, or `3`. The answer displays the corresponding French group label beside the infinitive.
