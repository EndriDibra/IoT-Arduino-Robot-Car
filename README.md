# IoT Smart Robot Car: with Arduino, Sensors, Flask Server, and Machine Learning

## Author
**Endri Dibra**

## Project Overview

This project was developed during the **Internet of Things (IoT)** course at **NKUA-DIND**, under the supervision of **Professor Panagiotis Gkonis**.

It focuses on building a fully functional **3D-printed autonomous robot car** powered by **Arduino Uno**, equipped with multiple environmental sensors, wireless communication, remote control capabilities, and machine learning–based anomaly detection.

The system combines:

- Embedded systems  
- Robotics  
- IoT sensing  
- Wireless communication  
- Real-time monitoring  
- Flask web backend  
- Artificial Intelligence  

The result is a smart robotic platform capable of environmental data collection, movement control, obstacle avoidance, and fire/smoke anomaly detection.

---

## Core Features

### Autonomous / Remote Robot Navigation

The robot supports two operating modes:

### Remote Control Mode
User can control the robot manually via Bluetooth commands:

- Forward  
- Backward  
- Left  
- Right  
- Stop  
- Speed adjustment  

### Autonomous Mode

The robot uses an **ultrasonic sensor** to detect nearby obstacles and automatically:

- Stop  
- Reverse  
- Turn  
- Continue navigation safely  

---

## Environmental Sensing

The robot continuously collects real-world sensor data using onboard IoT modules:

### Temperature & Humidity
Using **DHT11 sensor**

### Gas / Smoke Detection
Using analog gas sensor

### Distance Measurement
Using ultrasonic sensor

Sensor readings are transmitted wirelessly to the server.

---

## Wireless Communication

The system uses an **HC-05 Bluetooth module** to exchange data between the robot and the backend server.

Bluetooth is used for:

- Sending live sensor telemetry  
- Receiving movement commands  
- Mode switching  
- Speed control  

---

## AI / Machine Learning Layer

Collected sensor data is processed using anomaly detection models to identify dangerous environmental conditions such as:

- Smoke presence  
- Fire risk  
- Gas abnormalities  
- Unusual temperature spikes  

### Models Evaluated

- Random Forest  
- XGBoost  
- Isolation Forest  

After comparison, the most effective model can be deployed into production.

---

## Flask Server Dashboard

A Python Flask backend receives sensor data and provides:

- Real-time monitoring  
- Data logging  
- Dataset enrichment with live robot data  
- Keyboard-based robot control  
- AI anomaly prediction  
- Mode switching interface  

---

## Mechanical Construction

The robot chassis was custom-designed and physically assembled using:

### Hardware Fabrication

- **Ender 3 V3 3D Printer**
- PLA+ filament

### Mobility Components

- 4x TT DC Motors  
- 4x Rubber Wheels  
- Servo Motor  

---

## Electronic Components

- Arduino Uno  
- L298N Motor Driver  
- HC-05 Bluetooth Module  
- DHT11 Temperature/Humidity Sensor  
- Gas Sensor  
- Ultrasonic Sensor  
- 12V Battery Supply (dual packs in series)  
- 9V Auxiliary Battery  
- Jumper Wires  

---

## Software Stack

### Programming

- Python  
- Arduino C++  

### Design & CAD

- Autodesk Inventor 2025  
- Cura Slicer  

### AI Libraries

- Scikit-Learn  
- XGBoost  
- Joblib  

### Backend

- Flask  

---

## Repository Structure

### Python AI / Backend Files

- `flaskServer.py` → Flask backend server  
- `randomForest.py` → Random Forest training  
- `XGBoost.py` → XGBoost training  
- `isolationForest.py` → Isolation Forest training  
- `modelComparison.py` → Model benchmarking  
- `sensorData.csv` → Training dataset  

### Saved Models

- `.joblib` trained models  
- scalers for preprocessing  

### Arduino Code

Contains full firmware for:

- Motion control  
- Sensor acquisition  
- Bluetooth communication  
- Autonomous mode logic  

---

## Why This Project Matters

This project demonstrates practical integration of multiple engineering disciplines:

- Robotics  
- IoT  
- Embedded Programming  
- Mechanical Design  
- AI / Machine Learning  
- Backend Development  

It shows how intelligent physical systems can interact with real-world environments and make autonomous decisions.

---

## Future Improvements

Potential next steps:

- WiFi / ESP32 cloud connectivity  
- Mobile app control  
- Live camera streaming  
- GPS navigation  
- SLAM mapping  
- ROS2 integration  
- Li-ion battery management  
- Deep learning fire detection with camera  

---

## Final Note

This project reflects my passion for building systems that combine:

- Hardware + Software  
- AI + Robotics  
- Sensors + Intelligence  
- Real-world engineering + Automation  

from concept design to final implementation.
