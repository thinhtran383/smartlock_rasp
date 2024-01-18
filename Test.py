
from datetime import datetime
from modules import I2C_LCD_driver
from modules.keypad_module import Keypad
from modules.led_module import LEDController
from modules.Fingerprint import FingerPrint
from datetime import datetime
from DataManager import DataManager
from functions.MqttSub import MQTTHandler


import threading
import time

# Define mqtt broker
brokerAddress = '0.tcp.ap.ngrok.io'
port = 17753
topic = '#'
led = LEDController()
mqtt = MQTTHandler(brokerAddress, port, topic)

# Define pin for keypad
rowPins = [17, 27, 22, 5]
colPins = [23, 24, 25, 16]


# Define variable module
lcd = I2C_LCD_driver.lcd()
keypad = Keypad(rowPins, colPins)
finger = FingerPrint()
db = DataManager()
led = LEDController()

# Define status
showDatetime = True
pauseThread = False

keyInput = ''
buffer = ''
rootPassword = '3897'

position = None
status = None
waitingForInput = None


# Locking thread
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
    root = checkPasscode(rootPasscode,root=True)    
    new = checkPasscode(newPasscode)
    
    print('add root: ' + str(root))
    print('add new: ' + str(new))

    if root:
        if new == False:
            sql = 'insert into user_data(passcode) values(?)'
            sqlValues = (newPasscode,)
            db.executeSql(sql, sqlValues)
            return True
    
    return False
    
    
def checkPasscode(passcode, root=False):
    if root == False:
        sql = 'select passcode from user_data where passcode = \'' + passcode + '\''
    else:
        sql = 'select passcode from user_data where passcode =  \'' + passcode + '\' and root = 1'
    rs = db.executeSql(sql, fetchResult=True)
    
    
    
    if rs:
        return True
    else:
        return False

def deleteUser(passcode):
    sql = 'delete from user_data where passcode = ? and root = 0'
    sqlValues = (passcode,)
    db.executeSql(sql, sqlValues)
    
def addNewFinger(passcode, position):
        print(passcode, position)
        sql = 'update user_data set finger = ? where passcode = ?'
        sqlValues = (position, passcode,)
        rs = db.executeSql(sql, sqlValues)

def checkFingerExist(passcode):
    '''True:
        
'''
    
    sqlSelect = 'select finger from user_data where passcode = \'' + passcode + '\''
    rs = db.executeSql(sqlSelect, fetchResult=True)
    
    
    rsStr = (str(rs[0])) if rs[0] is not None else 'None'
    
    print(rsStr)
    
    if rsStr == '(None,)':
        return True
    else:
        return False

def deleteFinger(passcode):
    
    
    sqlGetPosition = 'select finger from user_data where passcode = ?'
    sqlValues = (passcode,)  
    rs = db.executeSql(sqlGetPosition, sqlValues, fetchResult=True)
    number = rs[0][0]
    
    if number is not None:    
        with fingerLock:
            finger.deleteFinger(int(number))
    

    sql = 'update user_data set finger = ? where passcode = ?'
    values = (None, passcode,)
    db.executeSql(sql, values)



