import time

from gpiozero import Device, PWMOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory

from momir.tube_display import CD4511


def main():
    Device.pin_factory = LGPIOFactory()

    pwm = PWMOutputDevice(17, frequency=1000)
    pwm.value = 0.5  # 50% duty cycle

    display = CD4511(a=27, b=22, c=23, d=24, name="ones")

    print("Testing single tube display — counting 0 to 9")

    try:
        for digit in range(10):
            display.display(digit)
            time.sleep(1)
    finally:
        display.clear()
        print("Done")


if __name__ == "__main__":
    main()
