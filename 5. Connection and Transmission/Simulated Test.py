"""
====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
Test file to ensure there is a two-way connection to a Cloud
Platform - AWS IoT Core.

Components required:
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)
x1 5mm Red LED GPIO 
x1 5mm Green LED
x2 330 ohm resistors
x1 Ultrasonic Sensor

Code description:
I'm not sure what I want to achieve yet. Bit of iteration lets go!
Going to simulate a single bay and see if I can get a two way
connection somehow to update states of LED and send sensor data
--------------------------------------------------------------------
Setup:

Bay 1 - Reserved:
LED(GPIO 2) - Yellow LED
LED(GPIO 3) - Red LED
Ultrasonic Sensor:
• VCC connects to Pin 2 (5V)
• Trig connects to Pin 11 (GPIO 17)
• Echo connects to R1 (1k OHM)
• R2 and R3 (1k OHM + 1 k OHM) connects from R1 to Ground
• Wire from R1 and R2+R3 connects to Pin 16 (GPIO 23)
• GND connects to Pin 34 (Ground)

Need to setup AWS IoT Core, follow Setup Guide
Install AWSIoTPythonSDK, using terminal:
pip install AWSIoTPythonSDK
Successfully installed AWSIoTPythonSDK-1.5.2

--------------------------------------------------------------------

Date: 09/09/2023
Author: Asad Maza - Group 3

====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
"""
# Imports
import RPi.GPIO as GPIO
import time
from gpio_reset import all_pins_to_off
import AWSIoTPythonSDK 
# Set all pins to off before main code
all_pins_to_off()

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define distance measuring function
def read_distance(TRIG, ECHO):
    GPIO.output(TRIG, False)
    time.sleep(2)    
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)    
    while GPIO.input(ECHO)==0:
        pulse_start = time.time()
    while GPIO.input(ECHO)==1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration * 34300) / 2
    distance = round(distance, 2)
    return distance

# LED, sensor and state mapping for each bay
bay_mapping = {
    'Bay1': {'red_led': 2, 'yellow_or_green_led': 3, 'sensor_trigger': 17, 'sensor_echo': 23, 'state': 0},
}

# Setup GPIO for LEDs
for bay, info in bay_mapping.items():
    GPIO.setup(info['yellow_or_green_led'], GPIO.OUT)
    GPIO.setup(info['red_led'], GPIO.OUT)
    GPIO.setup(info['sensor_trigger'], GPIO.OUT)
    GPIO.setup(info['sensor_echo'], GPIO.IN)

try:
    while True:
        for bay, info in bay_mapping.items():
            # Read distance from ultrasonic sensor
            dist_measured = read_distance(info['sensor_trigger'], info['sensor_echo'])
            # Check toy car presence
            # 5cm threshold for toy car
            if dist_measured <= 5.0 and dist_measured >= 0.0:
                # Turn off yellow/green LED and turn on red LED
                GPIO.output(info['yellow_or_green_led'], False)
                GPIO.output(info['red_led'], True)
                # Update available bays
                if info['state'] == 0:
                    info['state'] = 1

            if dist_measured > 5.0:
                # Turn on yellow/green LED and turn off red LED
                GPIO.output(info['yellow_or_green_led'], True)
                GPIO.output(info['red_led'], False)
                # Update available bays
                if info['state'] == 1:
                    info['state'] = 0
            
            # Print for testing purposes
            print(f"{bay} Distance: {dist_measured} State: {info['state']}")
        print("-"*80)
        print("To stop script correctly, press CTRL + C, ensure all_pins_to_off() function runs")

# Break out
except KeyboardInterrupt:
    print("Terminating module")
    all_pins_to_off()
    
# Cleanup
finally:
    all_pins_to_off()