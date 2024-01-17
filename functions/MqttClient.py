import sys
import paho.mqtt.client as mqtt



message = None

def onConnect(client, userdata, flags, rc):
    print('Connected with result code: ' + str(rc))
    client.subscribe('#')
    
def onMessage(client, userdata, msg):
    global message
    message = msg.payload.decode()
    

client = mqtt.Client()
client.on_connect = onConnect
client.on_message = onMessage

client.connect('0.tcp.ap.ngrok.io', 10376, 60)

client.loop_start()