import sys
from datetime import datetime
from modules import I2C_LCD_driver
from modules.keypad_module import Keypad
from modules.led_module import LEDController
from modules.Fingerprint import FingerPrint
from datetime import datetime

import time
import threading
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
enroll_lock = threading.Lock()
enroll_completed_event = multiprocessing.Event()

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

def fingerPrintService(option='detect'):
    if finger.detectFinger():
        with lcd_lock:
            lcd.lcd_clear()
            lcd.lcd_display_string('Unlock success', 1, 0)
            time.sleep(1.5)
            lcd.lcd_clear()
    else:
        with lcd_lock:
            lcd.lcd_clear()
            lcd.lcd_display_string('Cannot detect', 1, 0)
            lcd.lcd_display_string(' finger', 2, 0)
            time.sleep(1.5)
            lcd.lcd_clear()

def enrollFinger():
    global buffer
    global showDatetime
    with enroll_lock:
        if password + '#' == buffer:
            finger.enrollFinger()
            buffer = ''  # Clear the buffer after enrollment
            showDatetime = True  # Display datetime after enrollment
            with lcd_lock:
                lcd.lcd_clear()
                lcd.lcd_display_string('Enrollment successful', 1, 0)
                time.sleep(1.5)
                lcd.lcd_clear()
        else:
            with lcd_lock:
                lcd.lcd_clear()
                lcd.lcd_display_string('Invalid input', 1, 0)
                time.sleep(1.5)
                lcd.lcd_clear()

def passcodeThread(lock, enroll_completed_event):
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
                elif password + '#' == buffer:
                    threading.Thread(target=enrollFinger).start()  # Start enrollFinger in a new thread
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
    passcode_process = multiprocessing.Process(target=passcodeThread, args=(lcd_lock, enroll_completed_event))
    passcode_process.start()
    
    finger =  multiprocessing.Process(target=fingerPrintService)
    finger.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        passcode_process.terminate()
        lcd.lcd_clear()
        sys.exit()
