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
        return cls._instance

    def __init__(self, port='/dev/ttyS0', baudrate=57600, password=0xFFFFFFFF, address=0x00000000):
        pass  # Initialize in __new__ to ensure it's done only once

    def enrollFinger(self):
        try:
            print('Waiting for finger...')
            
            while not self.fingerprint.readImage():
                pass

            self.fingerprint.convertImage(FINGERPRINT_CHARBUFFER1)

            result = self.fingerprint.searchTemplate()
            positionNumber = result[0]

            if positionNumber >= 0:
                print('Template already exists at position #' + str(positionNumber))
                return

            print('Remove finger...')
            time.sleep(2)

            print('Waiting for the same finger again...')
            
            while not self.fingerprint.readImage():
                pass

            self.fingerprint.convertImage(FINGERPRINT_CHARBUFFER2)

            if self.fingerprint.compareCharacteristics() == 0:
                raise Exception('Fingers do not match')

            self.fingerprint.createTemplate()

            positionNumber = self.fingerprint.storeTemplate()
            print('Finger enrolled successfully!')
            print('New template position #' + str(positionNumber))
            
            self.fingerprint.loadTemplate(positionNumber, FINGERPRINT_CHARBUFFER1)
            characteristics = str(self.fingerprint.downloadCharacteristics(FINGERPRINT_CHARBUFFER1)).encode('utf-8')
            print('SHA-2: ' + hashlib.sha256(characteristics).hexdigest())
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            sys.exit(1)

    def detectFinger(self, status=True):
        if not status:
            return False
        
        if status:
            try:
                print('Waiting for finger...')

                while not self.fingerprint.readImage():
                    pass

                self.fingerprint.convertImage(FINGERPRINT_CHARBUFFER1)

                result = self.fingerprint.searchTemplate()

                positionNumber = result[0]
                accuracyScore = result[1]

                if positionNumber == -1:
                    print('Match not found!')
                    return False
                else:
                    print('Remove finger...')
                    print('Found template at position #' + str(positionNumber))
                    print('The accuracyScore is: ' + str(accuracyScore))

                self.fingerprint.loadTemplate(positionNumber, FINGERPRINT_CHARBUFFER1)

                characteristics = str(self.fingerprint.downloadCharacteristics(FINGERPRINT_CHARBUFFER1)).encode('utf-8')
                print('SHA-2: ' + hashlib.sha256(characteristics).hexdigest())

                return True
            except Exception as e:
                print('Operation failed')
                print('Exception message: ' + str(e))
                return False
    
    def deleteFinger(self):
        try:
            positionNumber = input('Please enter the template position you want to delete: ')
            positionNumber = int(positionNumber)

            if self.fingerprint.deleteTemplate(positionNumber):
                print('Template deleted')
        except Exception as e:
            print('Exception message: ' + str(e))
            
    def stop(self):
        sys.exit(1)
    
    def deleteAllTemplate(self):
        self.fingerprint.clearDatabase()

# Example usage:
#finger = FingerPrint()

