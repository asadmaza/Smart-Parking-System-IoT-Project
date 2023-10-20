"""
====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
Test file for Smart Parking System on a toy car with
Magnetometer sensor.

Threshold values:
Magnetometer sensor     |   sensor_threshold = 0.015 # in percent 
Magnetometer sensor     |   base_val_threshold = 0.005 # in percent

Components required:
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)
x1 5mm Red LED GPIO 
x1 5mm Green LED
x2 330 ohm resistors
x1 Magnetometer

Code description:
The system uses a  magnetometer to detect the presence of a car in the 
parking bay. When a car  is detected, the LED will turn from Green 
(free) to Red (occupied).

--------------------------------------------------------------------
Setup:
Magnetometer:
Needs I2C communication enabled on RPI
SDA to GPIO 2/SDA (in I2C Data mode enabled)
SCL to GPIO 3/SCL (in I2C Data mode enabled)
3.3V to 3V Pin
GND to GND pin

LED(GPIO 5) - Green LED
LED(GPIO 6) - Red LED

--------------------------------------------------------------------

Date: 11/10/2023
Author: Asad Maza - Group 3

====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
"""
# Imports
import RPi.GPIO as GPIO
import time
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import os
from gpio_reset import all_pins_to_off
from PiicoDev_QMC6310 import PiicoDev_QMC6310
from PiicoDev_Unified import sleep_ms

# Define function to get average of a list
def get_average(data_list):
    return sum(data_list) / len(data_list)

# Define function to collect data for a given number of seconds
def collect_data_for_seconds(seconds):
    data_list = []
    for _ in range(seconds):
        raw_data = magSensor.read()
        z_axis_strength = raw_data['z']
        data_list.append(z_axis_strength)
        sleep_ms(1000)
    return data_list

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
green_LED = GPIO.output(5, GPIO.HIGH)
red_LED = GPIO.output(6, GPIO.LOW)

# Topic Constant
BAY_STATUS_CHANGE_FROM_DEVICE = "BAY_STATUS_CHANGE_FROM_DEVICE" # publish to this

# AWS IoT client setup
myMQTTClient = AWSIoTMQTTClient("testCertif")
myMQTTClient.configureEndpoint("a30y98prchbi0n-ats.iot.us-west-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials(os.path.abspath(os.getcwd())+"/testCertif/root-CA.crt",
                                      os.path.abspath(os.getcwd())+"/testCertif/testCertif.private.key",
                                      os.path.abspath(os.getcwd())+"/testCertif/testCertif.cert.pem")

# Confirm MQTT Connection
myMQTTClient.connect()

# Initialise threshold value
sensor_threshold = 0.015 # in percent (e.g. 10% = 0.10)
base_val_threshold = 0.005 # in percent (e.g. 2% = 0.02)

# Initialise sensor
magSensor = PiicoDev_QMC6310(range=3000)

print("Magnetometer sensor mounted at top of bay")
print("Formula for change_in_magnetfic_flux_density: abs((z_axis_strength - default_value) / default_value) * 100%")

# Loop until a valid default value is obtained
while True:
    # Read the data of the previous ten seconds
    data_list = collect_data_for_seconds(10)
    
    # If the data fluctuation is less than 2%, set it as the default value
    avg_value = get_average(data_list)
    max_value = max(data_list)
    min_value = min(data_list)
    fluctuation = (max_value - min_value) / avg_value
    
    if fluctuation < base_val_threshold:
        default_value = avg_value
        break

try:
    while True:
        raw_data = magSensor.read()
        z_axis_strength = raw_data['z']
        print("Observation value : "+ str(default_value))
        print("Change in magnetic flux density : ", abs((z_axis_strength - default_value) / default_value)*100)

        # Check car presence based on Magnetometer sensor measurement
        if abs((z_axis_strength - default_value) / default_value) > sensor_threshold:
            print("Magnetometer is detecting a car and bay status is occupied")
            green_LED = GPIO.output(5, GPIO.LOW)
            red_LED = GPIO.output(6, GPIO.HIGH)
            bayStatus = {"state": 1}
            message = json.dumps({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "data": bayStatus})
            try:
                myMQTTClient.publish(BAY_STATUS_CHANGE_FROM_DEVICE, message, 1)
            except Exception as e:
                print(f"An exception occurred while publishing: {e}")
        else:
            print("Magnetometer is not detecting a car and bay status is free")
            green_LED = GPIO.output(5, GPIO.HIGH)
            red_LED = GPIO.output(6, GPIO.LOW)
            bayStatus = {"state": 0}
            message = json.dumps({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "data": bayStatus})
            try:
                myMQTTClient.publish(BAY_STATUS_CHANGE_FROM_DEVICE, message, 1)
            except Exception as e:
                print(f"An exception occurred while publishing: {e}")
                
        print("-" * 50)
        time.sleep(1)  # Delay for 1 second before the next reading
                
except KeyboardInterrupt:
    print("Terminating and cleaning up")
    all_pins_to_off()

