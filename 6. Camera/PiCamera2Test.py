"""
====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
Test file for 1 Pi Camera 2 module for the project

Components required:
x1 Pi Camera 2 module
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)

Code description:
This code tests a Pi Camera 2 module with a Raspberry Pi, the code
uses OpenCV to livestream in a window on Raspberry Pi.

--------------------------------------------------------------------
Setup:
Ensure you connect the Pi Camera 2 module to the Camera port.

Remember to install OpenCV library, commands in terminal:
sudo apt update
sudo apt install python3-opencv

Enable the camera through terminal or settings:
Terminal -> sudo raspi-config -> Enable Camera
Settings -> Interface Options -> Camera -> Enable



Testing camera natively through terminal:
-	Is camera detected? -> vcgencmd get_camera
    if detected, returns: supported=1 detected=1 

-	Test capture image -> raspistill -o test.jpg
    saves test.jpg in current folder

-	Test video capture -> raspivid -o testVid.h264 -t 10000
    Saves 10s video testVid.h264 in current folder
--------------------------------------------------------------------

Date: 04/09/2023
Author: Asad Maza - Group 3

====================================================================
ONLY RUN AFTER YOU HAVE DOUBLE CHECKED CONNECTIONS AS COMPONENTS
CAN BE DAMAGED IF INCORRECTLY WIRED.
====================================================================
"""

# Import
import cv2

# Initialise camera object
videoCapture = cv2.VideoCapture(0)

# Set video capture width and height
videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Alt code, don't use cause IOT bandwidth issues
# Set video to maximum resolution for Pi Camera v2 
#videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080

while True:
    # Capture frame by frame
    ret, frame = videoCapture.read()
    
    # Display the resulting frame
    cv2.imshow('Pi Camera Test Stream', frame)
    
    # Press 'q' to quit the application
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and destroy all OpenCV windows
videoCapture.release()
cv2.destroyAllWindows()