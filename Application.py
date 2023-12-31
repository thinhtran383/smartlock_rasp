import sys
from datetime import datetime
from modules import I2C_LCD_driver
from modules.keypad_module import Keypad
from modules.led_module import LEDController
from modules.Fingerprint import FingerPrint
from datetime import datetime
import threading
import time

row_pins = [17, 27, 22, 5]
col_pins = [23, 24, 25, 16]

lcd = I2C_LCD_driver.lcd()
finger = FingerPrint()
led = LEDController()
keypad = Keypad(row_pins, col_pins)

waitingForInput = True
showDatetime = True
pauseProcess = False

flag: int


buffer = ''
password = '3897'
keyInput = ''

lcd_lock = threading.Lock()
finger_lock = threading.Lock()

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
    global showDatetime
    global flag
    
    while True:
        time.sleep(1)
        if not pauseProcess:
            with finger_lock:
                flag = finger.detectFinger()
                
                
                if flag == 1:
                    with lcd_lock:
                        lcd.lcd_clear()
                        lcd.lcd_display_string('Cannot detect', 1, 0)
                        lcd.lcd_display_string(' 1finger',2, 0)
                        time.sleep(1.5)
                        lcd.lcd_clear()
                        showDatetime = True
                elif flag == 0:
                    with lcd_lock:
                        lcd.lcd_clear()
                        lcd.lcd_display_string('Unlock success', 1, 0)
                        time.sleep(1.5)
                        lcd.lcd_clear()
                        showDatetime = True        
                
                # if finger.detectFinger():
                    # with lcd_lock:
                    #     lcd.lcd_clear()
                    #     lcd.lcd_display_string('Unlock success', 1, 0)
                    #     time.sleep(1.5)
                    #     lcd.lcd_clear()
                    #     showDatetime = True
                        
                        
                # else:
                #     with lcd_lock:
                #         lcd.lcd_clear()
                #         lcd.lcd_display_string('Cannot detect', 1, 0)
                #         lcd.lcd_display_string(' 1finger',2, 0)
                #         time.sleep(1.5)
                #         lcd.lcd_clear()
                #         showDatetime = True
                        

def passcodeThread():
    global keyInput
    global buffer
    global waitingForInput
    global password
    global showDatetime
    global pauseProcess
    global flag


    
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
                    lcd.lcd_clear()
                    lcd.lcd_display_string('Waiting for', 1, 0)
                    lcd.lcd_display_string('finger...', 2, 0)
                    pauseProcess = True
                    
                    
                    if flag == 0 or flag == 1 or hasattr(obj, 'flag'):
                        pass
                    else:
                        with finger_lock:      
                            keyInput = ''
                            buffer = ''
                            status = finger.enrollFinger()   
                            if status == 3:
                                lcd.lcd_clear()
                                lcd.lcd_display_string('Finger enroll', 1, 0)
                                lcd.lcd_display_string('success', 2, 0)
                                time.sleep(1.5)
                                lcd.lcd_clear()
                                
                            elif status == 2:
                                lcd.lcd_clear()
                                lcd.lcd_display_string('Cannot detect', 1, 0)
                                lcd.lcd_display_string('finger 2', 2, 0)
                                time.sleep(1.5)
                                lcd.lcd_clear()
                        
                        showDatetime = True
                        pauseProcess = False
                        # elif status == 1:
                        #     lcd.lcd_clear()
                        #     lcd.lcd_display_string('Finger existed', 1, 0)
                        #     time.sleep(1.5)
                        #     lcd.lcd_clear()
                            
                    
                
                else:
                    with lcd_lock:
                        lcd.lcd_clear()
                        lcd.lcd_display_string('Wrong password', 1, 0)
                        time.sleep(1.5)
                        lcd.lcd_clear()
                    keyInput = ''
                    buffer = ''
                    lcd.lcd_clear()
                    showDatetime = True

        if key == 'C' and waitingForInput:
            with lcd_lock:
                keyInput = ''
                buffer = ''
                lcd.lcd_clear()
                lcd.lcd_display_string('Input password: ', 1, 0)

if __name__ == '__main__':
    passcode_thread = threading.Thread(target=passcodeThread)
    passcode_thread.start()

   # fingerPrint_thread = threading.Thread(target=fingerPrintDetect)
   # fingerPrint_thread.start()
    
    try:
        while True:
            time.sleep(1)
            fingerPrintDetect()
    except KeyboardInterrupt:
        passcode_thread.join()
        fingerPrint_thread.join()
        lcd.lcd_clear()
        sys.exit()
