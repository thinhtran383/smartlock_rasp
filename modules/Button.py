import RPi.GPIO as GPIO
import time


class Button:
    def __init__(self, buttonPin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.buttonPin = buttonPin
        
    def checkButtonState(self):
        buttonState = GPIO.input(self.buttonPin)
        if buttonState == GPIO.LOW:
            print('Button is pressed')
            return True
        
        return False
'''

button = Button(20)

while True:
    button.checkButtonState()
    time.sleep(0.1)
    '''