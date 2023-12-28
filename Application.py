import sys
from datetime import datetime
from modules import I2C_LCD_driver
from modules.keypad_module import Keypad
from modules.led_module import LEDController
from modules.Fingerprint import FingerPrint
from datetime import datetime

import time
import threading

row_pins = [17, 27, 22, 5]
col_pins = [23, 24, 25, 16]

lcd = I2C_LCD_driver.lcd()
finger = FingerPrint()
led = LEDController()
keypad = Keypad(row_pins, col_pins)

waitingForInput = True
showDatetime = True

stopFingerThread = False

buffer = ''
password = '3897'
keyInput = ''

lcd_lock = threading.Lock()

def currentDate():
    currentTime = datetime.now()
    dateFormat = '%d-%m-%y'
    formattedDate = currentTime.strftime(dateFormat)
    return f'{formattedDate}'

def currentTime():
    currentTime = datetime.now()
    timeFormat = '%H:%M:%S'
    formattedTime = currentTime.strftime(timeFormat)
    return f'{formattedTime}'

def fingerPrintThread():
    global stopFingerThread

    while not stopFingerThread:
        if finger.detectFinger():
            with lcd_lock:
                lcd.lcd_clear()
                lcd.lcd_display_string('Unlock succes', 1, 0)
                time.sleep(1.5)
                lcd.lcd_clear()
        else:
            with lcd_lock:
                lcd.lcd_clear()
                lcd.lcd_display_string('Cannot detect',1, 0)
                lcd.lcd_display_string(' finger', 2, 0)
                time.sleep(1.5)
                lcd.lcd_clear()

finger_thread = threading.Thread(target=fingerPrintThread, daemon=True)
finger_thread.start()

def passcodeThread():
    global keyInput
    global buffer
    global waitingForInput
    global password
    global showDatetime
    global stopFingerThread

    while True:
        if showDatetime:
            with lcd_lock:
                lcd.lcd_display_string('Date: ' + currentDate(), 1, 0)
                lcd.lcd_display_string(currentTime(), 2, 6)

        key = str(keypad.get_key())

        if waitingForInput and key != 'None' and key != 'B':
            showDatetime = False
            with lcd_lock:
                lcd.lcd_clear()
                lcd.lcd_display_string('Input password: ', 1, 0)
                keyInput += '*'
                lcd.lcd_display_string(keyInput, 2, 0)
                buffer += key
                print('Buffer: ' + buffer)

        if key == 'B':
            if waitingForInput:
                if password == buffer:
                    with lcd_lock:
                        lcd.lcd_clear()
                        lcd.lcd_display_string('Unlock success', 1, 0)
                        time.sleep(1.5)
                        lcd.lcd_clear()
                    keyInput = ''
                    buffer = ''
                    showDatetime = True
                elif password + '#' == buffer:
                    with lcd_lock:
                        lcd.lcd_clear()
                        stopFingerThread = True
                        finger_thread.join()
                        print('fingerThread has stopped')
                        finger.enrollFinger()
                    stopFingerThread = False
                    keyInput = ''
                    buffer = ''
                else:
                    with lcd_lock:
                        lcd.lcd_clear()
                        lcd.lcd_display_string('Wrong password', 1, 0)
                        time.sleep(1.5)
                        lcd.lcd_clear()
                    keyInput = ''
                    buffer = ''
                    showDatetime = True

        if key == 'C' and waitingForInput:
            with lcd_lock:
                keyInput = ''
                buffer = ''
                lcd.lcd_clear()
                lcd.lcd_display_string('Input password: ', 1, 0)

passcode_thread = threading.Thread(target=passcodeThread, daemon=True)
passcode_thread.start()


