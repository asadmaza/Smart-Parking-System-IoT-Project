# import RPi.GPIO as GPIO
# import time
from PiicoDev_QMC6310 import PiicoDev_QMC6310
from PiicoDev_Unified import sleep_ms
# from gpio_reset import all_pins_to_off
# 
# # Set all pins to off before main code
# all_pins_to_off()
# 
# # GPIO config
# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
# sensor = 16
# buzzer = 18

# Read the magnetic field strength and determine if a magnet is nearby



magSensor = PiicoDev_QMC6310(range=3000) # initialise the magnetometer

threshold = 80 # microTesla or 'uT'.

while True:

    strength = magSensor.readMagnitude()   # Reads the magnetic-field strength in microTesla (uT)
    myString = str(strength) + ' uT'       # create a string with the field-strength and the unit
    print(myString)                        # Print the field strength
    
    if strength > threshold:               # Check if the magnetic field is strong
        print('Strong Magnet!')

    sleep_ms(1000)