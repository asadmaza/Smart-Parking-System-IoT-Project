"""
Test file for 6 LEDs - total in project.
Will turn every LED on for 1s then off and move onto next LED.
Use this file to test the 6 GPIO ports or LEDs.

Components required:
x6 5mm LED
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)
x6 220 - 330 ohm resistor

----------------------------------------------------------
Setup:

Ensure LEDs are connected to correct GPIO ports
The below is reference for the Dictionary

LED(2) 	# Sensor 1 - Reserved; Red LED
LED(3)	# Sensor 1 - Reserved; Yellow LED
LED(4)	# Sensor 2 - General; Red LED
LED(14)	# Sensor 2 - General; Green LED
LED(15)	# Sensor 2 - General; Red LED
LED(18)	# Sensor 2 - General; Green LED
----------------------------------------------------------

Date: 03/09/2023
Author: Asad Maza - Group 3
"""

# Imports
import RPI.GPIO as GPIO
from time import sleep as sleep

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Dictionary of GPIO ports and labelled LEDs
LEDs_dict = {
    2: "S1_Reserved_Red",
    3: "S1_Reserved_Yellow",
    4: "S2_General_Red",
    14: "S2_General_Green",
    15: "S3_General_Red",
    18: "S3_General_Green"
    }

# Setup GPIO as output
for port in LEDs_dict.keys():
    GPIO.setup(port, GPIO.OUT)

# Indefinite loop for LEDs
try:
    while True:
        for port, name in LEDs_dict.items():
            GPIO.output(port, True)
            sleep(1)
            GPIO.output(port, False)

# Break out
except KeyboardInterrupt:
    print("Terminating module")
    GPIO.cleanup()

# Cleanup
finally:
    GPIO.cleanup()      
