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
lonely_led = 4

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(lonely_led, GPIO.OUT)

# Indefinite loop for LED
try:
    while True:
        GPIO.output(lonely_led, True)
        print("LED on")
        sleep(1)
        GPIO.output(lonely_led, False)
        print("LED off")
        sleep(1)

# Break out
except KeyboardInterrupt:
    print("Terminating module")
    all_pins_to_off()

# Cleanup
finally:
    all_pins_to_off()      
