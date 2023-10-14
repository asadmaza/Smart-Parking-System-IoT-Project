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
import RPi.GPIO as GPIO
from time import sleep as sleep
from gpio_reset import all_pins_to_off

# Set all pins to off before main code
all_pins_to_off()
# Ensure LED is connected to GPIO 4
first_red = 6
first_green = 5

second_red = 27
first_yellow = 17
blue = 10

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(first_red, GPIO.OUT)
GPIO.setup(first_green, GPIO.OUT)
GPIO.setup(second_red, GPIO.OUT)
GPIO.setup(first_yellow, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)

# Indefinite loop for LED
try:
    while True:
        GPIO.output(first_red, True)
        GPIO.output(first_green, True)
        GPIO.output(second_red, True)
        GPIO.output(first_yellow, True)
        GPIO.output(blue, True)
        print("LED on")
        sleep(1)
        GPIO.output(first_red, False)
        GPIO.output(first_green, False)
        GPIO.output(second_red, False)
        GPIO.output(first_yellow, False)
        GPIO.output(blue, False)
        print("LED off")
        sleep(1)

# Break out
except KeyboardInterrupt:
    print("Terminating module")
    all_pins_to_off()

# Cleanup
finally:
    all_pins_to_off()      
