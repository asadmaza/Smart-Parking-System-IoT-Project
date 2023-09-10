"""
Test file to ensure there is a two-way connection to a Cloud
Platform - AWS IoT Core to RPI using MQTT Protocol and
Publish and Subscribe.

Components required:
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)

Code description:
Test file to test whether I can send and receive data from
AWS IoT core before it gets complicated with RPI and sensors.
Can both send and receive messages, DEBUG mode enabled.
--------------------------------------------------------------------
Setup:

Setup AWS IoT Core:
1. Create device on AWS IoT Core, guide in the file
"Plan for BAckend and Front End.docx"

2. Install AWSIoTPythonSDK, using terminal:
pip install AWSIoTPythonSDK
Successfully installed AWSIoTPythonSDK-1.5.2

Configure the topics for subscribe and publish accordingly.
--------------------------------------------------------------------

Date: 09/09/2023
Author: Asad Maza - Group 3
"""
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import random
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload.decode("utf-8"))
    print("from topic: ")
    print(message.topic)

try:
    # Configure MQTT client
    myMQTTClient = AWSIoTMQTTClient("basicPubSub") # Using working sample in SDK folder
    myMQTTClient.configureEndpoint("a2mqsm6nqkmbh6-ats.iot.ap-southeast-2.amazonaws.com", 8883)

    # Setup credentials
    myMQTTClient.configureCredentials("/home/asadRPI/Desktop/AWS IoT Core/root-CA.crt",
                                      "/home/asadRPI/Desktop/AWS IoT Core/RaspberryPi-Asad.private.key",
                                      "/home/asadRPI/Desktop/AWS IoT Core/RaspberryPi-Asad.cert.pem")

    # Add additional configurations to align with working example
    myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect to AWS IoT
    if myMQTTClient.connect():
        print("Connected successfully!")
    else:
        print("Could not connect. Exiting.")
        exit(1)

    # Subscribe topic
    print("Subscribing to topic 'sdk/test/python'")
    myMQTTClient.subscribe("sdk/test/python", 1, customCallback)
    time.sleep(2)  # Wait to ensure the subscription is active

    # Test Code: Publish to the same topic in a loop forever
    while True:
        message = {
            'message': 'Hello from RaspberryPi!',
            'value': random.randint(0, 100)
        }
        # Publish topic
        print(f"Publishing message to topic 'sdk/test/python': {json.dumps(message)}")
        myMQTTClient.publish("sdk/test/python", json.dumps(message), 1)  # Changed QoS to 1
        time.sleep(5)  # Publish every 5 seconds

except Exception as e:
    print(f"An exception occurred: {e}")