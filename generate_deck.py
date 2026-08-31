from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
import csv
import html
import json
import edge_tts
import genanki
import requests
from anki_model import Card, create_note
from config import (
    AUDIO_DIR,
    BASE_DIR,
    CATEGORY_DECKS,
    FEMALE_VOICE,
    MALE_VOICE,
    NOUN_CSV_FIELDS,
    NOUNS_DIR,
    OUTPUT_FILE_NAME,
    UNSPLASH_CACHE_FILE,
)

AUDIO_DIR.mkdir(exist_ok=True)


# ----------------------------------------
# Helpers
# ----------------------------------------
def load_csv_cards(csv_file, expected_fields, card_factory):
    if not csv_file.exists():
        raise FileNotFoundError(f"Missing vocabulary file: {csv_file}")

    with open(csv_file, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != expected_fields:
            raise ValueError(
                f"Invalid columns in {csv_file.name}. "
                f"Expected: {', '.join(expected_fields)}"
            )

        cards = []
        for row_number, row in enumerate(reader, start=2):
            missing_fields = [
                field for field in expected_fields
                if not row.get(field, "").strip()
            ]

            if missing_fields:
                raise ValueError(
                    f"Missing value(s) in {csv_file.name}, row {row_number}: "
                    f"{', '.join(missing_fields)}"
                )

            try:
                cards.append(card_factory(row))
            except (KeyError, ValueError) as error:
                raise ValueError(
                    f"Invalid value in {csv_file.name}, row {row_number}: {error}"
                ) from error

    return cards


def load_noun_decks():
    category_cards = []

    for filename, (deck_id, category_name) in CATEGORY_DECKS.items():
        csv_file = NOUNS_DIR / filename
        cards = load_csv_cards(csv_file, NOUN_CSV_FIELDS, Card.from_csv_row)

        deck = genanki.Deck(
            deck_id,
            f"Learn French::Nouns::{category_name}",
        )
        category_cards.append((deck, cards))

    return category_cards


def load_unsplash_cache():
    if not UNSPLASH_CACHE_FILE.exists():
        return {}

    with open(UNSPLASH_CACHE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_unsplash_cache(cache):
    with open(UNSPLASH_CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(cache, file, indent=2, ensure_ascii=False)


def get_unsplash_image(card, cache):
    if card.english in cache:
        print(f"  Using cached Unsplash result for: {card.english}")
        return cache[card.english]

    result = find_unsplash_image(card.search_terms)

    if result:
        track_unsplash_download(result["download_location"])

    cache[card.english] = result
    save_unsplash_cache(cache)

    return result


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
        "content_filter": "high"
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

def track_unsplash_download(download_location):
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")

    response = requests.get(
        download_location,
        headers={
            "Authorization": f"Client-ID {access_key}"
        },
        timeout=20
    )

    response.raise_for_status()

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

async def generate_audio(card):

    voice = FEMALE_VOICE
    if card.gender != "f":
        voice = MALE_VOICE

    voice_ssml = f"\n{card.french}\n\n{card.context}"

    communicate = edge_tts.Communicate(
        voice_ssml,
        voice,
        rate="-10%"
    )

    await communicate.save(
        str(card.audio_file)
    )

# ----------------------------------------
# Main
# ----------------------------------------

async def main():

    media_files = []
    category_cards = load_noun_decks()
    decks = [deck for deck, _ in category_cards]
    total_cards = sum(len(cards) for _, cards in category_cards)

    print(f"Found {total_cards} nouns in {len(decks)} categories.")

    unsplash_cache = load_unsplash_cache()
    index = 0
    for deck, cards in category_cards:
        print(f"\nCategory: {deck.name} ({len(cards)} cards)")

        for card in cards:
            index += 1
            card.print_info(index, total_cards)

            # -------------------------
            # Image
            # -------------------------
            try:
                result = get_unsplash_image(card, unsplash_cache)

                if result:
                    card.image_file = result["image_url"]
                    card.image_credit = (
                        f'Photo by '
                        f'<a href="{result["photographer_url"]}?utm_source=french_vocab_app&utm_medium=referral">'
                        f'{html.escape(result["photographer"])}</a> on '
                        f'<a href="https://unsplash.com/?utm_source=french_vocab_app&utm_medium=referral">'
                        f'Unsplash</a>'
                    )
                else:
                    print("  No image found.")
                    card.image_file = None

            except Exception as e:
                print(f"  Image lookup failed: {e}")
                card.image_file = None

            # -------------------------
            # Audio
            # -------------------------
            print(card.audio_file)
            if card.audio_file.exists():
                print(
                    "  Audio already exists."
                )
            else:
                print(
                    "  Generating French pronunciation..."
                )

                try:
                    await generate_audio(card)

                except Exception as e:
                    print(
                        f"  Audio generation failed: {e}"
                    )

                    card.audio_file = None

            # -------------------------
            # Media
            # -------------------------
            note = create_note(card)
            if card.audio_file:
                media_files.append(str(card.audio_file))

            deck.add_note(note)


    # --------------------------------
    # Export
    # --------------------------------

    print()
    print("Creating Anki package...")

    package = genanki.Package(
        decks
    )

    package.media_files = media_files

    output_file = (
        BASE_DIR / OUTPUT_FILE_NAME
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
    print(f"Categories: {len(decks)}")
    print(f"Cards: {total_cards}")

if __name__ == "__main__":
    asyncio.run(main())
