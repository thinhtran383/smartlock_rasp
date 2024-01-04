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

waitingForInput = True
showDatetime = True

keyInput = ''
buffer = ''
rootPassword = '3897'

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
    if passcode == rootPassword:
        lcd.lcd_clear()
        lcd.lcd_display_string('Unlock success', 1, 0)
        time.sleep(1)
        lcd.lcd_clear()
    else:
        lcd.lcd_clear()
        lcd.lcd_display_string('Password wrong!!', 1, 0)
        time.sleep(1)
        lcd.lcd_clear()
        
    
    

if __name__ == '__main__':
    while True:   
        pressedKey = passcode()
        
        if showDatetime:
            date, time = currentDateTime()
            lcd.lcd_display_string('Date: '+ date, 1, 0)
            lcd.lcd_display_string('Time: ' + time, 2, 0)
        
        if pressedKey is not None:
            showDatetime = False
            keyInput += pressedKey
            buffer += '*'
            
            lcd.lcd_clear()
            lcd.lcd_display_string(buffer, 1, 0)
            
            if keyInput[-1] == 'B':
                checkPasscode(keyInput[:-1])
                keyInput = ''
                showDatetime = True
            
            