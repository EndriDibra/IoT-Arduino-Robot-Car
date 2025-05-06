# IoT-Arduino-Robot-Car
This is a project created in IoT course from NKUA-DIND, supervised by Professor Panagiotis Gkonis.

This project concerns the creation of a 3D printed Arduino robot car, that will make use of IoT sensors like temperature, humidity and gas to collect and send these data via a Bluetooth modeule into a Flask server to process them and check for smoke or fire occurance. Ultimately, these data will be processed by a machine learning model [Isolation Forest] for Anomaly detection. In the Flask server, the dataset of the AI model, is enriched with the new real-world data taken from the Robot from its surrounding environment, and is has a function to control the Robot, via keyboard arrows, text and voice commands.

Mechanical Parts:
. 3D Printer Ender3 V3
.3D printer fillament PLA+

Electronic Parts:
.1x Arduino Uno
. M-M, F-F, M-F Jumper wires
.4x DC TT Motors
.4x Rubber wheels
.1x Servo motor
.2x battery packs of 6 Volts in series, so total 12 Volts
.1x battery pack of 9 Volts
.1x L298N Motor driver
.1x DHT11 Temperature and Humidity sensor
.1X Gas sensor
.1x Ultrasonic sensor
.1x HC-05 Bluetooth module

Software:
.Python
.C++ Arduino
.AutoDesk Inventor 2025
.Cura Slicer
