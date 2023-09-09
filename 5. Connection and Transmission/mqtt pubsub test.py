"""
Test file to ensure there is a two-way connection to a Cloud
Platform - AWS IoT Core to RPI.

Components required:
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)

Code description:
Test file to test whether I can send and receive data from
AWS IoT core before it gets complicated with RPI and sensors.
--------------------------------------------------------------------
Setup:

Setup AWS IoT Core:
1. Create device on AWS IoT Core, guide in the file
"Plan for BAckend and Front End.docx"

2. Install AWSIoTPythonSDK, using terminal:
pip install AWSIoTPythonSDK
Successfully installed AWSIoTPythonSDK-1.5.2
--------------------------------------------------------------------

Date: 09/09/2023
Author: Asad Maza - Group 3
"""

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import random

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload.decode("utf-8"))
    print("from topic: ")
    print(message.topic)

# Configure MQTT client
myMQTTClient = AWSIoTMQTTClient("RaspberryPi-Asad")  # Things device name
myMQTTClient.configureEndpoint("a2mqsm6nqkmbh6-ats.iot.ap-southeast-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/asadRPI/Desktop/AWS IoT Core/root-CA.crt",
                                  "/home/asadRPI/Desktop/AWS IoT Core/private.pem.key",
                                  "/home/asadRPI/Desktop/AWS IoT Core")

# Connect to AWS IoT
myMQTTClient.connect()

# Subscribe to a topic, ensure you have setup on AWS IoT Core correctly
print("Subscribing to topic 'sdk/test/AWS'") # 
myMQTTClient.subscribe("sdk/test/AWS", 1, customCallback)
time.sleep(2)  # Wait to ensure the subscription is active

# Some test codePublish to the same topic in a loop forever
while True:
    message = {
        'message': 'Hello from RaspberryPi!',
        'value': random.randint(0, 100)
    }
    print(f"Publishing message to topic 'sdk/test/Python': {json.dumps(message)}")
    myMQTTClient.publish("my/test/topic", json.dumps(message), 0)
    time.sleep(5)  # Publish every 10 seconds
    
