# LEDs in pin 5 and 6

# Kexin's Code for real car detection using magnetometer
from PiicoDev_QMC6310 import PiicoDev_QMC6310
from PiicoDev_Unified import sleep_ms


# Initialise threshold value
sensor_threshold = 0.10 # in percent (e.g. 10% = 0.10)

base_val_threshold = 0.02 # in percent (e.g. 2% = 0.02)
# Initialise sensor
magSensor = PiicoDev_QMC6310(range=3000)

# Imports
import RPi.GPIO as GPIO
import time
from gpio_reset import all_pins_to_off

# Initialise the GPIO pins

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Initialise the LEDs
GPIO.setup([6,5], GPIO.OUT)
green_LED = GPIO.output(6, GPIO.LOW)
red_LED = GPIO.output(5, GPIO.HIGH)

def get_average(data_list):
    return sum(data_list) / len(data_list)

def collect_data_for_seconds(seconds):
    data_list = []
    for _ in range(seconds):
        raw_data = magSensor.read()
        z_axis_strength = raw_data['z']
        data_list.append(z_axis_strength)
        sleep_ms(1000)
    return data_list

# Loop until a valid default value is obtained
while True:
    # Read the data of the previous ten seconds
    data_list = collect_data_for_seconds(10)
    
    # If the data fluctuation is less than 2%, set it as the default value
    avg_value = get_average(data_list)
    max_value = max(data_list)
    min_value = min(data_list)
    fluctuation = (max_value - min_value) / avg_value
    
    if fluctuation < base_val_threshold:
        default_value = avg_value
        break

# main loop
try:
    while True:
        raw_data = magSensor.read()
        z_axis_strength = raw_data['z']
        print("observation value : "+ str(default_value))
        if abs((z_axis_strength - default_value) / default_value) > sensor_threshold:
            print("magnetometer difference :"+ str((z_axis_strength - default_value) / default_value))
            print("detected car")
            # Change LED status
            green_LED = GPIO.output(6, GPIO.HIGH)
            red_LED = GPIO.output(5, GPIO.LOW)
        else:
            print("no car")
            # change LED status
            green_LED = GPIO.output(6, GPIO.LOW)
            red_LED = GPIO.output(5, GPIO.HIGH)
        sleep_ms(1000)
except KeyboardInterrupt:
    print("\nProgram terminated.")