if __name__ == '__main__':   
    fingerThread = threading.Thread(target=fingerDetect)
    fingerThread.start()
    mqtt.connect()
    
    try:
        while True:
            pressedKey = passcode()
            
            if mqtt.message is not None:
                if mqtt.message == 'led-on':
                    led.ledOn()
                if mqtt.message == 'led-off':
                    led.ledOff()
                
            
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
                        lcd.lcd_display_string('1.Add 2.Delete U', 1,0)
                        lcd.lcd_display_string('3.Delete F 4.Exist',2,0)
                        
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
                                waitingForInput = True
                                
                                if pressedKey == '1':
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Input new pass:',1,0)
                                    while waitingForInput:
                                        pressedKey = passcode()
                                        if pressedKey is not None:
                                            keyInput += pressedKey
                                            lcd.lcd_display_string('*' * len(keyInput), 2, 0)
                                        if pressedKey is not None and pressedKey == 'B':
                                            newPasscode = keyInput[:-1]
                                            lcd.lcd_clear()
                                            lcd.lcd_display_string('Input root pass:',1,0)
                                            keyInput = ''
                                            print('new passcode: ' + newPasscode)
                                            break
                                    while waitingForInput:
                                        pressedKey = passcode()
                                        if pressedKey is not None:
                                            keyInput += pressedKey
                                            lcd.lcd_display_string('*' * len(keyInput), 2, 0)
                                            
                                        if pressedKey is not None and pressedKey == 'B':
                                            rootPasscode = keyInput[:-1]
                                            if addNewPasscode(rootPasscode, newPasscode):
                                                lcd.lcd_clear()
                                                lcd.lcd_display_string('Create success!',1,0)
                                                time.sleep(1.5)
                                                lcd.lcd_clear()
                                                keyInput = ''
                                                rootPasscode = ''
                                                newPasscode = ''
                                                buffer = ''
                                                showDatetime = True
                                                break
                                            else:
                                                lcd.lcd_clear()
                                                lcd.lcd_display_string('Root pass wrong' ,1,0)
                                                lcd.lcd_display_string('Or new pass exist',2,0)
                                                time.sleep(1.5)
                                                lcd.lcd_clear()
                                                rootPasscode = ''
                                                keyInput = ''
                                                newPasscode = ''
                                                buffer = ''
                                                showDatetime = True
                                                break
                                    print('menu 1')
                                    break
                                elif pressedKey == '2':
                                    print('menu 2') 
                                    passcodeToDelete = ''
                                    keyInput = ''
                                    
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Input pass to delete', 1, 0)
                                    
                                    while waitingForInput:
                                        pressedKey = passcode()
                                            
                                        if pressedKey is not None:
                                            keyInput += pressedKey
                                            lcd.lcd_display_string('*' * len(keyInput), 2,0)
                                            
                                        if pressedKey is not None and pressedKey == 'B':
                                            passcodeToDelete = keyInput[:-1]
                                            keyInput = ''
                                            lcd.lcd_clear()
                                            lcd.lcd_display_string('Input root pass', 1, 0)
                                            break
                                    
                                    while waitingForInput:
                                        pressedKey = passcode()
                                        
                                        if pressedKey is not None:
                                            keyInput += pressedKey
                                            print('KeyInput root: ' + keyInput)
                                            lcd.lcd_display_string('*' * len(keyInput), 2, 0)
                                            
                                        if pressedKey is not None and pressedKey == 'B':
                                            if(checkPasscode(keyInput[:-1], root=True)):
                                                lcd.lcd_clear()
                                                lcd.lcd_display_string('Put your finger',1,0)
                                                deleteFinger(passcodeToDelete)
                                                deleteUser(passcodeToDelete)
                                                
                                                lcd.lcd_clear()
                                                lcd.lcd_display_string('Delete success!', 1, 0)
                                                time.sleep(1.5)
                                                lcd.lcd_clear()
                                                
                                                keyInput = ''
                                                passcodeToDelete = ''
                                                buffer = ''
                                                showDatetime = True
                                                break
                                            else:
                                                lcd.lcd_clear()
                                                lcd.lcd_display_string('Root pass wrong',1,0)
                                                time.sleep(1.5)
                                                lcd.lcd_clear()
                                                
                                                keyInput = ''
                                                passcodeToDelete = ''
                                                buffer = ''
                                                showDatetime = True
                                                break
                                    break
                                
                                elif pressedKey == '3':
                                    print('menu 3')
                                    keyInput = ''
                                    passcodeFinger = ''
                                    
                                    lcd.lcd_clear()
                                    lcd.lcd_display_string('Input pass:',1,0)
                                    while waitingForInput:
                                        pressedKey = passcode()
                                        
                                        if pressedKey is not None:
                                            keyInput += pressedKey
                                            lcd.lcd_display_string('*' * len(keyInput),2, 0)
                                            
                                        if pressedKey is not None and pressedKey == 'B':
                                            passcodeFinger = keyInput[:-1]
                                            lcd.lcd_clear()
                                            lcd.lcd_display_string('Input root pass:',1,0)
                                            keyInput = ''
                                            break
                                    
                                    while waitingForInput:
                                        pressedKey = passcode()
                                        
                                        if pressedKey is not None:
                                            keyInput += pressedKey
                                            lcd.lcd_display_string('*' * len(keyInput),2,0)
                                            
                                        if pressedKey is not None and pressedKey == 'B':
                                            if checkPasscode(keyInput[:-1], root=True):
                                                lcd.lcd_clear()
                                                lcd.lcd_display_string('Put finger again',1,0)
                                                deleteFinger(passcodeFinger)
                                                lcd.lcd_clear()
                                                lcd.lcd_display_string('Finger deleted ',1,0)
                                                time.sleep(1.5)
                                                lcd.lcd_clear()
                                                keyInput = ''
                                                buffer = ''
                                                passcodeFinger = ''
                                                showDatetime = True
                                                break
                                            else:
                                                lcd.lcd_clear()
                                                lcd.lcd_display_string('Root pass wrong',1,0)
                                                time.sleep(1.5)
                                                lcd.lcd_clear()
                                                keyInput = ''
                                                buffer = ''
                                                passcodeFinger = ''
                                                showDatetime = True
                                                break
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
                        
                        if checkFingerExist(keyInput[:-2]) == False:
                            print('ex')
                            lcd.lcd_clear()
                            lcd.lcd_display_string('Finger existed', 1, 0)
                            time.sleep(1.5)
                            
                            keyInput = ''
                            buffer = ''
                            showDatetime = True
                        
                                                    
                        elif checkFingerExist(keyInput[:-2]) == True:
                            print('Run')
                            s, p = finger.enrollFinger(lcd)
                            
                            print('s,p: ' + str(s), str(p))
                            
                            addNewFinger(keyInput[:-2], p)
                            
                            keyInput = ''
                            buffer = ''
                            showDatetime = True
                            
                            position = None
                            status = None
                        else:
                            lcd.lcd_clear()
                            lcd.lcd_display_string('Cannot detect', 1, 0)
                            lcd.lcd_display_string('try again',2, 0)
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
