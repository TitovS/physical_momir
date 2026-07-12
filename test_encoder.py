from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory
from signal import pause
import yaml

from momir.encoder import EncoderWithButton

Device.pin_factory = LGPIOFactory()

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Create encoder
encoder = EncoderWithButton(
    encoder_a=config["encoder"]["encoder_a"],
    encoder_b=config["encoder"]["encoder_b"],
    button_pin=config["encoder"]["button_pin"],
    min_value=config["encoder"]["min_value"],
    max_value=config["encoder"]["max_value"]
)

# Event handlers
def on_rotate(value):
    print(f">>> Value changed to: {value}")

def on_button_press(value):
    print(f">>> BUTTON PRESSED! Current value: {value}")

encoder.when_rotated(on_rotate)
encoder.when_pressed(on_button_press)

print("Encoder test started")
print("Rotate encoder to see value changes")
print("Press button to test button press")
print("Press Ctrl+C to exit")

pause()
