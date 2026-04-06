from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter
from thermalprinter import ThermalPrinter

MAX_WIDTH = 384


class Printer:
    def __init__(self, port="/dev/serial0", baudrate=9600):
        self.printer = ThermalPrinter(port=port, baudrate=baudrate)

    def print_card(self, image_path: Path):
        """Print a card image with optimized settings for thermal printer."""
        print(f"Printing: {image_path.stem}")

        img = Image.open(image_path).convert("L")

        # Resize to fit printer width
        if img.width > MAX_WIDTH:
            img = img.resize((MAX_WIDTH, int(img.height * MAX_WIDTH / img.width)))

        # Enhance contrast
        img = ImageEnhance.Contrast(img).enhance(2.0)

        # Sharpen
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        img.filename = "this_is_a_dirty_fix.jpg"
        # Threshold to black/white (no dithering)
        img = img.point(lambda x: 0 if x < 150 else 255, "1")

        # Print
        self.printer.feed(1)
        self.printer.image(img)
        self.printer.feed(5)

    def close(self):
        self.printer.close()
