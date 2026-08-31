import genanki
import html
import re
from config import AUDIO_DIR


def safe_filename(text):
    text = re.sub(r"[^a-zA-Z0-9_-]", "_", text)
    return text.lower()


class Card:
    def __init__(
        self,
        french,
        english,
        context,
        context_en,
        search_terms,
        audio_file,
    ):
        self.french = french
        self.english = english
        self.context = context
        self.context_en = context_en
        self.search_terms = search_terms
        self.audio_file = audio_file
        self.image_file = None
        self.image_credit = None

    def get_filename(self):
        return safe_filename(self.english)

    @classmethod
    def from_csv_row(cls, row):
        raise NotImplementedError("Card subclasses must implement from_csv_row()")

    def print_info(self, index, total):
        print(f"{index}/{total} {self.english} -> {self.french}")


class NounCard(Card):
    def __init__(
        self,
        french,
        article,
        gender,
        english,
        context,
        context_en,
        search_terms,
    ):
        super().__init__(
            french=french,
            english=english,
            context=context,
            context_en=context_en,
            search_terms=search_terms,
            audio_file=AUDIO_DIR / f"{safe_filename(english)}.mp3",
        )
        self.article = article
        self.gender = gender

    @classmethod
    def from_csv_row(cls, row):
        french = row["french"].strip()
        article = row["article"].strip()
        gender = row["gender"].strip()
        english = row["english"].strip()
        context = row["context"].strip()
        context_en = row["context_en"].strip()
        search_terms = row["search_terms"].strip()

        return cls(
            french,
            article,
            gender,
            english,
            context,
            context_en,
            search_terms,
        )


class VerbCard(Card):
    GROUP_LABELS = {
        "1": "1er groupe · régulier",
        "2": "2e groupe · régulier",
        "3": "3e groupe · irrégulier",
    }

    def __init__(
        self,
        infinitive,
        group,
        english,
        context,
        context_en,
        search_terms,
    ):
        if group not in self.GROUP_LABELS:
            raise ValueError(f"Unknown French verb group: {group}")

        super().__init__(
            french=infinitive,
            english=english,
            context=context,
            context_en=context_en,
            search_terms=search_terms,
            audio_file=AUDIO_DIR / f"verb_{safe_filename(english)}.mp3",
        )
        self.infinitive = infinitive
        self.group = group

    @property
    def group_label(self):
        return self.GROUP_LABELS[self.group]

    @classmethod
    def from_csv_row(cls, row):
        return cls(
            infinitive=row["infinitive"].strip(),
            group=row["group"].strip(),
            english=row["english"].strip(),
            context=row["context"].strip(),
            context_en=row["context_en"].strip(),
            search_terms=row["search_terms"].strip(),
        )


# -------------------------
# Create noun note
# -------------------------
def create_noun_note(card):
    image_html = ""
    audio_html = ""

    if card.image_file:
        image_html = (
            f'<img src="{card.image_file}">'
        )
    else:
        image_html = (
            f'<div class="no-image">'
            f'No image available'
            f'</div>'
        )

    if card.audio_file:
        audio_html = (
            f"[sound:{card.audio_file.name}]"
        )
    
    
    return genanki.Note(
        model=noun_model,

        fields=[
            html.escape(card.french),
            html.escape(card.article),
            html.escape(card.gender),
            html.escape(card.english),
            image_html,
            audio_html,
            html.escape(card.context),
            html.escape(card.context_en),
            card.image_credit if card.image_file else ""
        ],

        guid=genanki.guid_for(
            card.french,
            card.article,    
            card.gender,
            card.english,
            card.context,
            card.context_en
        )
)

# ----------------------------------------
# Anki model
# ----------------------------------------

