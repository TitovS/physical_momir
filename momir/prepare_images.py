import asyncio
import json
import urllib.request
from pathlib import Path

import aiohttp

SCRYFALL_BULK_URL = "https://api.scryfall.com/bulk-data"
IMAGES_DIR = Path(__file__).parent / "resources" / "images"

MAX_CONCURRENT_DOWNLOADS = 20


def download_scryfall_bulk_data(output_path: Path) -> list[dict]:
    """Download bulk card data from Scryfall."""
    print("Fetching Scryfall bulk data info...")

    req = urllib.request.Request(SCRYFALL_BULK_URL, headers={
        "User-Agent": "PhysicalMomir/1.0",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req) as response:
        bulk_info = json.loads(response.read().decode("utf-8"))

    default_cards = next(
        (item for item in bulk_info.get("data", []) if item.get("type") == "default_cards"),
        None
    )
    if not default_cards:
        raise RuntimeError("Could not find default_cards bulk data")

    if output_path.exists():
        print(f"Loading existing {output_path}")
        with open(output_path, "r", encoding="utf-8") as f:
            return json.load(f)

    download_url = default_cards["download_uri"]
    print(f"Downloading bulk data (~70MB)...")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(download_url, output_path)

    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_creatures_by_mana_value(cards: list[dict]) -> dict[int, list[dict]]:
    """Extract creatures grouped by mana value (0-16+)."""
    creatures_by_mv = {}
    seen_names = set()

    for card in cards:
        if card.get("digital", False):
            continue
        if card.get("layout") in ("token", "double_faced_token", "emblem", "art_series"):
            continue

        type_line = card.get("type_line", "")
        if "Creature" not in type_line:
            continue

        name = card.get("name", "")
        if name in seen_names:
            continue
        seen_names.add(name)

        mv = min(int(card.get("cmc", 0)), 16)

        image_uris = card.get("image_uris", {})
        if not image_uris:
            faces = card.get("card_faces", [])
            if faces:
                image_uris = faces[0].get("image_uris", {})

        image_url = image_uris.get("normal") or image_uris.get("large")
        if not image_url:
            continue

        if mv not in creatures_by_mv:
            creatures_by_mv[mv] = []

        creatures_by_mv[mv].append({"name": name, "image_url": image_url})

    return creatures_by_mv


async def download_image(session: aiohttp.ClientSession, card: dict, mv: int, semaphore: asyncio.Semaphore) -> bool:
    """Download a single card image."""
    mv_dir = IMAGES_DIR / str(mv)
    mv_dir.mkdir(parents=True, exist_ok=True)

    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in card["name"])
    image_path = mv_dir / f"{safe_name}.jpg"

    if image_path.exists():
        return True

    async with semaphore:
        try:
            async with session.get(card["image_url"]) as response:
                if response.status == 200:
                    image_path.write_bytes(await response.read())
                    return True
                else:
                    print(f"  HTTP {response.status}: {card['name']}")
                    return False
        except Exception as e:
            print(f"  Error: {card['name']}: {e}")
            return False


async def download_all_images(creatures_by_mv: dict[int, list[dict]]):
    """Download all creature images concurrently."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    all_cards = [(card, mv) for mv, cards in creatures_by_mv.items() for card in cards]
    total = len(all_cards)

    print(f"Downloading {total} creature images ({MAX_CONCURRENT_DOWNLOADS} concurrent)...")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
    downloaded = 0
    failed = 0

    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, card, mv, semaphore) for card, mv in all_cards]

        for i, coro in enumerate(asyncio.as_completed(tasks)):
            success = await coro
            if success:
                downloaded += 1
            else:
                failed += 1

            if (i + 1) % 100 == 0:
                print(f"  Progress: {i + 1}/{total}")

    print(f"\nDone! Downloaded: {downloaded}, Failed: {failed}")


def check_data_ready() -> bool:
    """Check if Scryfall JSON and images are downloaded."""
    data_dir = Path(__file__).parent / "resources"
    bulk_path = data_dir / "scryfall_cards.json"

    if not bulk_path.exists():
        print("Scryfall data not found. Run prepare_images.py first.")
        return False

    if not IMAGES_DIR.exists():
        print("Images directory not found. Run prepare_images.py first.")
        return False

    # Check if we have at least some images
    image_count = sum(1 for _ in IMAGES_DIR.rglob("*.jpg"))
    if image_count == 0:
        print("No images found. Run prepare_images.py first.")
        return False

    print(f"Data ready: {image_count} card images available")
    return True


def main():
    data_dir = Path(__file__).parent / "resources"
    bulk_path = data_dir / "scryfall_cards.json"

    cards = download_scryfall_bulk_data(bulk_path)
    creatures_by_mv = get_creatures_by_mana_value(cards)

    for mv in sorted(creatures_by_mv.keys()):
        print(f"MV {mv}: {len(creatures_by_mv[mv])} creatures")

    total = sum(len(c) for c in creatures_by_mv.values())
    print(f"\nTotal creatures: {total}")

    response = input("\nDownload all images? (y/n): ")
    if response.lower() == "y":
        asyncio.run(download_all_images(creatures_by_mv))


if __name__ == "__main__":
    main()
