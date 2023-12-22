import sys

print(sys.path)

sys.path.append('/home/thinhtran/smartlock/modules')

from time import sleep
from as608_driver import PyFingerprint, FINGERPRINT_CHARBUFFER1, FINGERPRINT_CHARBUFFER2
import hashlib

class FingerPrint:
    def __init__(self, lcd, port='/dev/ttyS0', baudrate=57600, password=0xFFFFFFFF, address=0x00000000):
        try:
            self.fingerprint = PyFingerprint(port, baudrate, password, address)

            self.lcd = lcd 

            if not self.fingerprint.verifyPassword():
                raise ValueError('The given fingerprint sensor password is wrong!')
        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            exit(1)

    def enroll(self):
        try:
            print('Waiting for finger...')
            self.lcd.lcd_clear()
            self.lcd.lcd_display_string('Waiting for finger...', 1, 0)
            
            # Wait for a finger to be read
            while not self.fingerprint.readImage():
                self.lcd.lcd_clear()
                pass

            # Convert read image to characteristics and store it in charbuffer 1
            self.fingerprint.convertImage(FINGERPRINT_CHARBUFFER1)

            # Check if finger is already enrolled
            result = self.fingerprint.searchTemplate()
            positionNumber = result[0]

            if positionNumber >= 0:
                print('Template already exists at position #' + str(positionNumber))
                self.lcd.lcd_display_string('Template already exists at position #' + str(positionNumber), 1, 0)
                return

            print('Remove finger...')
            self.lcd.lcd_display_string('Remove finger...', 1, 0)
            sleep(2)

            print('Waiting for the same finger again...')
            
            # Wait for the finger to be read again
            while not self.fingerprint.readImage():
                pass

            # Convert read image to characteristics and store it in charbuffer 2
            self.fingerprint.convertImage(FINGERPRINT_CHARBUFFER2)

            # Compare the charbuffers
            if self.fingerprint.compareCharacteristics() == 0:
                raise Exception('Fingers do not match')

            # Create a template
            self.fingerprint.createTemplate()

            # Save template at a new position number
            positionNumber = self.fingerprint.storeTemplate()
            print('Finger enrolled successfully!')
            print('New template position #' + str(positionNumber))

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            exit(1)

    def detect(self):
        try:
            print('Waiting for finger...')

            while(self.fingerprint.readImage() == False):
                pass

            self.fingerprint.convertImage(FINGERPRINT_CHARBUFFER1)

            result = self.fingerprint.searchTemplate()

            positionNumber = result[0]
            accuracyScore = result[1]

            if(positionNumber == -1):
                print('Match not found!')
                exit(0)
            
            else:
                print('Found template at position #' + str(positionNumber))
                print('The accuracyScore is: ' + str(accuracyScore))
            
            self.fingerprint.loadTemplate(positionNumber, FINGERPRINT_CHARBUFFER1)

            characterics = str(self.fingerprint.downloadCharacteristics(FINGERPRINT_CHARBUFFER1)).encode('utf-8')
            print('SHA-2: ' + hashlib.sha256(characterics).hexdigest())
        except Exception as e:
            print('Operation failed')
            print('Exception message: ' + str(e))
# Example usage:
#fingerprint_enroller = FingerprintEnrollment()
#fingerprint_enroller.enroll()