noun_model = genanki.Model(
    1607392319,
    "French Nouns",

    fields=[
        {"name": "French"},
        {"name": "Article"},
        {"name": "Gender"},
        {"name": "English"},
        {"name": "Image"},
        {"name": "Audio"},
        {"name": "Context"},
        {"name": "Context EN"},
        {"name": "ImageCredit"}
    ],

    templates=[
        {
            "name": "English to French",

            "qfmt": """
                <div class="image">
                    {{Image}}
                </div>
                <div class="image-credit">
                    {{ImageCredit}}
                </div>
                <div class="english">
                    {{English}}
                    <p>{{Context EN}}</p>
                </div>
                <hr>
            """,

            "afmt": """
                <div class="image">
                    {{Image}}
                </div>
                <div class="image-credit">
                    {{ImageCredit}}
                </div>
                <div class="english">
                    {{English}}
                    <p>{{Context EN}}</p>
                </div>
                <hr>
                <div class="french">
                    {{Article}} {{French}}
                    <p> {{Context}} </p>
                </div>
                <div class="audio">
                    {{Audio}}
                </div>
            """
        }
    ],

    css="""
        .card {
            font-family: Arial;
            text-align: center;
            font-size: 30px;
            background-color: white;
            color: black;
            max-width: 100%;
            overflow-x: hidden;
            box-sizing: border-box;
        }
        
        .image {
            width: 100%;
            max-width: 100%;
            overflow: hidden;
            box-sizing: border-box;
        }
        
        .mobile .image {
            width: 75%;
            max-width: 75%;
            overflow: hidden;
            box-sizing: border-box;
            align-items: center;
            margin: 0 auto;
        }

        .image img {
            display: block;
            width: 100% !important;
            max-width: 100% !important;
            height: auto !important;

            margin: 0 auto;
            border-radius: 12px;
            box-sizing: border-box;
        }
        
        .english {
            font-size: 34px;
            font-weight: bold;
            margin: 10px;
            color: #888;
        }
        
        .mobile .english {
            font-size: 28px;
        }

        .french {
            font-size: 40px;
            font-weight: bold;
            margin: 10px;
        }
        
        .mobile .french {
            font-size: 32px;
        }

        p {
            font-size: 20px;
            font-style: italic;
            margin: 20px;
            color: #888;
        }

        .mobile p {
            font-size: 18px;
            font-style: italic;
            margin: 10px;
            color: #888;
        }
        
        .mobile .context {
            font-size: 18px;
        }

        .audio {
            margin: 20px;
        }
        
        textarea {
            width: 100% !important;
            max-width: 100% !important;
            height: auto !important;
        }
        
        .text-field {
            width: 100%;
            max-width: 100%;
            margin: 0 auto;
            text-align: center;
            border: none;
            outline: none;
            background: transparent;
            font-size: 40px;
            font-weight: bold;
            pointer-events: none;
        }
        
        .text-field::placeholder {
            color: #888;
        }
        
        .image-credit {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
            text-align: right;
        }
        
        .mobile .image-credit {
            font-size: 8px;
            color: #999;
            margin-top: 5px;
            text-align: center;
        }
    """
)


# ----------------------------------------
# Verb note and model
# ----------------------------------------
def create_verb_note(card):
    image_html = '<div class="no-image">No image available</div>'
    if card.image_file:
        image_html = f'<img src="{card.image_file}">'

    audio_html = ""
    if card.audio_file:
        audio_html = f"[sound:{card.audio_file.name}]"

    return genanki.Note(
        model=verb_model,
        fields=[
            html.escape(card.infinitive),
            html.escape(card.group_label),
            html.escape(card.english),
            image_html,
            audio_html,
            html.escape(card.context),
            html.escape(card.context_en),
            card.image_credit if card.image_file else "",
        ],
        guid=genanki.guid_for(
            "verb",
            card.infinitive,
            card.english,
            card.context,
            card.context_en,
        ),
    )


verb_model = genanki.Model(
    1607392320,
    "French Verbs",
    fields=[
        {"name": "Infinitive"},
        {"name": "Group"},
        {"name": "English"},
        {"name": "Image"},
        {"name": "Audio"},
        {"name": "Context"},
        {"name": "Context EN"},
        {"name": "ImageCredit"},
    ],
    templates=[
        {
            "name": "English to French Verb",
            "qfmt": """
                <div class="image">
                    {{Image}}
                </div>
                <div class="image-credit">
                    {{ImageCredit}}
                </div>
                <div class="english">
                    {{English}}
                    <p>{{Context EN}}</p>
                </div>
                <hr>
            """,
            "afmt": """
                <div class="image">
                    {{Image}}
                </div>
                <div class="image-credit">
                    {{ImageCredit}}
                </div>
                <div class="english">
                    {{English}}
                    <p>{{Context EN}}</p>
                </div>
                <hr>
                <div class="french">
                    {{Infinitive}}
                    <div class="verb-group">{{Group}}</div>
                    <p>{{Context}}</p>
                </div>
                <div class="audio">
                    {{Audio}}
                </div>
            """,
        }
    ],
    css=noun_model.css + """
        .verb-group {
            margin-top: 4px;
            color: #888;
            font-size: 16px;
            font-weight: normal;
        }

        .mobile .verb-group {
            font-size: 14px;
        }
    """,
)


def create_note(card):
    if isinstance(card, NounCard):
        return create_noun_note(card)

    if isinstance(card, VerbCard):
        return create_verb_note(card)

    raise TypeError(f"Unsupported card type: {type(card).__name__}")
