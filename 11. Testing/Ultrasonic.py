"""
Sensor testing file to measure the accuracy and the detection of
a car in the bay. We will use this file to test a toy car and a
real car.

Components required:
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)
x1 5mm Red LED GPIO 
x1 5mm Green LED
x2 330 ohm resistors
x1 Ultrasonic Sensor

Code description:
File to test the measurement accuracy, prints out value when the
code is run:
- Distance measured when bay is occupied
- Distance measured when bay is free
- % Accuracy with actual (ground truth) measured using measuring
tape or micrometer.
--------------------------------------------------------------------
Setup:
Will need to create a circuit diagram for the connection of
ultrasonic sensor and 2 LEDs.

Ensure the Ultrasonic sensor is connected as described:
• VCC connects to Pin 2 (5V)
• Trig connects to Pin 11 (GPIO 17)
• Echo connects to R1 (1k OHM)
• R2 and R3 (1k OHM + 1 k OHM) connects from R1 to Ground
• Wire from R1 and R2+R3 connects to Pin 16 (GPIO 23)
• GND connects to Pin 34 (Ground)

LED(GPIO 2) - Green LED
LED(GPIO 3) - Red LED
--------------------------------------------------------------------

Date: 10/10/2023
Author: Asad Maza - Group 3
"""
# Imports
import RPi.GPIO as GPIO
import time
import json
from gpio_reset import all_pins_to_off

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

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Mapping bay information
bay_mapping = {
    'Bay1': {'red_led': 2, 'yellow_or_green_led': 3,
             'sensor_trigger': 17, 'sensor_echo': 23,
             'state': 0, 'prev_state': 0,
             'bay_type': 'reserved', 'is_bay_booked' : 0}
    }

# Initialise interval variables for publish and check bay status and threshold for distance
check_bay_status_interval = 0.5  # Queries bay status every (1.5 + 0.5) seconds
last_publish_time = time.time()
last_check_time = time.time()

threshold_max = 5.0 # in cm
threshold_min = 0.0 # in cm

# initalise continue_loop to Yes
continue_loop = "Yes"

try:
    initial_publish = True # Flag to force initial publish
    state_changed = False  # Flag to indicate whether state has changed
    
    while continual_loop = "Yes":
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
                if dist_measured <= threshold_max and dist_measured >= threshold_min:
                    GPIO.output(info['yellow_or_green_led'], False)
                    GPIO.output(info['red_led'], True)
                    if info['state'] == 0:
                        info['state'] = 1
                        state_changed = True  # State has changed
                
                elif dist_measured > threshold_max:
                    GPIO.output(info['yellow_or_green_led'], True)
                    GPIO.output(info['red_led'], False)
                    if info['state'] == 1:
                        info['state'] = 0
                        state_changed = True  # State has changed
                
                print(f"{bay} Distance: {dist_measured} Bay State: {info['state']}")
                continue_loop = "No"
                continue_loop = input("Do you require another reading? -Please reply with Yes")
                
#         # Publish if either any state has changed or for initial publish
#         if (state_changed or initial_publish) and current_time - last_publish_time >= publish_bay_mapping_interval:
#             timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Update timestamp here
#             last_publish_time = current_time
#             state_changed = False  # Reset state flag
#             initial_publish = False  # Reset initial_publish flag
#             
#             print("-"*80)
#             print("To stop script correctly, press CTRL + C, ensure all_pins_to_off() function runs")
#             print("Publishing bay_mapping to AWS IoT")
#         time.sleep(0.01)
        
except KeyboardInterrupt:
    print("Terminating and cleaning up")
    all_pins_to_off()
