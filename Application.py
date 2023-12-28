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

lcd_lock = multiprocessing.Lock()
stopFingerEvent = multiprocessing.Event()

password = '3897'
keyInput = ''

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

def fingerPrintDetect(stop_event):
    while not stop_event.is_set():
        if finger.detectFinger():
            with lcd_lock:
                lcd.lcd_clear()
                lcd.lcd_display_string('Finger detected', 1, 0)

finger_detect_process = multiprocessing.Process(target=fingerPrintDetect, args=(stopFingerEvent,))
finger_detect_process.start()

def passcodeThread():
    global keyInput

    while True:
        with lcd_lock:
            lcd.lcd_display_string('Date: ' + currentDate(), 1, 0)
            lcd.lcd_display_string(currentTime(), 2, 6)

        key = str(keypad.get_key())

        if key != 'None' and key != 'B':
            with lcd_lock:
                lcd.lcd_clear()
                lcd.lcd_display_string('Input password: ', 1, 0)
                keyInput += '*'
                lcd.lcd_display_string(keyInput, 2, 0)

        if key == 'B':
            if password == keyInput:
                with lcd_lock:
                    lcd.lcd_clear()
                    lcd.lcd_display_string('Unlock success', 1, 0)
                    time.sleep(1.5)
                    lcd.lcd_clear()
                keyInput = ''
            else:
                with lcd_lock:
                    lcd.lcd_clear()
                    lcd.lcd_display_string('Wrong password', 1, 0)
                    time.sleep(1.5)
                    lcd.lcd_clear()
                keyInput = ''

        time.sleep(0.1)

# Sử dụng multiprocessing.Process để tạo một quá trình mới cho passcodeThread
passcode_process = multiprocessing.Process(target=passcodeThread)
passcode_process.start()

try:
    # Chờ để chương trình chạy
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Khi nhấn Ctrl+C, kết thúc chương trình
    stopFingerEvent.set()  # Đặt sự kiện để dừng quá trình fingerPrintDetect
    finger_detect_process.join()
    passcode_process.join()
