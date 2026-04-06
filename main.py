from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory
from signal import pause

from momir.tube_display import CD4511, TwoDigitDisplay
from momir.encoder import EncoderWithButton
from momir.print import Printer
from momir.cards import CardPool
from momir.prepare_images import check_data_ready, main as download_images

Device.pin_factory = LGPIOFactory()


# ----- Check data -----
if not check_data_ready():
    print("\nStarting image download...")
    download_images()
    if not check_data_ready():
        raise RuntimeError("Failed to download card data")


# ----- Displays -----
tens_display = CD4511(
    a=20,
    b=26,
    c=21,
    d=16,
    name="tens"
)

ones_display = CD4511(
    a=13,
    b=5,
    c=6,
    d=12,
    name="ones"
)

display = TwoDigitDisplay(tens_display, ones_display)


# ----- Encoder + Button -----
encoder = EncoderWithButton(
    encoder_a=23,
    encoder_b=24,
    button_pin=22,
    min_value=0,
    max_value=99
)


# ----- Thermal printer -----
printer = Printer()

# ----- Card pool -----
card_pool = CardPool()


# ----- Event handlers -----
def on_rotate(value):
    display.display(value)


def on_button_press(mana_value):
    card_path = card_pool.get_random_card(mana_value)
    if card_path:
        printer.print_card(card_path)
    else:
        print(f"No creatures found for mana value {mana_value}")


encoder.when_rotated(on_rotate)
encoder.when_pressed(on_button_press)

# Show initial value
display.display(encoder.value)

print("Ready")
print("Rotate to select mana value (0-16)")
print("Press button to print random creature")

pause()
