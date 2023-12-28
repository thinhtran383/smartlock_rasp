import sys
from datetime import datetime
from modules import I2C_LCD_driver
from modules.keypad_module import Keypad
from modules.led_module import LEDController
from modules.Fingerprint import FingerPrint
from datetime import datetime

import time
import multiprocessing

row_pins = [17, 27, 22, 5]
col_pins = [23, 24, 25, 16]

lcd = I2C_LCD_driver.lcd()
finger = FingerPrint()
led = LEDController()
keypad = Keypad(row_pins, col_pins)

waitingForInput = True
showDatetime = True

buffer = ''
password = '3897'
keyInput = ''

lcd_lock = multiprocessing.Lock()

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

def fingerPrintProcess(lock):
    while True:
        if finger.detectFinger():
            with lock:
                lcd.lcd_clear()
                lcd.lcd_display_string('Unlock success', 1, 0)
                time.sleep(1.5)
                lcd.lcd_clear()
        else:
            with lock:
                lcd.lcd_clear()
                lcd.lcd_display_string('Cannot detect', 1, 0)
                lcd.lcd_display_string(' finger', 2, 0)
                time.sleep(1.5)
                lcd.lcd_clear()

def passcodeThread(lock):
    global keyInput
    global buffer
    global waitingForInput
    global password
    global showDatetime

    while True:
        if showDatetime:
            with lock:
                lcd.lcd_display_string('Date: ' + currentDate(), 1, 0)
                lcd.lcd_display_string(currentTime(), 2, 6)

        key = str(keypad.get_key())

        if waitingForInput and key != 'None' and key != 'B':
            showDatetime = False
            with lock:
                lcd.lcd_clear()
                lcd.lcd_display_string('Input password: ', 1, 0)
                keyInput += '*'
                lcd.lcd_display_string(keyInput, 2, 0)
                buffer += key
                print('Buffer: ' + buffer)

        if key == 'B':
            if waitingForInput:
                if password == buffer:
                    with lock:
                        lcd.lcd_clear()
                        lcd.lcd_display_string('Unlock success', 1, 0)
                        time.sleep(1.5)
                        lcd.lcd_clear()
                    keyInput = ''
                    buffer = ''
                    showDatetime = True
                else:
                    with lock:
                        lcd.lcd_clear()
                        lcd.lcd_display_string('Wrong password', 1, 0)
                        time.sleep(1.5)
                        lcd.lcd_clear()
                    keyInput = ''
                    buffer = ''
                    showDatetime = True

        if key == 'C' and waitingForInput:
            with lock:
                keyInput = ''
                buffer = ''
                lcd.lcd_clear()
                lcd.lcd_display_string('Input password: ', 1, 0)

if __name__ == '__main__':
    finger_process = multiprocessing.Process(target=fingerPrintProcess, args=(lcd_lock,))
    finger_process.start()

    passcode_process = multiprocessing.Process(target=passcodeThread, args=(lcd_lock,))
    passcode_process.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        finger_process.terminate()
        passcode_process.terminate()
        lcd.lcd_clear()
        sys.exit()
