from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory
from signal import pause
import yaml

from momir.tube_display import CD4511, TwoDigitDisplay
from momir.encoder import EncoderWithButton
from momir.print import Printer
from momir.cards import CardPool
from momir.prepare_images import check_data_ready, main as download_images

Device.pin_factory = LGPIOFactory()

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


# ----- Check data -----
if not check_data_ready():
    print("\nStarting image download...")
    download_images()
    if not check_data_ready():
        raise RuntimeError("Failed to download card data")


# ----- Displays -----
tens_display = CD4511(
    a=config["tubes"]["tens_display"]["a"],
    b=config["tubes"]["tens_display"]["b"],
    c=config["tubes"]["tens_display"]["c"],
    d=config["tubes"]["tens_display"]["d"],
    name="tens"
)

ones_display = CD4511(
    a=config["tubes"]["ones_display"]["a"],
    b=config["tubes"]["ones_display"]["b"],
    c=config["tubes"]["ones_display"]["c"],
    d=config["tubes"]["ones_display"]["d"],
    name="ones"
)

display = TwoDigitDisplay(tens_display, ones_display, config["tubes"]["pwm"])


# ----- Encoder + Button -----
encoder = EncoderWithButton(
    encoder_a=config["encoder"]["encoder_a"],
    encoder_b=config["encoder"]["encoder_b"],
    button_pin=config["encoder"]["button_pin"],
    min_value=config["encoder"]["min_value"],
    max_value=config["encoder"]["max_value"]
)


# ----- Thermal printer -----
printer = Printer(
    port=config["printer"]["port"],
    baudrate=config["printer"]["baudrate"]
)

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
