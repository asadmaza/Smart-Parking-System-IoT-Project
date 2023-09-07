"""
====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
Test file for 1 LCD Display: 16 x 2 Characters (HD44780)
and 1 ultrasonic sensor for the project.

Components required:
x1 LCD 16x2 (HD44780)
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)
x1 10K ohm potentiometer
x1 HC-SR04 Ultrasonic Sensor
x3 1K ohm resistor


Code description:
This code tests an LCD 16x2 (HD44780) and an Ultrasonic distance
sensor with a Raspberry Pi to measure, print and display the
distance to an object in centimeters, updating every second.

--------------------------------------------------------------------
Setup:
Need to setup first on https://pimylifeup.com/raspberry-pi-lcd-16x2/

Remember to install the Adafruit library and run the code as root
(use sudo). I have created a file install_dependencies.sh to help out

Ensure you connect everything as below:

Ultrasonic sensor:
• VCC connects to Pin 2 (5V)
• Trig connects to Pin 11 (GPIO 17)
• Echo connects to R1 (1k OHM)
• R2 and R3 (1k OHM + 1 k OHM) connects from R1 to Ground
• Wire from R1 and R2+R3 connects to Pin 16 (GPIO 23)
• GND connects to Pin 34 (Ground)

LCD Display 16x02:
• LCD Pin 1 (Ground) to Pin 39 (GND)
• LCD Pin 2 (VCC/5V) to Pin 2 (5V)
• LCD Pin 3 (V0) to middle leg of Potentiometer
• LCD Pin 4 (RS) to Pin 22 (GPIO 25)
• LCD Pin 5 (RW) to Pin 39 (GND)
• LCD Pin 6 (EN) to Pin 21 (GPIO 09)
• LCD Pin 11 (D4) to Pin (GPIO 11)
• LCD Pin 12 (D5) to Pin (GPIO 05)
• LCD Pin 13 (D6) to Pin (GPIO 06)
• LCD Pin 14 (D7) to Pin (GPIO 13)
• LCD Pin 15 (LED +) to Pin 2 (5V)
• LCD Pin 16 (LED -) to 39 (GND)
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
import Adafruit_CharLCD as LCD
from gpio_reset import all_pins_to_off

# Set all pins to off before main code
all_pins_to_off()


# Setup GPIO for Ultrasonic sensor
TRIG = 17
ECHO = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Setup GPIO for LCD
lcd_rs        = 25 # LCD Pin 4 (RS) to Pin 22 (GPIO 25)
lcd_en        = 9  # LCD Pin 6 (EN) to Pin 21 (GPIO 09)
lcd_d4        = 11 # LCD Pin 11 (D4) to Pin (GPIO 11)
lcd_d5        = 5  # LCD Pin 12 (D5) to Pin (GPIO 05)
lcd_d6        = 6  # LCD Pin 6 (EN) to Pin 21 (GPIO 09)
lcd_d7        = 13 # LCD Pin 14 (D7) to Pin (GPIO 13)
lcd_backlight = 4
lcd_columns   = 16
lcd_rows      = 2

# Initialise LCD object
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)
# Set cursor blinks off
lcd.blink(False)
# Define distance measuring function
def distance():
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



# main loop
try:
    while True:
        dist = distance()
        print("Distance:",dist,"cm")

        lcd.clear()
        lcd.message(f"Dist: {dist}")
        
        time.sleep(1)

# Break out
except KeyboardInterrupt:
    print("Measurement stopped by user")
    lcd.clear()
    all_pins_to_off()
    
finally:
    all_pins_to_off()