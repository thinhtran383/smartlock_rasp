import paho.mqtt.client as mqtt
'''
client = mqtt.Client()
client.connect('0.tcp.ap.ngrok.io', 17753, 60)

client.publish('myTopic', 'thinh')

client.disconnect()
'''

class MQTTPublisher:
    def __init__(self, brokerAddress, port):
        self.brokerAddress = brokerAddress
        self.port = port
        self.client = mqtt.Client()
        self.client.connect(self.brokerAddress, self.port, 60)
        
    def sendToSub(self, topic, message):
        self.client.publish(topic, message)
        print(f'send message: @{message} to topic: @{topic}')
    
    def disconnect(self):
        self.client.disconnect()
'''
if __name__ == '__main__':
    pub = MQTTPublisher('0.tcp.ap.ngrok.io', 17753)
    pub.sendToSub('myTopic', 'thinhtran')
    pub.sendToSub('myTopic', 'hello')
'''