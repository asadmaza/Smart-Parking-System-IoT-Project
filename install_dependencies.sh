#!/bin/bash

# Clone the Adafruit library
git clone https://github.com/pimylifeup/Adafruit_Python_CharLCD.git

# Navigate to the directory
cd Adafruit_Python_CharLCD

# Run the setup file
sudo python setup.py install

# Navigate back to the original directory
cd ..