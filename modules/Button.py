import RPi.GPIO as GPIO
import time


BUTTON_PIN = 21
GPIO.setmode(GPIO.BCM)

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


while True:
    time.sleep(0.1)
    if GPIO.input(BUTTON_PIN) == GPIO.LOW:
        print('press')
    else:
        print('not press')
        
GPIO.cleanup()