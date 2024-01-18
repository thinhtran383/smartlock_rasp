from functions.MqttSub import MQTTHandler
from modules.led_module import LEDController

import time


brokerAddress = '0.tcp.ap.ngrok.io'
port = 17753
topic = '#'
led = LEDController()
mqtt = MQTTHandler(brokerAddress, port, topic)

def main():
    try:
        mqtt.connect()
        
        while True:
            if mqtt.message is not None:
                if mqtt.message == 'led-on':
                    print('led is on')
                    led.ledOn()
                    mqtt.message = None
                if mqtt.message == 'led-off':
                    print('led is off')
                    led.ledOff()
                    mqtt.message = None
            time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting...')
    finally:
        mqtt.disconnect()
        
main()