import sys

print(sys.path)

sys.path.append('/home/thinhtran/smartlock/modules')

from time import sleep
from as608_driver import PyFingerprint, FINGERPRINT_CHARBUFFER1, FINGERPRINT_CHARBUFFER2

class FingerPrint:
    def __init__(self, port='/dev/ttyS0', baudrate=57600, password=0xFFFFFFFF, address=0x00000000):
        try:
            self.fingerprint = PyFingerprint(port, baudrate, password, address)
            if not self.fingerprint.verifyPassword():
                raise ValueError('The given fingerprint sensor password is wrong!')
        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            exit(1)

    def enroll(self):
        try:
            print('Waiting for finger...')
            
            # Wait for a finger to be read
            while not self.fingerprint.readImage():
                pass

            # Convert read image to characteristics and store it in charbuffer 1
            self.fingerprint.convertImage(FINGERPRINT_CHARBUFFER1)

            # Check if finger is already enrolled
            result = self.fingerprint.searchTemplate()
            positionNumber = result[0]

            if positionNumber >= 0:
                print('Template already exists at position #' + str(positionNumber))
                return

            print('Remove finger...')
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

# Example usage:
#fingerprint_enroller = FingerprintEnrollment()
#fingerprint_enroller.enroll()
