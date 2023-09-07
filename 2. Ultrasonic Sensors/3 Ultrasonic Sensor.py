"""
====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
Test file for 3 HC-SR04 Ultrasonic sensors.
Use this file to test 3 Ultrasonic sensors for the project.

Components required:
x3 HC-SR04 Ultrasonic Sensor
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)
x9 1K ohm resistor

Code description:
This code controls 3 HC-SR04 ultrasonic sensors with a Raspberry Pi
to measure and print the distance to objects in centimeters for each
sensor, updating every second.
--------------------------------------------------------------------
Setup:

Ensure all 3 Ultrasonic sensors are connected as described:

Ultrasonic sensor 1:
• VCC connects to Pin 2 (5V)
• Trig connects to Pin 11 (GPIO 17)
• Echo connects to R1 (1k OHM)
• R2 and R3 (1k OHM + 1 k OHM) connects from R1 to Ground
• Wire from R1 and R2+R3 connects to Pin 16 (GPIO 23)
• GND connects to Pin 34 (Ground)

Ultrasonic sensor 2:
• VCC connects to Pin 2 (5V)
• Trig connects to Pin 11 (GPIO 27)
• Echo connects to R1 (1k OHM)
• R2 and R3 (1k OHM + 1 k OHM) connects from R1 to Ground
• Wire from R1 and R2+R3 connects to Pin 16 (GPIO 24)
• GND connects to Pin 34 (Ground)

Ultrasonic sensor 3:
• VCC connects to Pin 2 (5V)
• Trig connects to Pin 11 (GPIO 22)
• Echo connects to R1 (1k OHM)
• R2 and R3 (1k OHM + 1 k OHM) connects from R1 to Ground
• Wire from R1 and R2+R3 connects to Pin 16 (GPIO 10)
• GND connects to Pin 34 (Ground)
--------------------------------------------------------------------

Date: 03/09/2023
Author: Asad Maza - Group 3

====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
"""

# Imports
import RPi.GPIO as GPIO
import time
from time import sleep as sleep

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define GPIO pins
sensor_data = [
    {'TRIG': 17, 'ECHO': 23},  # Sensor 1
    {'TRIG': 27, 'ECHO': 24},  # Sensor 2
    {'TRIG': 22, 'ECHO': 10}   # Sensor 3
]

# Setup GPIO
for sensor in sensor_data:
    GPIO.setup(sensor['TRIG'], GPIO.OUT)
    GPIO.setup(sensor['ECHO'], GPIO.IN)
    
# Define distance measuring function
def distance(TRIG, ECHO):
    # Trigger sensor
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    # Measure start and stop time
    while GPIO.input(ECHO) == 0:
        start_time = time.time()
    while GPIO.input(ECHO) == 1:
        stop_time = time.time()

    # Calculate distance
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2

    return distance

# main loop
if __name__ == '__main__':
    try:
        while True:
            for i, sensor in enumerate(sensor_data):
                dist = distance(sensor['TRIG'], sensor['ECHO'])
                print(f"Measured Distance from Sensor {i+1} = {dist:.1f} cm")
            print('-'*30)
            time.sleep(1)

    # Break out
    except KeyboardInterrupt:
        print("Measurement stopped")
        GPIO.cleanup() 
