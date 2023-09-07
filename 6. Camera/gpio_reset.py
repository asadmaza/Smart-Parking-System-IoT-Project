"""
This module is used to ensure all GPIO pins are off.
Please use this before main code to avoid issues with
incorrect states on GPIO pins.

----------------------------------------------------------
Setup:
Place in folder for every Python script, add before and
after main code is run.


N/A
----------------------------------------------------------

Date: 07/09
Author: Asad Maza - Group 3
"""

# Imports
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
# Set all Raspberry Pi 3 GPIO pins to "off" state
def all_pins_to_off():
    GPIO.setmode(GPIO.BCM)
    all_pins = list(range(2, 26))  # GPIO 2 to GPIO 26
    # Set each pin as an output and turn it off
    for pin in all_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, False)