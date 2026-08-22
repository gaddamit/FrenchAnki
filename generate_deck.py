from dotenv import load_dotenv
import os

load_dotenv()

import asyncio
import html
import re
from pathlib import Path
import os
import edge_tts
import genanki
import requests


BASE_DIR = Path(__file__).parent

WORDS_FILE = BASE_DIR / "words.txt"
IMAGE_DIR = BASE_DIR / "images"
AUDIO_DIR = BASE_DIR / "audio"

IMAGE_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

FEMALE_VOICE = "fr-FR-DeniseNeural"
MALE_VOICE = "fr-FR-HenriNeural"


# ----------------------------------------
# Helpers
# ----------------------------------------

def safe_filename(text):
    text = re.sub(r"[^a-zA-Z0-9_-]", "_", text)
    return text.lower()


def find_unsplash_image(search_term):

    print(f"  Searching Unsplash for: {search_term}")

    access_key = os.getenv("UNSPLASH_ACCESS_KEY")

    if not access_key:
        raise RuntimeError(
            "UNSPLASH_ACCESS_KEY is not set in .env"
        )

    url = "https://api.unsplash.com/search/photos"

    params = {
        "query": search_term,
        "per_page": 10,
        "orientation": "squarish",
    }

    headers = {
        "Authorization": f"Client-ID {access_key}"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    results = data.get("results", [])

    if not results:
        return None

    # First result
    photo = results[0]

    return {
        "image_url": photo["urls"]["regular"],
        "photographer": photo["user"]["name"],
        "photographer_url": photo["user"]["links"]["html"],
        "photo_url": photo["links"]["html"],
        "download_location": photo["links"]["download_location"],
    }


def download_image(url, output_path):

    print("  Downloading image...")

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    with open(output_path, "wb") as file:
        file.write(response.content)


# ----------------------------------------
# Text-to-speech
# ----------------------------------------

async def generate_audio(text, gender, output_file):

    voice = FEMALE_VOICE if gender == "f" else MALE_VOICE

    communicate = edge_tts.Communicate(
        text,
        voice
    )

    await communicate.save(
        str(output_file)
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
        {"name": "Context"}
    ],

    templates=[
        {
            "name": "English to French",

            "qfmt": """
                <div class="image">
                    {{Image}}
                </div>

                <div class="english">
                    {{English}}
                </div>
            """,

            "afmt": """
                {{FrontSide}}

                <hr>

                <div class="french">
                    {{Article}} {{French}}
                </div>
                <div class="context">
                    {{Context}}
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
        }

        .image img {
            max-width: 500px;
            max-height: 450px;
            border-radius: 12px;
        }

        .english {
            font-size: 40px;
            font-weight: bold;
            margin: 30px;
            color: #888;
        }

        .french {
            font-size: 44px;
            font-weight: bold;
            margin: 25px;
        }
        
        .context {
            font-size: 24px;
            font-style: italic;
            margin: 20px;
            color: #888;
        }

        .audio {
            margin: 20px;
        }
    """
)


deck = genanki.Deck(
    2059400110,
    "French Vocabulary"
)


# ----------------------------------------
# Main
# ----------------------------------------

async def main():

    media_files = []

    with open(
        WORDS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        words = []

        for line in file:

            line = line.strip()

            if not line:
                continue

            french, article, gender, english, context = line.split("|", 4)

            words.append(
                (
                    french.strip(),
                    article.strip(),
                    gender.strip(),
                    english.strip(),
                    context.strip()
                )
            )


    print(f"Found {len(words)} words.")

    for index, (french, article, gender, english, context) in enumerate(words, 1):

        print(
            f"[{index}/{len(words)}] {french} → {english}"
        )

        filename = safe_filename(english)

        image_file = (
            IMAGE_DIR / f"{filename}.jpg"
        )

        audio_file = (
            AUDIO_DIR / f"{filename}.mp3"
        )


        # -------------------------
        # Image
        # -------------------------

        if image_file.exists():
            print("  Image already exists.")
        else:
            result = find_unsplash_image(english)

            if result:

                try:

                    download_image(
                        result["image_url"],
                        image_file
                    )

                    image_credit = (
                        f'Photo by '
                        f'<a href="{result["photographer_url"]}">'
                        f'{result["photographer"]}'
                        f'</a> on '
                        f'<a href="https://unsplash.com/">Unsplash</a>'
                    )

                except Exception as e:

                    print(f"  Image download failed: {e}")
                    image_file = None
            else:
                result = find_unsplash_image(english)
                
                if result:
    
                    try:
    
                        download_image(
                            result["image_url"],
                            image_file
                        )
    
                        image_credit = (
                            f'Photo by '
                            f'<a href="{result["photographer_url"]}">'
                            f'{result["photographer"]}'
                            f'</a> on '
                            f'<a href="https://unsplash.com/">Unsplash</a>'
                        )
    
                    except Exception as e:
    
                        print(f"  Image download failed: {e}")
                        image_file = None
                else:
                    print("  No image found.")
                    image_file = None


        # -------------------------
        # Audio
        # -------------------------

        if audio_file.exists():

            print(
                "  Audio already exists."
            )

        else:

            print(
                "  Generating French pronunciation..."
            )

            try:

                await generate_audio(
                    french,
                    gender,
                    audio_file
                )

            except Exception as e:

                print(
                    f"  Audio generation failed: {e}"
                )

                audio_file = None


        # -------------------------
        # Media
        # -------------------------

        image_html = ""

        if image_file:

            image_html = (
                f'<img src="{image_file.name}">'
            )

            media_files.append(
                str(image_file)
            )
        else:
            image_html = (
                f'<div class="no-image">'
                f'No image available'
                f'</div>'
            )

        audio_html = ""

        if audio_file:

            audio_html = (
                f"[sound:{audio_file.name}]"
            )

            media_files.append(
                str(audio_file)
            )


        # -------------------------
        # Create Anki note
        # -------------------------

        note = genanki.Note(
            model=model,

            fields=[
                html.escape(french),
                html.escape(article),
                html.escape(gender),
                html.escape(english),
                image_html,
                audio_html,
                html.escape(context)
            ],

            guid=genanki.guid_for(
                french,
                article,    
                gender,
                english,
                context
            )
        )

        deck.add_note(note)


    # --------------------------------
    # Export
    # --------------------------------

    print()
    print("Creating Anki package...")

    package = genanki.Package(
        deck
    )

    package.media_files = media_files

    output_file = (
        BASE_DIR /
        "FrenchVocabulary.apkg"
    )

    package.write_to_file(
        output_file
    )

    print()
    print("=" * 50)
    print("DONE!")
    print("=" * 50)
    print()
    print(f"Deck: {output_file}")
    print(f"Cards: {len(words)}")


asyncio.run(main())