import sys
from datetime import datetime
from modules import I2C_LCD_driver
from modules.keypad_module import Keypad
from modules.led_module import LEDController
from modules.Fingerprint import FingerPrint
from datetime import datetime
from DataManager import DataManager
import threading
import time


rowPins = [17, 27, 22, 5]
colPins = [23, 24, 25, 16]

lcd = I2C_LCD_driver.lcd()
keypad = Keypad(rowPins, colPins)
finger = FingerPrint()
db = DataManager()

waitingForInput = True
showDatetime = True
pauseThread = False

keyInput = ''
buffer = ''
rootPassword = '3897'

position = None
status = None
waitingForInput = None

condition = threading.Condition()
lcdLock = threading.Lock()
fingerLock = threading.Lock()

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
        
'''
def checkPasscode(passcode):
    return passcode == rootPassword
'''       

def fingerDetect():
    
    global status, position
    
    
    while True:
        time.sleep(1.5)
        with fingerLock:
            status, position = finger.checkFingerExist()
            
def addNewPasscode(rootPasscode, newPasscode):
    rs = checkPasscode(rootPasscode,root=True)    
    if rs:
        return False
    else:
        sql = 'Insert into user_data(passcode) values(?)'
        dataInsert = (newPasscode,)
        return True
def checkPasscode(passcode, root=False):
    if root == False:
        sql = 'select passcode from user_data where passcode = \'' + passcode + '\''
    else:
        sql = 'select passcode from user_data where passcode =  \'' + passcode + '\' and root = 1'
   # print(sql)
    rs = db.executeSql(sql, fetchResult=True)
    
    if rs:
        return True
    else:
        return False
        

    
if __name__ == '__main__':
    
    fingerThread = threading.Thread(target=fingerDetect)
    fingerThread.start()
   
    try:
        while True:   
            pressedKey = passcode()
            
            if status and position != -1:
                finger.detectFinger(position)
                status = None
                position = None
                lcd.lcd_clear()
                lcd.lcd_display_string('Unlock success', 1, 0)
                time.sleep(1.5)
                showDatetime = True
            elif status == False:
                status = None
                position = None
                lcd.lcd_clear()
                lcd.lcd_display_string('Password wrong', 1, 0)
                time.sleep(1.5)
                showDatetime = True
            
            if showDatetime:
                date, currentTime = currentDateTime()
                with lcdLock:
                    lcd.lcd_display_string('Date: '+ date, 1, 0)
                    lcd.lcd_display_string('Time: ' + currentTime, 2, 0)
            
            if pressedKey is not None:
                showDatetime = False
                keyInput += pressedKey
                buffer += '*'
                print('keyInput: ' + keyInput)
                with lcdLock:
                    lcd.lcd_clear()
                    lcd.lcd_display_string('Input passcode:' , 1, 0)
                    lcd.lcd_display_string(buffer, 2, 0)
                
                
                
                
                if keyInput[-1] == 'B': # so sanh ky tu cuoi cung
                    if keyInput[:-1] == '*#*#':
                        lcd.lcd_clear()
                        lcd.lcd_display_string('1.Add 2.Delete F', 1,0)
                        lcd.lcd_display_string('3.Delete U 4.Exist',2,0)
                        
                        startTime = time.time()
                        
                        while True:
                            elapsedTime = time.time() - startTime
                            
                            if elapsedTime >=10:
                                lcd.lcd_clear()
                                showDatetime = True
                                keyInput = ''
                                buffer = ''
                                break
                            
                            pressedKey = passcode()
                            
                            if pressedKey is not None:
                                keyInput = ''
                                newPasscode = ''
                                if pressedKey == '1':
                                    waitingForInput = True
                                    print('menu 1')
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Input new pass: ',1,0)
                                    while waitingForInput:
                                        pressedKey = passcode()
                                        if pressedKey is not None:
                                            if pressedKey == 'B':
                                               newPasscode = keyInput
                                               keyInput = ''
                                               lcd.lcd_clear()
                                               lcd.lcd_display_string('Input root pass:',1,0)
                                               
                                            keyInput += pressedKey
                                            lcd.lcd_display_string(keyInput,2,0)
                                            
                                            
                            
                                   # lcd.lcd_clear()
                                    #showDatetime = True
                                    #keyInput = ''
                                    #buffer = ''
                                    break
                                elif pressedKey == '2':
                                    print('menu 2')
                                    lcd.lcd_clear()
                                    showDatetime = True
                                    keyInput = ''
                                    buffer = ''
                                    break
                                elif pressedKey == '3':
                                    print('menu 3')
                                    lcd.lcd_clear()
                                    showDatetime = True
                                    keyInput = ''
                                    buffer = ''
                                    break
                                elif pressedKey == '4':
                                    print('menu 4')
                                    lcd.lcd_clear()
                                    showDatetime = True
                                    keyInput = ''
                                    buffer = ''
                                    break
                                        
                    
                    elif checkPasscode(keyInput[:-2]) and keyInput[-2] == '#':
                        print('Enroll mode')
                        while status == None:
                            pass
                        
                        if (status == False) and (position == -1):
                            print('Run')
                            finger.enrollFinger()
                            position = None
                            status = None
                        else:
                            keyInput = ''
                            buffer = ''
                            showDatetime = True
                    
                    
                    elif checkPasscode(keyInput[:-1]):    
                        lcd.lcd_clear()
                        lcd.lcd_display_string('Unlock success', 1, 0)
                        time.sleep(1.5)
                        lcd.lcd_clear()
                        
                        keyInput =''
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
                        
                        
            
            if pressedKey == 'C' and pressedKey is not None:
                keyInput = ''
                buffer = ''
                lcd.lcd_clear()
                lcd.lcd_display_string('Input passcode: ',1,0)
            
            
    except KeyboardInterrupt:
        fingerThread.join()
