#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

import time
from as608_driver import PyFingerprint
from as608_driver import FINGERPRINT_CHARBUFFER1
from as608_driver import FINGERPRINT_CHARBUFFER2

class FingerprintEnroll:
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

            while not self.fingerprint.readImage():
                pass

            self.fingerprint.convertImage(FINGERPRINT_CHARBUFFER1)

            result = self.fingerprint.searchTemplate()
            positionNumber = result[0]

            if positionNumber >= 0:
                print('Template already exists at position ' + str(positionNumber))
                exit(0)

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
            print('New template position ' + str(positionNumber))

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            exit(1)

# Example of how to use the class in main.py
if __name__ == "__main__":
     fingerprint_enroller = FingerprintEnroll()
     fingerprint_enroller.enroll()
