"""
====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
Test file for 1 HC-SR04 Ultrasonic sensor.
Use this file to test 1 ultrasonic sensor for the project.

Components required:
x1 HC-SR04 Ultrasonic Sensor
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)
x3 1K ohm resistor

Code description:
This code controls an HC-SR04 ultrasonic sensor with a Raspberry Pi
to measure and print the distance to an object in centimeters,
updating every second.

--------------------------------------------------------------------
Setup:

Ensure the Ultrasonic sensor is connected as described:
• VCC connects to Pin 2 (5V)
• Trig connects to Pin 11 (GPIO 17)
• Echo connects to R1 (1k OHM)
• R2 and R3 (1k OHM + 1 k OHM) connects from R1 to Ground
• Wire from R1 and R2+R3 connects to Pin 16 (GPIO 23)
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
TRIG = 17  # Trigger Pin
ECHO = 23  # Echo Pin

# Setup GPIO
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Define distance measuring function
def distance():
    # Set Trigger to HIGH
    GPIO.output(TRIG, True)

    # Set Trigger after 0.01ms to LOW
    sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    # Save the start time
    while GPIO.input(ECHO) == 0:
        start_time = time.time()

    # Save time of arrival
    while GPIO.input(ECHO) == 1:
        stop_time = time.time()

    # Calculate time difference between start and arrival
    time_elapsed = stop_time - start_time

    # Calculate distance: multiply with speed of sound (34300 cm/s)
    # and divide by 2, as there and back
    distance = (time_elapsed * 34300) / 2

    return distance

# main loop
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print(f"Measured Distance = {dist:.1f} cm")
            sleep(1)

    # Break out
    except KeyboardInterrupt:
        print("Measurement stopped")
        GPIO.cleanup() 
