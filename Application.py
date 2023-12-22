import sys

sys.path.append('/home/thinhtran/smartlock')

from datetime import datetime
from modules import I2C_LCD_driver
from modules.keypad_module import Keypad
from modules.led_module import LEDController
from modules.Fingerprint import FingerPrint

import time


row_pins = [17, 27, 22, 5]
col_pins = [23, 24, 25, 16]

lcd = I2C_LCD_driver.lcd()
finger = FingerPrint(lcd)

finger.enroll()

led = LEDController()


keypad = Keypad(row_pins, col_pins)



waitingForInput = False
enteringPassword = False

buffer = ''
password = '3897'
keyInput = '';





while True:

    key = str(keypad.get_key())

    if key != 'None':
        if key == 'A':
            lcd.lcd_clear()
            lcd.lcd_display_string('Input password:')
            waitingForInput = True
            enteringPassword = True
            buffer = ''
            keyInput = ''
            
        elif key == 'B' and waitingForInput:
            waitingForInput = False
            lcd.lcd_clear()
            if password == buffer[1:]:
                lcd.lcd_display_string('Unlock success', 1, 0)
                led.ledOn()
                time.sleep(3)
                led.ledOff()
                lcd.lcd_display_string('Input password:',1, 0)
            else:
                lcd.lcd_display_string('Password wrong', 1, 0)
                time.sleep(3)
                lcd.lcd_display_string('Input password: ', 1, 0)
                
                
    if waitingForInput and key != 'None':
            keyInput += '*'
            lcd.lcd_display_string(keyInput[1:],2,0)

            buffer += key
            print('Buffer: ' + buffer)
    time.sleep(0.1)
