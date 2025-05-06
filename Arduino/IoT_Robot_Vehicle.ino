// Importing the required libraries 
#include <dht11.h>
#include <ArduinoJson.h>


// Motor Driver Pins
int motor1pin1 = 2;  // Left Motors Forward
int motor1pin2 = 3;  // Left Motors Backward
int motor2pin1 = 4;  // Right Motors Forward
int motor2pin2 = 5;  // Right Motors Backward
int ENA = 6;         // Speed control for Left Motors
int ENB = 7;        // Speed control for Right Motors

// Ultrasonic Sensor Pins
int trigPin = 9;
int echoPin = 8;

// DHT11 Sensor Pin
#define DHT11_PIN 11
dht11 DHT11;

// Gas Sensor Pin
#define GAS_PIN A0

// Distance threshold for obstacle avoidance
int distanceThreshold = 20;

// DHT11 sensor reading frequency(every 5 seconds)
const long DHT11_FREQUENCY = 5000;

// last reading from the DHT11 sensor
unsigned long lastDHT11Read = 0;

// Robot mode selection: remote or autonomous
// Default mode: "remote"
String mode = "remote";


// setup function, for initialization purposes
void setup() {
  
  // Initializing Serial Monitor
  Serial.begin(9600);

  // Motor Pins Setup
  pinMode(motor1pin1, OUTPUT);
  pinMode(motor1pin2, OUTPUT);
  
  pinMode(motor2pin1, OUTPUT);
  pinMode(motor2pin2, OUTPUT);
  
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  
  // Ultrasonic Pins setup
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  Serial.println("Bluetooth connection Ready! Send 'm' for mode, to change between remote and automomous mode.");
}


// loop function, for the actual running process
void loop() {

  // Counting the current millis
  unsigned long currentMillis = millis();

  // Checking for Bluetooth input
  if (Serial.available()) {
      
      String command = Serial.readStringUntil('\n');
      command.trim();
      
      // Mode switching logic
      if (command == "m") {
          
          mode = (mode == "autonomous") ? "remote" : "autonomous";
          
          Serial.print("Mode changed to: ");
          Serial.println(mode);
          
          // Exit to prevent accidental execution of other commands
          return; 
      }

      // If in remote control mode, processing movement commands
      if (mode == "remote") {
          
          controlRobot(command);
      }

      delay(20);
  }

      // If in autonomous mode, run obstacle avoidance function 
      if (mode == "autonomous") {
          
          autonomousMode();
      }

    // Sending sensor data via Bluetooth every 5 seconds
    if (currentMillis - lastDHT11Read >= DHT11_FREQUENCY) {
        
        lastDHT11Read = currentMillis;
        
        sendSensorData();
    }
}


// Function to control robot remotely
void controlRobot(String command) {

    // Sending the data
    sendSensorData();
    
    Serial.print("Command received: ");
    Serial.println(command);

    command.toLowerCase(); 

    if (command == "f" || command == "forward") {
      
      moveForward();
    }
    
    else if (command == "b" || command == "backward") {
      
      moveBackward();
    }

    else if (command == "l" || command == "left") { 
      
      turnLeft();
    }
    
    else if (command == "r" || command == "right") { 
      
      turnRight();
    }

    else if (command == "s" || command == "stop"){
      
      stopMotors();
    }

    else {
      
      Serial.println("Invalid command! Try again.");
    }  
}


// Function to control the robot autonomously
void autonomousMode() {

    // Sending the data
    sendSensorData();
    
    // Taking the distance between the robot and the obstacle
    int distance = measureDistance();
    
    Serial.print("Distance: ");
    Serial.println(distance);

    // Checking if the distance is less than the safe range
    // If it is, then the robot will stop, move backward and then turn on the right side  
    if (distance < distanceThreshold) {
    
        Serial.println("Obstacle detected!");
    
        stopMotors();
        delay(700);
    
        moveBackward();
        delay(700);
    
        turnRight();
        delay(700);
    }
    
    // if no obstacles are detected, then the robot will continue to move forward
    else {
    
        moveForward();
    }
}


// Function to send sensor data via Bluetooth
void sendSensorData() {
    
    StaticJsonDocument<200> doc;

    int dhtData = DHT11.read(DHT11_PIN);
    
    // Taking temperature data
    float tempValue = (float)DHT11.temperature;

     // Taking humidity data
    float humValue = (float)DHT11.humidity;

     // Taking gas data
    int gasValue = readGasSensor();
    
    doc["Temperature"] = tempValue;
    doc["Humidity"] = humValue;
    doc["Gas"] = gasValue;

    String jsonString;
    serializeJson(doc, jsonString);

    // Sending JSON via Bluetooth
    Serial.println(jsonString);
}


// Function to read and return analog sensor data (gas sensor)
int readGasSensor() {

  // Taking the gas data
  unsigned int sensorValue = analogRead(GAS_PIN);

  return sensorValue;
}


// Function that measures the distance between the robot and the obstacle
int measureDistance() {
    
    // Ensuring the trigger pin is low before starting
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    
    // Sending a 10-microsecond pulse to trigger the sensor
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    
    digitalWrite(trigPin, LOW);

    // Listening for the echo and setting a timeout of 30ms (30000 µs)
    long duration = pulseIn(echoPin, HIGH, 30000); 

    // If timeout occurs, return a very high value (no obstacle detected)
    if (duration == 0) {
    
        Serial.println("Ultrasonic Sensor Timeout: No echo received");
    
        return 999;
    }

    // Calculating distance (speed of sound = 0.034 cm/µs)
    int distance = duration * 0.034 / 2;

    // Capping distance to 400 cm to avoid unrealistic values
    return (distance > 400) ? 400 : distance;
}


// Function to move forward
void moveForward() {

  analogWrite(ENA, 255);
  analogWrite(ENB, 255);

  digitalWrite(motor1pin1, LOW);
  digitalWrite(motor1pin2, HIGH);

  digitalWrite(motor2pin1, LOW);
  digitalWrite(motor2pin2, HIGH);
}


// Function to move backward
void moveBackward() {

  analogWrite(ENA, 255);
  analogWrite(ENB, 255);

  digitalWrite(motor1pin1, HIGH);
  digitalWrite(motor1pin2, LOW);

  digitalWrite(motor2pin1, HIGH);
  digitalWrite(motor2pin2, LOW);
}


// Function to stop motors
void stopMotors() {

  analogWrite(ENA, 0);
  analogWrite(ENB, 0);

  digitalWrite(motor1pin1, LOW);
  digitalWrite(motor1pin2, LOW);

  digitalWrite(motor2pin1, LOW);
  digitalWrite(motor2pin2, LOW);
}


// Function to turn left
void turnLeft() {
  
  analogWrite(ENA, 255);  
  analogWrite(ENB, 255);    

  digitalWrite(motor1pin1, HIGH);   // Left motors move backward
  digitalWrite(motor1pin2, LOW);

  digitalWrite(motor2pin1, LOW);    // Right motors move forward
  digitalWrite(motor2pin2, HIGH);
}


// Function to turn right
void turnRight() {
  
  analogWrite(ENA, 255);  
  analogWrite(ENB, 255);    

  digitalWrite(motor1pin1, LOW);    // Left motors move forward
  digitalWrite(motor1pin2, HIGH);

  digitalWrite(motor2pin1, HIGH);   // Right motors move backward
  digitalWrite(motor2pin2, LOW);
}
