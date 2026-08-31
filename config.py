from pathlib import Path


BASE_DIR = Path(__file__).parent

NOUNS_DIR = BASE_DIR / "cards" / "nouns"
VERBS_FILE = BASE_DIR / "cards" / "verbs" / "verbs.csv"
AUDIO_DIR = BASE_DIR / "audio"
NOUN_AUDIO_DIR = AUDIO_DIR / "nouns"
VERB_AUDIO_DIR = AUDIO_DIR / "verbs"
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

VERB_CSV_FIELDS = [
    "infinitive",
    "group",
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

VERB_DECK = (2059400200, "Learn French::Verbs")
