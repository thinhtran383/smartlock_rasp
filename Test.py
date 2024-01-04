import sys
from datetime import datetime
from modules import I2C_LCD_driver
from modules.keypad_module import Keypad
from modules.led_module import LEDController
from modules.Fingerprint import FingerPrint
from datetime import datetime
import threading
import time

rowPins = [17, 27, 22, 5]
colPins = [23, 24, 25, 16]

lcd = I2C_LCD_driver.lcd()
keypad = Keypad(rowPins, colPins)
finger = FingerPrint()

waitingForInput = True
showDatetime = True
pauseThread = False

keyInput = ''
buffer = ''
rootPassword = '3897'

condition = threading.Condition()
lcdLock = threading.Lock()
fingerprintLock = finger.fingerprint_lock

def currentDateTime():
    currentTime = datetime.now()

    dateFormat = '%d-%m-%y'
    timeFormat = '%H:%M:%S'

    formattedDate = currentTime.strftime(dateFormat)
    formattedTime = currentTime.strftime(timeFormat)

    return formattedDate, formattedTime

def passcode():
    key = str(keypad.get_key())
    return key if key != 'None' else None

def checkPasscode(passcode):
    return passcode == rootPassword

def fingerDetect():
    global pauseThread
    global showDatetime
    global buffer
    global keyInput

    while True:
        with condition:
            while pauseThread:
                condition.wait()

            with fingerprintLock:
                status = finger.detectFinger()

            if status == 0:
                with lcdLock:
                    lcd.lcd_clear()
                    lcd.lcd_display_string('Cannot detect', 1, 0)
                    lcd.lcd_display_string('finger', 2, 0)
                    time.sleep(1.5)

            if status == 1:
                with lcdLock:
                    lcd.lcd_clear()
                    lcd.lcd_display_string('Unlock success', 1, 0)
                    time.sleep(1.5)

            if keyInput.endswith('#B'):
                # Nếu người dùng nhập đúng mật khẩu root và nhấn 'B'
                with fingerprintLock:
                    result = finger.enrollFinger()

                    if result == 3:
                        with lcdLock:
                            lcd.lcd_clear()
                            lcd.lcd_display_string('Finger enrolled!', 1, 0)
                            time.sleep(1.5)
                            lcd.lcd_clear()
                            keyInput = ''
                            buffer = ''
                            showDatetime = True
                    elif result == 2:
                        with lcdLock:
                            lcd.lcd_clear()
                            lcd.lcd_display_string('Enrollment failed', 1, 0)
                            time.sleep(1.5)
                            lcd.lcd_clear()
                            keyInput = ''
                            buffer = ''
                            showDatetime = True

            showDatetime = True
            buffer = ''
            keyInput = ''

if __name__ == '__main__':
    fingerThread = threading.Thread(target=fingerDetect)
    fingerThread.start()

    try:
        while True:
            pressedKey = passcode()

            if showDatetime:
                date, currentTime = currentDateTime()
                with lcdLock:
                    lcd.lcd_display_string('Date: ' + date, 1, 0)
                    lcd.lcd_display_string('Time: ' + currentTime, 2, 0)

            if pressedKey is not None:
                showDatetime = False
                keyInput += pressedKey
                buffer += '*'
                print('keyInput: ' + keyInput)
                with lcdLock:
                    lcd.lcd_clear()
                    lcd.lcd_display_string('Input passcode:', 1, 0)
                    lcd.lcd_display_string(buffer, 2, 0)

                if keyInput[-1] == 'B':
                    if checkPasscode(keyInput[:-1]):
                        lcd.lcd_clear()
                        lcd.lcd_display_string('Unlock success', 1, 0)
                        time.sleep(1.5)
                        lcd.lcd_clear()

                        keyInput = ''
                        buffer = ''
                        showDatetime = True
                    else:
                        lcd.lcd_clear()
                        lcd.lcd_display_string('Passcode wrong!!!', 1, 0)
                        time.sleep(1.5)
                        lcd.lcd_clear()

                        keyInput = ''
                        buffer = ''
                        showDatetime = True

            if pressedKey == '*' and pressedKey is not None:
                pauseThread = True

            if pressedKey == '#' and pressedKey is not None:
                pauseThread = False
                with condition:
                    condition.notify_all()

            if pressedKey == 'C' and pressedKey is not None:
                keyInput = ''
                buffer = ''
                lcd.lcd_clear()
                lcd.lcd_display_string('Input passcode: ', 1, 0)

    except KeyboardInterrupt:
        fingerThread.join()
