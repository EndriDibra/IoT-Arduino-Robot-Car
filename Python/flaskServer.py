# Importing the required libraries 
import serial
import requests
from flask import Flask, request, Response
from threading import Thread
import os
import csv
import json
from datetime import datetime


app = Flask(__name__)

# Openning serial connection to Arduino
ser = serial.Serial('COM5', 9600) 

# URL of the Flask server
url = 'http://127.0.0.1:5000/receive_data'

# Defining the path to the CSV file
csv_file = 'Rainfall.csv'

# Variable to store the latest temperature and humidity values
latest_data = {"Temperature": None, "Humidity": None}


# Function to send data to Flask server
def send_data_to_server(data):
    
    try:
        response = requests.post(url, json=data)
    
        print("Server Response:", response.text)
    
    except Exception as e:
    
        print("Error sending data to server:", e)


# Function to read data from Arduino and save it to a CSV file
def read_and_save_to_csv():

    while True:

        if ser.in_waiting > 0:

            data_str = ser.readline().decode('utf-8').rstrip()

            print("Received data from Arduino:", data_str)
            
            # Deserializing JSON string to Python dictionary
            try:
                
                data_dict = json.loads(data_str)
            
            except json.JSONDecodeError:

                print("Invalid JSON format received from Arduino:", data_str)
            
                continue
            
            # Checking if the received data dictionary contains all required keys
            if all(key in data_dict for key in ["Temperature", "Humidity"]):
                
                temperature = float(data_dict["Temperature"])
                humidity = float(data_dict["Humidity"])
                
                # Storing the latest data
                latest_data["Temperature"] = temperature
                latest_data["Humidity"] = humidity
                
                # Saving the data to the CSV file
                save_to_csv(temperature, humidity)
                
                # Sending the data to the Flask server
                send_data_to_server(data_dict)
            
            else:
            
                print("Incomplete data received from Arduino:", data_dict)


# Function to save data to CSV file
def save_to_csv(temperature, humidity):

    # Checking if CSV file exists, if not, create it and write headers
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, mode='a', newline='') as file:
   
        writer = csv.writer(file)
        
        # Writing headers if the file is empty
        if not file_exists:
            
            writer.writerow(["Timestamp", "Temperature", "Humidity"])
        
        # Writing the current data with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        writer.writerow([timestamp, temperature, humidity])


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


@app.route('/receive_data', methods=['GET'])
def get_data():

    # Returning the most recent data from the Arduino (Temperature and Humidity)
    if latest_data["Temperature"] is not None and latest_data["Humidity"] is not None:
      
        return latest_data
    
    else:
    
        return {"message": "No data received from Arduino yet"}, 404


# Flask route to serve the CSV file
@app.route('/csv_data')
def serve_csv():

    # Checking if CSV file exists
    if os.path.exists(csv_file):
        
        with open(csv_file, 'r') as file:
        
            csv_content = file.read()
        
        return Response(csv_content, mimetype='text/csv')
    
    else:
    
        return "CSV file not found", 404


# Running the main program
if __name__ == "__main__":
   
    # Running Flask server in a separate thread
    server_thread = Thread(target=app.run, kwargs={'host':'0.0.0.0', 'port':5000})
    server_thread.start()

    # Starting reading data from Arduino and saving to the CSV file
    read_and_save_to_csv()