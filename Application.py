import sys
from datetime import datetime
from modules import I2C_LCD_driver
from modules.keypad_module import Keypad
from modules.led_module import LEDController
from modules.Fingerprint import FingerPrint
from datetime import datetime
import multiprocessing
import time

row_pins = [17, 27, 22, 5]
col_pins = [23, 24, 25, 16]

lcd = I2C_LCD_driver.lcd()
finger = FingerPrint()
led = LEDController()
keypad = Keypad(row_pins, col_pins)

waitingForInput = True
showDatetime = True

pauseProcess = multiprocessing.Value('b', False)

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

def fingerPrintDetect():
    global pauseProcess
    while not pauseProcess.value:
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

def passcodeThread():
    global keyInput
    global buffer
    global waitingForInput
    global password
    global showDatetime
    global pauseProcess
    
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
                    print('Enroll mode')
                    with lcd_lock:
                        lcd.lcd_clear()
                        lcd.lcd_display_string('Enroll mode', 1, 0)
                    pauseProcess.value = True
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

if __name__ == '__main__':
    passcode_process = multiprocessing.Process(target=passcodeThread)
    passcode_process.start()

    fingerPrint_process = multiprocessing.Process(target=fingerPrintDetect)
    fingerPrint_process.start()
    
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        pauseProcess.value = True
        passcode_process.join()
        fingerPrint_process.join()
        lcd.lcd_clear()
        sys.exit()
