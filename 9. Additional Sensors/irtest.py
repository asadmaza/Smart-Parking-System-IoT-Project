import RPi.GPIO as GPIO
import time
from gpio_reset import all_pins_to_off

# Set all pins to off before main code
all_pins_to_off()

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
sensor = 19
buzzer = 18

GPIO.setup(sensor,GPIO.IN)
GPIO.setup(buzzer,GPIO.OUT)

GPIO.output(buzzer,False)
print("IR Sensor Ready.....")
print(" ")

try: 
   while True:
      if GPIO.input(sensor):
          GPIO.output(buzzer,True)
          print("Object Detected")
          while GPIO.input(sensor):
              time.sleep(0.2)
      else:
          print("no object")
          GPIO.output(buzzer,False)
          time.sleep(0.2)

except KeyboardInterrupt:
    all_pins_to_off()