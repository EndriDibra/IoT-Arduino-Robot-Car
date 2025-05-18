# Importing the required libraries 
import os
import csv
import json
import time
import serial
import pygame
import requests
from joblib import load
from datetime import datetime
from threading import Thread, Lock
from flask import Flask, request, Response
from requests.exceptions import ConnectionError


# Creating the Flask backend server
app = Flask(__name__)

# Opening serial connection to Arduino
serialCon = serial.Serial('COM7', 9600) 

# Giving Bluetooth time to initialize
time.sleep(2)

# URL of the Flask server
url = 'http://127.0.0.1:5000/receive_data'

# Defining the path to the CSV file
csvFile = 'sensorData.csv'

# Loading pre-trained model and scaler
model = load('randomForest_model.joblib')
scaler = load('randomForest_scaler.joblib')

# Thread-safe protection, for data reading and fetching sync
dataLock = Lock()

# Variable to store the latest temperature, humidity and Gas values
latestData = {"Temperature": None, "Humidity": None, "Gas":None}


# Waiting for server to be ready
def wait_for_server(url, retries=10, delay=1):
    
    for _ in range(retries):
    
        try:
    
            r = requests.get(url)

            # Acceptable for readiness
            if r.status_code in [200, 404]:
    
                return True
    
        except ConnectionError:
    
            time.sleep(delay)
    
    return False


# Function to control the robot via keyboard
def keyboard_control():
    
    # Initializing PyGame GUI
    pygame.init()
    
    # Creating a small GUI screen 
    screen = pygame.display.set_mode((300, 300))
    
    pygame.display.set_caption("Robot Control")
    
    print("[ARROWS] Move | [SPACE] Stop | [m] Mode | [SPEED UP] + | [SPEED DOWN] - | [ESC] Exit")

    running = True
    last_command = None
    
    # Default motor speed
    current_speed = 255

    # Looping for robot control until exit command
    while running:
        
        # Robot control architecture, via keyboard
        for event in pygame.event.get():
    
            if event.type == pygame.QUIT:
    
                running = False
    
            elif event.type == pygame.KEYDOWN:
    
                command = None

                # Forward movement
                if event.key == pygame.K_UP:
    
                    command = "f"
                
                # Backward movement
                elif event.key == pygame.K_DOWN:
    
                    command = "b"

                # Turn left movement
                elif event.key == pygame.K_LEFT:
    
                    command = "l"

                # Turn right movement
                elif event.key == pygame.K_RIGHT:
    
                    command = "r"

                # Stoping the robot
                elif event.key == pygame.K_SPACE:
    
                    command = "s"

                # Speed up by 5
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    
                    # Checking if it is less or equals to 250, to increase the speed
                    if current_speed <= 250:
                    
                        current_speed += 5
                    
                        command = f"speed{current_speed}"
                    
                    else:
                    
                        print("⚠️ Maximum speed reached!")

                # Speed down by 5
                elif event.key == pygame.K_MINUS:
                    
                    # Checking if it is more or equals to 5 to decrease the speed
                    if current_speed >= 5:
                    
                        current_speed -= 5
                    
                        command = f"speed{current_speed}"
                    
                    else:
                    
                        print("⚠️ Minimum speed reached!")
                    
                # Changing mode from remote to autonomous
                elif event.key == pygame.K_m:
                    
                    command = "m"

                # Exiting the process
                elif event.key == pygame.K_ESCAPE:
    
                    running = False
    
                    break
                
                # Sending commands to Arduino Uno via Bluetooth
                if command and command != last_command:
    
                    serialCon.write((command + "\n").encode())
    
                    print(f"Sent command: {command}")
    
                    last_command = command

    pygame.quit()
    print("Keyboard control exited.")


# Function to send data to Flask server
def send_data_to_server(data):
    
    try:
        
        response = requests.post(url, json=data)
    
        print("Server Response:", response.text)
    
    except Exception as e:
    
        print("Error sending data to server:", e)


