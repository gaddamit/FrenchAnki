import genanki
import html
from pathlib import Path
import re

BASE_DIR = Path(__file__).parent
AUDIO_DIR = BASE_DIR / "audio"

def safe_filename(text):
    text = re.sub(r"[^a-zA-Z0-9_-]", "_", text)
    return text.lower()

class Card:
    def __init__(self, french, article, gender, english, context, context_en, search_terms, image_file, image_credit, audio_file):
        self.french = french
        self.article = article
        self.gender = gender
        self.english = english
        self.context = context
        self.context_en = context_en
        self.image_file = image_file
        self.image_credit = image_credit
        self.audio_file = audio_file
        self.search_terms = search_terms

    def get_filename(self):
        return safe_filename(self.english)
    
    def create_card(line):
        french, article, gender, english, context, context_en, search_terms = (item.strip() for item in line.split("|", 6))
        return Card(
            french,
            article,
            gender,
            english,
            context,
            context_en,
            search_terms,
            image_file=None,
            image_credit=None,
            audio_file=(AUDIO_DIR / f"{safe_filename(english)}.mp3")
        )

    def print_info(self, index, total):
        print(f"{index}/{total} {self.english} -> {self.french}")


# -------------------------
# Create Anki note
# -------------------------
def create_note(card):
    image_html = None; 
    audio_html = None; 

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
        model=model,

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

model = genanki.Model(
    1607392319,
    "French Vocabulary",

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
            margin: 30px;
            color: #888;
        }
        
        .mobile .english {
            font-size: 28px;
        }

        .french {
            font-size: 40px;
            font-weight: bold;
            margin: 25px;
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