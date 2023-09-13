"""
====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
Test file to send single bay data to a Cloud Platform - AWS IoT Core.

Changelog v2.1:
- Updated code to publish data when initialised
- Updated bay mapping to include booking for booking option via
WebApp for reserved bay - can map another LED to this (White/Blue)
- Only send data when state of bay actually changes, added previous
state to dictionary
- updated sleep in distance reading to 1s and bay interval check
to 0.5s to avoid random state changes (issue with measuring)

Components required:
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)
x1 5mm Red LED GPIO 
x1 5mm Green LED
x2 330 ohm resistors
x1 Ultrasonic Sensor

Code description:
Simulates a single bay and sends data to AWS IoT Core. Sends bay
status every 10 seconds, can modify frequency in
publish_bay_mapping_interval. QoS = 1 (deliver atleast once)
Check out plan doc page 2 for example of what successful test looks
like.
--------------------------------------------------------------------
Setup:

Bay 1 - Reserved:
LED(GPIO 2) - Yellow LED
LED(GPIO 3) - Red LED
Ultrasonic Sensor:
• VCC connects to Pin 2 (5V)
• Trig connects to Pin 11 (GPIO 17)
• Echo connects to R1 (1k OHM)
• R2 and R3 (1k OHM + 1 k OHM) connects from R1 to Ground
• Wire from R1 and R2+R3 connects to Pin 16 (GPIO 23)
• GND connects to Pin 34 (Ground)

Setup AWS IoT Core:
If you haven't already done Basic pubsub test.py then:
1. Create device on AWS IoT Core, guide in the file
"Plan for Backend and Front End.docx"

2. Install AWSIoTPythonSDK, using terminal:
pip install AWSIoTPythonSDK
Successfully installed AWSIoTPythonSDK-1.5.2

Ensure you have successfully run "mqtt pubsub test.py" first or
this won't work.

Troubleshooting:
1. Security policy is setup so that client can connect and
pub/sub
2. Check configuration for MQTT Client - name of client and
credentials
--------------------------------------------------------------------

Date: 12/09/2023
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
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from gpio_reset import all_pins_to_off
import logging

# Connection debugging
logging.basicConfig(level=logging.DEBUG)

# Set all pins to off before main code
all_pins_to_off()

# AWS IoT client setup
myMQTTClient = AWSIoTMQTTClient("Asad-RaspberryPi")
myMQTTClient.configureEndpoint("a2mqsm6nqkmbh6-ats.iot.ap-southeast-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/asadRPI/Desktop/AWS IoT Core/root-CA.crt",
                                      "/home/asadRPI/Desktop/AWS IoT Core/RaspberryPi-Asad.private.key",
                                      "/home/asadRPI/Desktop/AWS IoT Core/RaspberryPi-Asad.cert.pem")

# Confirm MQTT Connection
myMQTTClient.connect()

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

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

# Mapping Bay
# {red_led = GPIO mapping, yellow_or_green_led = GPIO mapping, sensor_trigger =  GPIO map sensor, sensor_echo = GPIO map sensor,
# bay_state (free = 0, occupied = 1), prev_state, bay_type (reserved or general), is_bay_booked( 0 = No, 1 = yes)
bay_mapping = {
    'Bay1': {'red_led': 2, 'yellow_or_green_led': 3, 'sensor_trigger': 17, 'sensor_echo': 23, 'state': 0, 'prev_state': 0, 'bay_type': 'reserved', 'is_bay_booked' : 0}
            }

# Initialise interval variables for publish and check bay status
publish_bay_mapping_interval = 10  # Publish every 10 seconds
check_bay_status_interval = 0.5  # Queries bay status every (1 + 0.5) seconds

last_publish_time = time.time()
last_check_time = time.time()

last_publish_time = 0
last_check_time = time.time()


# GPIO setup
for bay, info in bay_mapping.items():
    GPIO.setup(info['yellow_or_green_led'], GPIO.OUT)
    GPIO.setup(info['red_led'], GPIO.OUT)
    GPIO.setup(info['sensor_trigger'], GPIO.OUT)
    GPIO.setup(info['sensor_echo'], GPIO.IN)


try:
    initial_publish = True # Flag to force initial publish
    state_changed = False  # Flag to indicate whether state has changed
    
    while True:
        current_time = time.time()
        
        # Check status of each bay if enough time has elapsed since the last check
        if current_time - last_check_time >= check_bay_status_interval:
            last_check_time = current_time
            
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            for bay, info in bay_mapping.items():
                dist_measured = read_distance(info['sensor_trigger'], info['sensor_echo'])
                
                # Remember previous state
                info['prev_state'] = info['state']
                
                # Check toy car presence based on Ultrasonic sensor distance measurement
                # Current threshold is 5cm
                if dist_measured <= 5.0 and dist_measured >= 0.0:
                    GPIO.output(info['yellow_or_green_led'], False)
                    GPIO.output(info['red_led'], True)
                    if info['state'] == 0:
                        info['state'] = 1
                        state_changed = True  # State has changed
                
                elif dist_measured > 5.0:
                    GPIO.output(info['yellow_or_green_led'], True)
                    GPIO.output(info['red_led'], False)
                    if info['state'] == 1:
                        info['state'] = 0
                        state_changed = True  # State has changed
                
                print(f"{bay} Distance: {dist_measured} State: {info['state']}")
                
        # Publish if either any state has changed or for initial publish
        if (state_changed or initial_publish) and current_time - last_publish_time >= publish_bay_mapping_interval:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Update timestamp here
            last_publish_time = current_time
            state_changed = False  # Reset state flag
            initial_publish = False  # Reset initial_publish flag
            
            print("-"*80)
            print("To stop script correctly, press CTRL + C, ensure all_pins_to_off() function runs")
            print("Publishing bay_mapping to AWS IoT")
            
            try:
                myMQTTClient.publish("sdk/test/python", json.dumps({"timestamp": timestamp, "data": bay_mapping}), 1)
            except Exception as e:
                print(f"An exception occurred while publishing: {e}")

        time.sleep(0.01)
        
except KeyboardInterrupt:
    print("Terminating and cleaning up")
    all_pins_to_off()
    myMQTTClient.disconnect()