import random
from pathlib import Path


IMAGES_DIR = Path(__file__).parent / "resources" / "images"


class CardPool:
    """Pool of creature cards organized by mana value."""

    def __init__(self):
        self._cards_by_mv: dict[int, list[Path]] = {}
        self._load_cards()

    def _load_cards(self):
        """Load all card image paths from the images directory."""
        if not IMAGES_DIR.exists():
            raise RuntimeError("Images directory not found. Run prepare_images.py first.")

        for mv_dir in IMAGES_DIR.iterdir():
            if not mv_dir.is_dir():
                continue

            try:
                mv = int(mv_dir.name)
            except ValueError:
                continue

            cards = list(mv_dir.glob("*.jpg"))
            if cards:
                self._cards_by_mv[mv] = cards

        if not self._cards_by_mv:
            raise RuntimeError("No cards found. Run prepare_images.py first.")

        total = sum(len(cards) for cards in self._cards_by_mv.values())
        print(f"CardPool loaded: {total} creatures across MV 0-{max(self._cards_by_mv.keys())}")

    def get_random_card(self, mana_value: int) -> Path | None:
        """Get a random card image path for the given mana value."""
        # Cap mana value at 16
        mv = min(mana_value, 16)

        cards = self._cards_by_mv.get(mv)
        if not cards:
            return None

        return random.choice(cards)

    def get_available_mana_values(self) -> list[int]:
        """Get list of mana values that have cards available."""
        return sorted(self._cards_by_mv.keys())

    def get_card_count(self, mana_value: int) -> int:
        """Get number of cards available for a mana value."""
        mv = min(mana_value, 16)
        return len(self._cards_by_mv.get(mv, []))
