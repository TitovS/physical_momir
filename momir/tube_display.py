from gpiozero import OutputDevice


class CD4511:
    def __init__(self, a, b, c, d, name="display"):
        self.name = name
        self.pins = [
            OutputDevice(a),  # A
            OutputDevice(b),  # B
            OutputDevice(c),  # C
            OutputDevice(d),  # D
        ]

    def display(self, num):
        if not (0 <= num <= 9):
            raise ValueError("Only digits 0-9 supported")

        bits = []
        for i in range(4):
            bit = (num >> i) & 1
            bits.append(bit)
            if bit:
                self.pins[i].on()
            else:
                self.pins[i].off()

        print(
            f"{self.name}: {num} | "
            f"D C B A = {bits[3]} {bits[2]} {bits[1]} {bits[0]}"
        )

    def clear(self):
        for pin in self.pins:
            pin.off()


class TwoDigitDisplay:
    def __init__(self, tens, ones):
        self.tens = tens
        self.ones = ones

    def display(self, num):
        if not (0 <= num <= 99):
            raise ValueError("Only numbers 0-99 supported")

        tens_digit = num // 10
        ones_digit = num % 10

        self.tens.display(tens_digit)
        self.ones.display(ones_digit)

        print(f"Number shown: {num:02d}")

    def clear(self):
        self.tens.clear()
        self.ones.clear()
