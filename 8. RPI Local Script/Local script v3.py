"""
====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
Test file for Smart Parking System Integration.

v3 Changelog :
- Initialisation changed, makes it clearer when system is running
- removed random commented out code, cleaned code
- changed print output to show distance and sensors for debugging
- added print output for stopping script
- updated conditional logic's distance threshold

Components required:
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)
x6 5mm LED (x3 Red, x1 Yellow, x2 Green)
x6 220 - 330 ohm resistor
x3 HC-SR04 Ultrasonic Sensor
x9 1K ohm resistor
x1 LCD 16x2 (HD44780)
x1 10K ohm potentiometer

Code description:
This is a Smart Parking System local script. 3 Bays in total, one
reserved and two general. There are 2 sets of LEDs per bay and 1
ultrasonic distance sensor per bay that detects whether a bay is
occupied or free and indicates red and green respectively. There
is also and LCD Display that shows available bays.


Bay 1 - Reserved:
LED(GPIO 2) - Yellow LED
LED(GPIO 3) - Red LED
Ultrasonic Sensor 1

Bay 2 - General:
LED(GPIO 4)
LED(GPIO 14)
Ultrasonic Sensor 2

Bay 3 - General:
LED(GPIO 15)
LED(GPIO 18)
Ultrasonic Sensor 3

--------------------------------------------------------------------
Setup:
Need to ensure you have installed Adafruit library, if unsure see
LCD test files.

LEDs
LED(GPIO 2) 	# Bay 1 - Reserved; Red LED
LED(GPIO 3)		# Bay 1 - Reserved; Yellow LED
LED(GPIO 4)		# Bay 2 - General; Red LED
LED(GPIO 14)	# Bay 2 - General; Green LED
LED(GPIO 15)	# Bay 3 - General; Red LED
LED(GPIO 18)	# Bay 3 - General; Green LED

Ultrasonic Sensors
Bay 1 - Reserved - Ultrasonic Sensor 1:
• VCC connects to Pin 2 (5V)
• Trig connects to Pin 11 (GPIO 17)
• Echo connects to R1 (1k OHM)
• R2 and R3 (1k OHM + 1 k OHM) connects from R1 to Ground
• Wire from R1 and R2+R3 connects to Pin 16 (GPIO 23)
• GND connects to Pin 34 (Ground)

Bay 2 - General - Ultrasonic Sensor 2:
• VCC connects to Pin 2 (5V)
• Trig connects to Pin 11 (GPIO 27)
• Echo connects to R1 (1k OHM)
• R2 and R3 (1k OHM + 1 k OHM) connects from R1 to Ground
• Wire from R1 and R2+R3 connects to Pin 16 (GPIO 24)
• GND connects to Pin 34 (Ground)

Bay 3 - General - Ultrasonic Sensor 3:
• VCC connects to Pin 2 (5V)
• Trig connects to Pin 11 (GPIO 22)
• Echo connects to R1 (1k OHM)
• R2 and R3 (1k OHM + 1 k OHM) connects from R1 to Ground
• Wire from R1 and R2+R3 connects to Pin 16 (GPIO 10)
• GND connects to Pin 34 (Ground)

Adafruit LCD Display 16x02:
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

Date: 08/09/2023
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

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup GPIOs for LCD
lcd_rs        = 25
lcd_en        = 9
lcd_d4        = 11
lcd_d5        = 5
lcd_d6        = 6
lcd_d7        = 13
lcd_backlight = 4
lcd_columns   = 16
lcd_rows      = 2

# Initialise LCD object
lcd = LCD.Adafruit_CharLCD(
    lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
    lcd_columns, lcd_rows, lcd_backlight)
# Set cursor blinks off
lcd.blink(False)

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
    'Bay2': {'red_led': 4, 'yellow_or_green_led': 14, 'sensor_trigger': 27, 'sensor_echo': 24, 'state': 0},
    'Bay3': {'red_led': 15, 'yellow_or_green_led': 18, 'sensor_trigger': 22, 'sensor_echo': 10,'state': 0}
}

# Setup GPIO for LEDs
for bay, info in bay_mapping.items():
    GPIO.setup(info['yellow_or_green_led'], GPIO.OUT)
    GPIO.setup(info['red_led'], GPIO.OUT)
    GPIO.setup(info['sensor_trigger'], GPIO.OUT)
    GPIO.setup(info['sensor_echo'], GPIO.IN)

# Initialise state and max and min bays
lcd.clear()
available_bays = 0
max_bays = 3
min_bays = 0
lcd.message("""Initialising
System""")
for bay,  info in bay_mapping.items():
    GPIO.output(info['yellow_or_green_led'], True)

# main loop
try:
    while True:
        available_bays = 0  # Reset the count of available bays        
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
            
            # Update available bays based on state
            if info['state'] == 0:
                available_bays += 1
            # Print for testing purposes
            print(f"{bay} Distance: {dist_measured} State: {info['state']}")
        lcd.clear()
        lcd.message(f"Available bays:{available_bays}")
        print("-"*80)
        print("To stop script correctly, press CTRL + C, ensure all_pins_to_off() function runs")

# Break out
except KeyboardInterrupt:
    print("Terminating module")
    lcd.clear()
    all_pins_to_off()
    
# Cleanup
finally:
    all_pins_to_off()