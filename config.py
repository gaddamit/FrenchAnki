from pathlib import Path


BASE_DIR = Path(__file__).parent

NOUNS_DIR = BASE_DIR / "cards" / "nouns"
AUDIO_DIR = BASE_DIR / "audio"
UNSPLASH_CACHE_FILE = BASE_DIR / "unsplash_cache.json"

FEMALE_VOICE = "fr-FR-DeniseNeural"
MALE_VOICE = "fr-FR-HenriNeural"

OUTPUT_FILE_NAME = "FrenchVocabulary.apkg"

NOUN_CSV_FIELDS = [
    "french",
    "article",
    "gender",
    "english",
    "context",
    "context_en",
    "search_terms",
]

CATEGORY_DECKS = {
    "people_and_family.csv": (2059400111, "People and Family"),
    "animals.csv": (2059400112, "Animals"),
    "food_and_drink.csv": (2059400113, "Food and Drink"),
    "places_work_education_and_transport.csv": (
        2059400114,
        "Places and Transport",
    ),
    "nature_weather_and_time.csv": (2059400115, "Nature and Time"),
    "objects.csv": (2059400116, "Objects"),
    "abstract_concepts.csv": (2059400117, "Abstract"),
}
