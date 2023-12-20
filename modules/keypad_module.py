import RPi.GPIO as GPIO
import time

class Keypad:
    def __init__(self, row_pins, col_pins):
        self.row_pins = row_pins
        self.col_pins = col_pins
        self.rows = len(row_pins)
        self.cols = len(col_pins)
        self.keys = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['*', '0', '#', 'D']
        ]

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(row_pins, GPIO.OUT)
        GPIO.setup(col_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def get_key(self):
        key = None
        for i in range(self.rows):
            GPIO.output(self.row_pins[i], GPIO.LOW)
            for j in range(self.cols):
                if GPIO.input(self.col_pins[j]) == GPIO.LOW:
                    key = self.keys[i][j]
                    while GPIO.input(self.col_pins[j]) == GPIO.LOW:
                        time.sleep(0.1)
            GPIO.output(self.row_pins[i], GPIO.HIGH)
        return key

    def cleanup(self):
        GPIO.cleanup()

if __name__ == "__main__":
    try:
        row_pins = [17, 27, 22, 5]
        col_pins = [23, 24, 25, 16]

        keypad = Keypad(row_pins, col_pins)

        while True:
            key = keypad.get_key()
            if key:
                print(f'Pressed key: {key}')
                # You can add your own logic here based on the pressed key

    except KeyboardInterrupt:
        keypad.cleanup()
