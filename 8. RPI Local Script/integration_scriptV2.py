"""
====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
Test file for Smart Parking System Integration.

v3.1 Changelog :
- Initialisation changed, makes it clearer when system is running
- removed random commented out code, cleaned code
- changed print output to show distance and sensors for debugging
- added print output for stopping script
- updated conditional logic's distance threshold
- updated bay dictionary, mapped type of bay (reserved and general)
- updated time.sleep(1) instead of 2 in read_distance function

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
import json
import os
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import Adafruit_CharLCD as LCD
from gpio_reset import all_pins_to_off
import logging
# from PiicoDev_QMC6310 import PiicoDev_QMC6310
# from PiicoDev_Unified import sleep_ms




# # Initialise threshold value
# sensor_threshold = 0.015 # in percent (e.g. 10% = 0.10)
# 
# base_val_threshold = 0.005 # in percent (e.g. 2% = 0.02)
# # Initialise sensor
# magSensor = PiicoDev_QMC6310(range=3000)
# 
# 
# 
# def get_average(data_list):
#     return sum(data_list) / len(data_list)
# 
# def collect_data_for_seconds(seconds):
#     data_list = []
#     for _ in range(seconds):
#         raw_data = magSensor.read()
#         z_axis_strength = raw_data['z']
#         data_list.append(z_axis_strength)
#         sleep_ms(1000)
#     return data_list
# 
# 
# # Loop until a valid default value is obtained
# while True:
#     # Read the data of the previous ten seconds
#     data_list = collect_data_for_seconds(10)
#     
#     # If the data fluctuation is less than 2%, set it as the default value
#     avg_value = get_average(data_list)
#     max_value = max(data_list)
#     min_value = min(data_list)
#     fluctuation = (max_value - min_value) / avg_value
#     
#     if fluctuation < base_val_threshold:
#         default_value = avg_value
#         break
# 
# print("Average default value for magnetosensor:", default_value)


# Connection debugging
logging.basicConfig(level=logging.DEBUG)

# Set all pins to off before main code
all_pins_to_off()

# Topic Constant
BAY_STATUS_CHANGE_FROM_DEVICE = "BAY_STATUS_CHANGE_FROM_DEVICE" # publish to this
SEND_BAY_CHANGE_STATUS_WHEN_RESERVED = "SEND_BAY_CHANGE_STATUS_WHEN_RESERVED" # subscribe to this
SEND_BAY_CHANGE_STATUS_WHEN_RESERVATION_EXPIRED = "SEND_BAY_CHANGE_STATUS_WHEN_RESERVATION_EXPIRED" # subscribe to this

# AWS IoT client setup
myMQTTClient = AWSIoTMQTTClient("testCertif")
myMQTTClient.configureEndpoint("a30y98prchbi0n-ats.iot.us-west-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials(os.path.abspath(os.getcwd())+"/testCertif/root-CA.crt",
                                      os.path.abspath(os.getcwd())+"/testCertif/testCertif.private.key",
                                      os.path.abspath(os.getcwd())+"/testCertif/testCertif.cert.pem")

# Confirm MQTT Connection
myMQTTClient.connect()

#GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup GPIOs for LCD
lcd_rs        = 25
lcd_en        = 9
lcd_d4        = 11
lcd_d5        = 21
lcd_d6        = 20
lcd_d7        = 13
lcd_backlight = 4
lcd_columns   = 16
lcd_rows      = 2

# Initialise LCD object
lcd = LCD.Adafruit_CharLCD(
    lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
    lcd_columns, lcd_rows, lcd_backlight)
#Set cursor blinks off
lcd.blink(False)


# LED, sensor, state and type mapping for each bay
bay_mapping = {
    'A1': {'red_led': 6, 'yellow_or_green_led': 5, 'sensor_trigger': 8, 'sensor_echo': 7, 'state': 0, 'prev_state': 0, 'bay_type': 1, 'is_bay_booked' : 0},
    'A3': {'red_led': 27, 'yellow_or_green_led': 17, 'blue_led':10, 'sensor_trigger': 0, 'sensor_echo': 1,'state': 0, 'prev_state': 0, 'bay_type': 2, 'is_bay_booked' : 0}
}

# Initialise interval variables for publish and check bay status
publish_bay_mapping_interval = 10  # Publish every 10 seconds
check_bay_status_interval = 0.5  # Queries bay status every (1 + 0.5) seconds

last_publish_time = time.time()
last_check_time = time.time()

last_publish_time = 0
last_check_time = time.time()

def customCallback(client, userdata, message):
    if(message.topic == SEND_BAY_CHANGE_STATUS_WHEN_RESERVED):
        print("Received a reservation from flask : ")
        getAReservationFromFlask(message.payload.decode("utf-8"))
    elif(message.topic == SEND_BAY_CHANGE_STATUS_WHEN_RESERVATION_EXPIRED):
        print("Received a reservation expiry from flask : ")
        getAReservationExpiryFromFlask(message.payload.decode("utf-8"))

myMQTTClient.subscribe(SEND_BAY_CHANGE_STATUS_WHEN_RESERVED, 1, customCallback)
myMQTTClient.subscribe(SEND_BAY_CHANGE_STATUS_WHEN_RESERVATION_EXPIRED, 1, customCallback)

def getDataFromJsonString(jsonString):
    commaSplit = jsonString.split(',')
    onlyData = commaSplit[1].replace('{', '')
    onlyData = onlyData.replace('}', '')
    onlyData = onlyData.split(':')
    parkingName = onlyData[1].replace('"','').strip()
    return parkingName

def getAReservationFromFlask(messagePayload):
    json_object = json.loads(messagePayload)
    parkingName = getDataFromJsonString(json_object)
    global available_bays
    available_bays -= 1
    bay_mapping[parkingName]["is_bay_booked"] = 1
    GPIO.output(info['yellow_or_green_led'], False)
    GPIO.output(info['red_led'], True)

def getAReservationExpiryFromFlask(messagePayload):
    json_object = json.loads(messagePayload)
    parkingName = getDataFromJsonString(json_object)
    global available_bays
    available_bays += 1
    bay_mapping[parkingName]["is_bay_booked"] = 0
    GPIO.output(info['yellow_or_green_led'], True)
    GPIO.output(info['red_led'], False)

# Define distance measuring function
def read_distance(TRIG, ECHO):
    GPIO.output(TRIG, False)
    time.sleep(1.5) # changed sleep time to read faster.
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

# Setup GPIO for LEDs
for bay, info in bay_mapping.items():
    GPIO.setup(info['yellow_or_green_led'], GPIO.OUT)
    GPIO.setup(info['red_led'], GPIO.OUT)
    GPIO.setup(info['sensor_trigger'], GPIO.OUT)
    GPIO.setup(info['sensor_echo'], GPIO.IN)

# GPIO.setup(bay_mapping['A3']['blue_led'], GPIO.OUT)

# Initialise state and max and min bays
lcd.clear()
available_bays = 0
max_bays = len(bay_mapping)
min_bays = 0
lcd.message("""Initialising
System""")
for bay,  info in bay_mapping.items():
    GPIO.output(info['yellow_or_green_led'], True)
    GPIO.output(info['red_led'], False)

check_bay_status_interval = 0.5  # Queries bay status every (1.5 + 0.5) seconds
last_publish_time = time.time()
last_check_time = time.time()

threshold_max = 20.0 # in cm
threshold_min = 0.0 # in cm

# initalise continue_loop to Yes
continue_loop = "Yes"






# main loop
try:
    print("checkPoint")
    initial_publish = True # Flag to force initial publish
    state_changed = False  # Flag to indicate whether state has changed
    
    while True:
        available_bays = 0
        current_time = time.time()
#         raw_data = magSensor.read()
#         z_axis_strength = raw_data['z']                    
        # Check status of each bay if enough time has elapsed since the last check   
        if current_time - last_check_time >= check_bay_status_interval:
            last_check_time = current_time
            
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            for bay, info in bay_mapping.items():
                dist_measured = read_distance(info['sensor_trigger'], info['sensor_echo'])
                # Remember previous state
                info['prev_state'] = info['state']
                
                # Check toy car presence based on Ultrasonic sensor distance measurement and Magnetometer conditional
                if dist_measured <= threshold_max and dist_measured >= threshold_min:  # and abs((z_axis_strength - default_value) / default_value) > sensor_threshold:
#                     print("magnetometer difference :"+ str((z_axis_strength - default_value) / default_value))
#                     print("Z-axis strength:", z_axis_strength)
                    print("detected car")
                    if info['state'] == 0:
                        info['state'] = 1
                        GPIO.output(info['yellow_or_green_led'], False)
                        GPIO.output(info['red_led'], True)
                        bayStatus = {"state":info['state']}
                        result = {
                            bay : bayStatus
                        }
                        message = json.dumps({"timestamp": timestamp, "data": result})
                        try:
                            myMQTTClient.publish(BAY_STATUS_CHANGE_FROM_DEVICE, message, 1)
                        except Exception as e:
                            print(f"An exception occurred while publishing: {e}")
                        
                else:
                    print("no car detected")
                    
                    if info['state'] == 1:
                        info['state'] = 0
                        GPIO.output(info['yellow_or_green_led'], True)
                        GPIO.output(info['red_led'], False)
                        bayStatus = {"state":info['state']}
                        result = {
                            bay : bayStatus
                        }
                        message = json.dumps({"timestamp": timestamp, "data": result})
                        try:
                            myMQTTClient.publish(BAY_STATUS_CHANGE_FROM_DEVICE, message, 1)
                        except Exception as e:
                            print(f"An exception occurred while publishing: {e}")                        
                print(f"{bay} Distance: {dist_measured} Bay State: {info['state']}")
                # Update available bays based on state
                if info['state'] == 0 and available_bays < max_bays:
                    available_bays += 1
                if info['state'] == 1 and available_bays > min_bays:
                    available_bays -= 1

            lcd.clear()
            lcd.message(f"Available bays:{available_bays}")
            
            print("-"*50)
# Break out
except KeyboardInterrupt:
    print("Terminating module")
#     lcd.clear()
#     all_pins_to_off()
#     
# # Cleanup
# finally:
#     all_pins_to_off()
