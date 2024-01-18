import sys
import paho.mqtt.client as mqtt

class MQTTHandler:
    def __init__(self, brokerAddress, port, topic='#'):
        self.brokerAddress = brokerAddress
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.message = None
        
    def connect(self):
        self.client.connect(self.brokerAddress, self.port, 60)
        self.client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc):
        print('Connect with result code: ' + str(rc))
        client.subscribe(self.topic)
        
    def on_message(self, client, userdata, msg):
        self.message = msg.payload.decode('utf-8')
        print(f'message: {self.message}')
    
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()