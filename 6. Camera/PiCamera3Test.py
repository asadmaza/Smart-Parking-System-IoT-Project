"""
====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
Test file for 1 Pi Camera 3 module for the project

Components required:
x1 Pi Camera 3 module
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)

Code description:
This code tests a Pi Camera 3 module with a Raspberry Pi, the code
uses PiCamera2 and OpenCV to livestream in a window on Raspberry Pi.

--------------------------------------------------------------------
Setup:
Ensure you connect the Pi Camera 3 module to the Camera port.

Remember to install OpenCV library, type commands in terminal:
sudo apt-get update
sudo apt-get install python3-opencv
Y

sudo apt-get install libqt5gui5 libqt5test5 python3-sip^
python3-pyqt5 libjasper-dev libatlas-base-dev libhdf5-dev^
libhdf5-serial-dev -y

pip3 install opencv-contrib-python==4.5.5.62
pip3 install -U numpy

check installation with these commands:
python3
import cv2
cv2.__version__
should return 4.5.5

Disable the camera through terminal or settings:
Terminal -> sudo raspi-config -> Disable Camera
Settings -> Interface Options -> Camera -> Disable
- legacy Camera settings are for Pi Camera module 2, not 3

Testing camera natively through terminal:
libcamera-hello -t 0
-> preview window, CTRL + C to terminate



--------------------------------------------------------------------
Code adapted from:
1. https://my.cytron.io/tutorial/face-detection-on-
raspberry-pi4-using-opencv-and-camera-module

2. PiCamera 2 Beta release docs
https://pypi.org/project/picamera2/

https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf
- resolutions

Date: 05/09/2023
Author: Asad Maza - Group 3

====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
"""

import cv2
from picamera2 import Picamera2

# Initialise camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()
print("-"*80)
print("""Press CTRL + C in IDE to quit the preview window properly.
Alternatively, press Q in camera preview window.""")

# Loop to continually get frames from camera
try:
    while True:
        im = picam2.capture_array()
        cv2.imshow("Pi Camera Module 3 Preview", im)
        # Press 'q' to close the window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # Release capture and destory all windows
    cv2.destroyAllWindows()
    picam2.stop_preview()
except KeyboardInterrupt:
    # Release capture and destory all windows
    cv2.destroyAllWindows()
    picam2.stop_preview()