import RPi.GPIO as GPIO
import time

class LEDController:
    def __init__(self, pin=21):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, 0)

    def ledOn(self):
        GPIO.output(self.pin, 1)
      

    def ledOff(self):
        GPIO.output(self.pin, 0)

    def cleanup(self):
        GPIO.cleanup()

if __name__ == "__main__":
  
    led_controller = LEDController()
    led_controller.ledOn()
    time.sleep(5)
    led_controller.ledOff()
    led_controller.cleanup()

