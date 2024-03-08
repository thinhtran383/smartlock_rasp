from datetime import datetime
from modules import I2C_LCD_driver
from modules.keypad_module import Keypad
from modules.led_module import LEDController
from modules.Fingerprint import FingerPrint
from modules.Button import Button
from datetime import datetime
from DataManager import DataManager
from functions.MqttSub import MQTTHandler


import threading
import time
import requests

# Define mqtt broker
brokerAddress = '0.tcp.ap.ngrok.io'
port = 15560
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
button = Button(20)

tmp_finger = FingerPrint()

#finger.enrollFinger(lcd)

# Define status
showDatetime = True
pauseThread = False
doorIsOpen = False


keyInput = ''
buffer = ''
rootPassword = '3897'

position = None
status = None
waitingForInput = None


# Locking thread
lcdLock = threading.Lock()
fingerLock = threading.Lock()




# Lay thoi gian hien tai
def currentDateTime():
    currentTime = datetime.now()
    
    dateFormat = '%d-%m-%y'
    timeFormat = '%H:%M:%S'
    
    formattedDate = currentTime.strftime(dateFormat)
    formattedTime = currentTime.strftime(timeFormat)
    
    return formattedDate, formattedTime
        
        
# Tra ve ki tu cua keypad
def passcode():
    key = str(keypad.get_key())
    return key if key != 'None' else None


    
        
       
# thread chay van tay (finger position)
def fingerDetect():    
    global status, position  
    while True:
        time.sleep(1.5)
        with fingerLock:
            status, position = finger.checkFingerExist()


# them passcode moi tu keypad (BO)
def addNewPasscode(rootPasscode, newPasscode):
    # Bo
    return False
    
# check passcode nhap vao
def checkPasscode(passcode, root=False):
    apiEndpoint = f'http://127.0.0.1:5000/api/v1/secure/{passcode}'
    
    try:
        response = requests.post(apiEndpoint)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'data' in result and result['data'] is True:
                return True
            else:
                return False
        else:
            print('err')
            return False
    except Exception as e:
        print(f'ex: {e}')
        return False


# check van tay
def finger_open(finger_position):
    apiEndpoint = f'http://127.0.0.1:5000/api/v1/secure/fingerPosition/{finger_position}'
    
    try:
        response = requests.post(apiEndpoint)
        
        if response.status_code == 200:
            return True
        else:
            print('err')
            return False
    except Exception as e:
        print(f'err: {e}')
        return False



# xoa user tu keypad (DONE) xoa toan bo
def deleteUser(passcode):
    #sql = 'delete from user_data where passcode = ? and root = 0'
    
    sql = 'select userId from secure where passcode = ? and root = 0'
    sqlValues = (passcode,)
    rs = db.executeSql(sql, sqlValues, fetchResult=True)
    
    if rs:
        (value,) = rs[0] # tahc tuple
        apiEndpoint = f'http://127.0.0.1:5000/api/v1/secure/deleteUser/{value}'
        
        try:
            response = requests.delete(apiEndpoint)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(f'err: {e}')
            return False
    else:
        return False



# them van tay moi finger Position (TODO)
def addNewFinger(passcode, position):
        print(passcode, position)
        
        
        sql = 'update secure set positionFinger = ? where passcode = ?'
        sql_values = (position, passcode,)
        rs = db.executeSql(sql, sql_values)


# Kiem tra van tay ton tai chua khi them tu keypad (TODO)
def checkFingerExist(passcode):
    sql_get_position = 'select positionFinger from secure where passcode = ?'
    sql_values = (passcode,)
    
    rs = db.executeSql(sql_get_position, sql_values, fetchResult=True)
    
    (value,) = rs[0]
    
    print(value)
    
    if value is None:
        return False
    else:
        return True

print('ton tai van tay' + str(checkFingerExist('000000')))
# Xoa van tay ra khoi db va finger print (TODO) chua test
def deleteFinger(passcode):
    
    # Tim position finger trong db
    sql_get_position = 'select positionFinger from secure where passcode = ?'
    sql_values = (passcode,)
    
    rs = db.executeSql(sql_get_position, sql_values, fetchResult=True)
    if rs:
        (number,) = rs[0]
    else:
        number = None
    
    
    # Thuc hien xoa trong phan cung
    if number is not None:    
        tmp_finger.deleteFinger(int(number))
    
    
        #Cap nhat lai trong db
        sql = 'update secure set positionFinger = ? where passcode = ?'
        values = (None, passcode,)
        db.executeSql(sql, values)



def check_root_passcode(passcode):
    sql = 'select root from secure where passcode = ?'
    sql_values = (passcode,)
    rs = db.executeSql(sql, sql_values, fetchResult=True)
    
    if rs:
        return True
    else:
        return False