# Function to read data from Arduino and save it to a CSV file
def read_and_save_to_csv():

    # Waiting for Flask server to start before sending data
    if not wait_for_server(url):
        
        print("❌ Flask server not responding in time. Exiting data logger.")
        
        return
    
    print("✅ Flask server is up. Starting data read loop.")

    while True:

        if serialCon.in_waiting > 0:

            dataStr = serialCon.readline().decode('utf-8').rstrip()

            print("Received data from Arduino:", dataStr)
            
            # Deserializing JSON string to Python dictionary
            try:
                
                dataDict = json.loads(dataStr)
            
            except json.JSONDecodeError:

                print("Invalid JSON format received from Arduino:", dataStr)
            
                continue
            
            # Checking if the received data dictionary contains all required keys
            if all(key in dataDict for key in ["Temperature", "Humidity", "Gas"]):
                
                temperature = float(dataDict["Temperature"])
                humidity = float(dataDict["Humidity"])
                gas = int(dataDict["Gas"])

                # Real-time anomaly detection
                inputScaled = scaler.transform([[temperature, humidity, gas]])
                
                prediction = model.predict(inputScaled)[0]
                
                anomalyStatus = 1 if prediction == -1 else 0

                if anomalyStatus == 1:
                
                    print("⚠️ Anomaly Detected (Smoke/Fire Possible)")
                
                else:
                
                    print("✅ Normal Reading")
                
                # Updating the latest data
                with dataLock:
                    
                    latestData.update({
                        
                        "Temperature": temperature,
                        
                        "Humidity": humidity,
                        
                        "Gas": gas,
                        
                        "Anomaly": anomalyStatus
                    })

                # Saving the data to the CSV file
                save_to_csv(temperature, humidity, gas, anomalyStatus)
                
                # Sending the data to the Flask server
                send_data_to_server(dataDict)
            
            else:
            
                print("Incomplete data received from Arduino:", dataDict)


# Function to save data to CSV file
def save_to_csv(temperature, humidity, gas, anomaly):
    
    fileExists = os.path.exists(csvFile)
    
    # Reading the last row, excluding timestamp
    if fileExists:
    
        try:
    
            with open(csvFile, 'r') as file:
    
                rows = list(csv.reader(file))
    
                if len(rows) > 1:
    
                    last_row = rows[-1]
    
                    if last_row[1:] == [str(temperature), str(humidity), str(gas), str(anomaly)]:
    
                        print("Duplicate entry detected — skipping data save.")
    
                        return
    
        except Exception as e:
    
            print(f"Error checking for duplicates: {e}")

    # Preparing timestamp and write data
    timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(csvFile, mode='a', newline='') as file:
    
        writer = csv.writer(file)
    
        if not fileExists:
    
            writer.writerow(["Timestamp", "Temperature", "Humidity", "Gas", "Anomaly"])
    
        writer.writerow([timeStamp, temperature, humidity, gas, anomaly])



@app.route('/receive_data', methods=['POST'])
def receive_data():

    if request.method == 'POST':

        if request.headers['Content-Type'] == 'application/json':

            data = request.json

            print("Received data from Arduino:", data)

            # Processing the data as needed
            return "Data received by server!"

        else:

            return "Unsupported Media Type", 415

    else:

        return "Method Not Allowed", 405

# Root server
@app.route("/")
def index():
    
    return "IoT UGV Flask Server Running"


@app.route('/receive_data', methods=['GET'])
def get_data():

    with dataLock:

        # Returning the most recent data from the Arduino (Temperature and Humidity)
        if latestData["Temperature"] is not None and latestData["Humidity"] is not None and latestData["Gas"] is not None:
        
            return latestData
        
        else:
        
            return {"message": "No data received from Arduino yet"}, 404


# Flask route to serve the CSV file
@app.route('/csv_data')
def serve_csv():

    # Checking if CSV file exists
    if os.path.exists(csvFile):
        
        with open(csvFile, 'r') as file:
        
            csv_content = file.read()
        
        return Response(csv_content, mimetype='text/csv')
    
    else:
    
        return "CSV file not found", 404


# Running the main program
if __name__ == "__main__":
   
    # Running Flask server in a separate thread
    serverThread = Thread(target=app.run, kwargs={'host':'0.0.0.0', 'port':5000, 'threaded': True})
    serverThread.start()

    # Starting reading data from Arduino and saving to the CSV file in a separate thread
    Thread(target=read_and_save_to_csv).start()

    # Starting the keyboard control thread
    Thread(target=keyboard_control).start()