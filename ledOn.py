import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)


print('on')

message = ''

def on_connect(client, userdata, flags, rc):
    print('Connect with result code' + str(rc))
    client.subscribe('#')
    
def on_message(client, userdata, msg):
    global message
    message = f'{msg.payload.decode()}'
    
    if message == '{"data":"led_on"}':
        GPIO.output(21, 1)
    
    if message == '{"data":"led_off"}':
        GPIO.output(21, 0)



client = mqtt.Client()	
client.on_connect = on_connect
client.on_message = on_message

client.connect('0.tcp.ap.ngrok.io', 10376, 60)
client.loop_forever()
print('pass')

