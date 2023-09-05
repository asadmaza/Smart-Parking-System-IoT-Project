"""
Test file for a single LED.
Alternates the LED state (ON/OFF) every 1s.
Use this file to test any GPIO ports or LEDs.

Components required:
x1 5mm LED
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)
x1 220 - 330 ohm resistor

Date: 03/09/2023
Author: Asad Maza - Group 3
"""
# Imports
import RPI.GPIO as GPIO
from time import sleep as sleep

# Ensure LED is connected to GPIO 4
lonely_led = LED(4)

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(lonley_led, GPIO.OUT)

# Indefinite loop for LED
try:
    while True:
        GPIO.output(lonely_LED, True)
        print("LED on")
        sleep(1)
        GPIO.output(lonely_LED, False)
        print("LED off")
        sleep(1)

# Break out
except KeyboardInterrupt:
    print("Terminating module")
    GPIO.cleanup()

# Cleanup
finally:
    GPIO.cleanup()      