def led_control():
    led.ledOn()
    time.sleep(2)
    led.ledOff()
    
def check_passcode_local(passcode):
    sql = 'select passcode from secure where passcode = ?'
    sql_values = (passcode,)
    rs = db.executeSql(sql, sql_values, fetchResult=True)
    if rs:
        return True
    else:
        return False



print(str(check_passcode_local('88888888')))

if __name__ == '__main__':   
    fingerThread = threading.Thread(target=fingerDetect)
    fingerThread.start()
    mqtt.connect()
    
    try:
        while True:
            pressedKey = passcode()
            
            
            if mqtt.message is not None:
                if mqtt.message == 'unlock':
                    led_control()             
                    mqtt.message = None
                
            
            if status and position != -1:
                store_position = position
                status = None
                position = None
                
                store = finger_open(store_position)
                if store :
                    lcd.lcd_clear()
                    lcd.lcd_display_string('Unlock success', 1, 0)
                    led_control()
                    showDatetime = True
                elif store is not True:
                    tmp_finger.deleteFinger(int(store_position))
                    status = None
                    position = None
                    lcd.lcd_clear()
                    lcd.lcd_display_string('Password wrong', 1, 0)
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
                        lcd.lcd_display_string('1.Delete U', 1,0)
                        lcd.lcd_display_string('2.Delete F 3.Exist',2,0)
                        
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
                                
                                
                                # Vao option none: them user moi (BO)
                                if pressedKey == 'vnb':
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
                                
                                # Vao option 1: xoa user
                                elif pressedKey == '1':
                                    print('menu 1') 
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
                                            # Co ton tai hay khong thi van luon xoa
                                            if(check_root_passcode(keyInput[:-1])):
                                                lcd.lcd_clear()
                                                lcd.lcd_display_string('Put your finger',1,0)
                                                
                                                
                                                deleteFinger(passcodeToDelete)
                                                deleteUser(passcodeToDelete)
                                                
                                                lcd.lcd_clear()
                                                lcd.lcd_display_string('Delete success!', 1, 0)
                                                time.sleep(1.5)
                                                lcd.lcd_clear()
                                                showDatetime = True
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
                                
                                # Vao option 2: xoa van tay
                                elif pressedKey == '2':
                                    print('menu 2')
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
                                            passcodeFinger = keyInput[:-1] # passcode cua nguoi dung luu tai day
                                            #print('Passcode nguoi dung' + passcodeFinger)
                                            if check_passcode_local(passcodeFinger) is not True: # neu nguoi dung nhap sai thi thoat
                                                break
                                            
                                            lcd.lcd_clear()
                                            lcd.lcd_display_string('Input root pass:',1,0)
                                            keyInput = ''
                                            break
                                    
                                    while waitingForInput:
                                        pressedKey = passcode()
                                        
                                        
                                        if check_passcode_local(passcodeFinger) == False: 
                                                lcd.lcd_clear()
                                                lcd.lcd_display_string('Wrong passcode',1,0)
                                                time.sleep(1.5)
                                                keyInput = ''
                                                buffer = ''
                                                passcodeFinger = ''
                                                showDatetime = True
                                                break
                                        
                                        if pressedKey is not None:
                                            keyInput += pressedKey
                                        
                                            lcd.lcd_display_string('*' * len(keyInput),2,0)
                                            
                                        if pressedKey is not None and pressedKey == 'B':
                                            if check_root_passcode(keyInput[:-1]):
                                                lcd.lcd_clear()
                                                lcd.lcd_display_string('Put finger again',1,0)
                                               # with fingerLock:
                                                    
                                                    
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
                                
                                # Vao option 4: Thoat ra khoi menu
                                elif pressedKey == '3':
                                    print('menu 3')
                                    lcd.lcd_clear()
                                    showDatetime = True
                                    keyInput = ''
                                    buffer = ''
                                    break
                                        
                    
                    #Them van tay moi neu nhap dung passcode
                    elif check_passcode_local(keyInput[:-2]) and keyInput[-2] == '#':
                        print('Enroll mode')
                        
                        if checkFingerExist(keyInput[:-2]) == True:
                            print('ex')
                            lcd.lcd_clear()
                            lcd.lcd_display_string('Finger existed', 1, 0)
                            time.sleep(1.5)
                            
                            keyInput = ''
                            buffer = ''
                            showDatetime = True
                        
                                                    
                        elif checkFingerExist(keyInput[:-2]) == False:
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
                        led_control()
                        #time.sleep(1.5)
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
                        
                        
            # Xoa man hinh
            if pressedKey == 'C' and pressedKey is not None:
                keyInput = ''
                buffer = ''
                lcd.lcd_clear()
                lcd.lcd_display_string('Input passcode: ',1,0)
            
            
    except KeyboardInterrupt:
        fingerThread.join()
