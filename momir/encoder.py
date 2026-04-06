from gpiozero import RotaryEncoder, Button


class EncoderWithButton:
    def __init__(self, encoder_a, encoder_b, button_pin, min_value=0, max_value=99):
        self.encoder = RotaryEncoder(
            a=encoder_a,
            b=encoder_b,
            max_steps=0,
            wrap=False,
        )

        self.button = Button(
            button_pin,
            pull_up=True,
            bounce_time=0.1,
        )

        self.value = 0
        self.min_value = min_value
        self.max_value = max_value
        self.last_steps = self.encoder.steps

        self._on_rotate_callback = None
        self._on_press_callback = None

        self.encoder.when_rotated = self._handle_rotate
        self.button.when_pressed = self._handle_press

    def clamp(self, n, low, high):
        return max(low, min(high, n))

    def _handle_rotate(self):
        current_steps = self.encoder.steps
        diff = current_steps - self.last_steps

        if diff == 0:
            return

        self.value = self.clamp(self.value + diff, self.min_value, self.max_value)
        self.last_steps = current_steps

        print(f"Encoder steps={current_steps}, diff={diff}, value={self.value:02d}")

        if self._on_rotate_callback:
            self._on_rotate_callback(self.value)

    def _handle_press(self):
        print(f"Button pressed -> current value: {self.value:02d}")

        if self._on_press_callback:
            self._on_press_callback(self.value)

    def when_rotated(self, callback):
        self._on_rotate_callback = callback

    def when_pressed(self, callback):
        self._on_press_callback = callback
