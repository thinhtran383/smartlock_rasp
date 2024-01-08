import sys

sys.path.append('/home/thinhtran/smartlock/modules')

import time
from threading import Lock
from as608_driver import PyFingerprint, FINGERPRINT_CHARBUFFER1, FINGERPRINT_CHARBUFFER2
from led_module import LEDController
import hashlib

led = LEDController()

class FingerPrint:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FingerPrint, cls).__new__(cls)
            try:
                cls._instance.fingerprint = PyFingerprint(*args, **kwargs)
                if not cls._instance.fingerprint.verifyPassword():
                    raise ValueError('The given fingerprint sensor password is wrong!')
            except Exception as e:
                print('The fingerprint sensor could not be initialized!')
                print('Exception message: ' + str(e))
                sys.exit(1)
            cls._instance.fingerprint_lock = Lock()
        return cls._instance

    def __init__(self, port='/dev/ttyS0', baudrate=57600, password=0xFFFFFFFF, address=0x00000000):
        pass

    def enrollFinger(self):
        try:
            print('Waiting for finger enroll')
            with self.fingerprint_lock:
                while not self.fingerprint.readImage():
                    pass
                self.fingerprint.convertImage(FINGERPRINT_CHARBUFFER1)
                
                result = self.fingerprint.searchTemplate()
                positionNumber = result[0]
                
                if positionNumber >= 0:
                    print('Finger exists! position: ' + str(positionNumber))
                    return 1
                time.sleep(1.5)
                print('Remove finger...')
                time.sleep(2)
                
                print('Waiting for the same finger again...')
                while not self.fingerprint.readImage():
                    pass
                
                self.fingerprint.convertImage(FINGERPRINT_CHARBUFFER2)
                
                if self.fingerprint.compareCharacteristics() == 0:
                    print('Finger not match')
                    return 2
                
                self.fingerprint.createTemplate()
                positionNumber = self.fingerprint.storeTemplate()
                print('Finger success')
                
        except Exception as e:
            print('Exception!!: ' + str(e))
            return 2
                    

    def detectFinger(self, positionNumber):
        try:
                self.fingerprint.loadTemplate(positionNumber, FINGERPRINT_CHARBUFFER1)

                characteristics = str(self.fingerprint.downloadCharacteristics(FINGERPRINT_CHARBUFFER1)).encode('utf-8')
                print('SHA-2: ' + hashlib.sha256(characteristics).hexdigest())

                return 1
        except Exception as e:
            print('Operation failed')
            print('Exception message: ' + str(e))
            return 0

    def checkFingerExist(self):
        try:
            print('Waiting for finger...')
            with self.fingerprint_lock:
                while not self.fingerprint.readImage():
                    pass

                self.fingerprint.convertImage(FINGERPRINT_CHARBUFFER1)

                result = self.fingerprint.searchTemplate()
                positionNumber = result[0]

                if positionNumber == -1:
                    print('Match not found!')
                    return False, positionNumber
                else:
                    print('Found ex template at position #' + str(positionNumber))
                    return True, positionNumber
                
        except Exception as e:
            print('Operation failed')
            print('Exception message: ' + str(e))
            return False
        
    
    def deleteFinger(self):
        try:
            positionNumber = input('Please enter the template position you want to delete: ')
            positionNumber = int(positionNumber)

            with self.fingerprint_lock:
                if self.fingerprint.deleteTemplate(positionNumber):
                    print('Template deleted')
        except Exception as e:
            print('Exception message: ' + str(e))

    def stop(self):
        sys.exit(1)

    def deleteAllTemplate(self):
        with self.fingerprint_lock:
            self.fingerprint.clearDatabase()

# Example usage
'''finger = FingerPrint()
finger.checkFingerExist()
finger.enrollFinger()
print('delete')'''
#if boo == 1:
 #   finger.detectFinger(posi)