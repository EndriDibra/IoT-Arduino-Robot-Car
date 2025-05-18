// Importing the required libraries 
#include <dht11.h>
#include <ArduinoJson.h>


// Left side motors (2 motors in parallel) via L298N Channel A
int motor1pin1 = 2;  // IN1 - Left motors backward
int motor1pin2 = 3;  // IN2 - Left motors forward
int ENA = 6;         // ENA - Speed control for left motors (PWM)

// Right side motors (2 motors in parallel) via L298N Channel B
int motor2pin1 = 4;  // IN3 - Right motors backward
int motor2pin2 = 5;  // IN4 - Right motors forward
int ENB = 10;         // ENB - Speed control for right motors (PWM)

// Default full speed, range: 0–255
int motorSpeed = 255;

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

  Serial.println("Bluetooth connection Ready! Send 'm' for mode, to change between remote and autonomous mode.");

  // For safety, all motors are stopped on startup
  stopMotors();  
}


// loop function, for the actual running process
void loop() {

  // Counting the current millis
  unsigned long currentMillis = millis();

  // Checking for Bluetooth input
  if (Serial.available()) {
      
      String command = Serial.readStringUntil('\n');
      command.trim();
      
      // Speed control: command starts with "speed"
      // and followed by a number, e.g. "speed150"
      // this sets speed to 150 from the default value 255
      if (command.startsWith("speed")) {
          
          // Extracting number after "speed"
          int newSpeed = command.substring(5).toInt();

          // Checking if speed is on the correct range
          if (newSpeed >= 0 && newSpeed <= 255) {
              
              // Setting speed to a new value
              motorSpeed = newSpeed;

              Serial.print("Speed set to: ");
              Serial.println(motorSpeed);
          }

          else if (motorSpeed > 0 && motorSpeed < 80) {
              
              Serial.println("⚠️ Warning: Low speed may cause motors to stall.");
          }
          
          // Incorrect value for speed 
          else {
          
              Serial.println("Invalid speed! Must be between 0 and 255.");
          }
          
          return;
      }


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
    
    // Data in JSON format
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

  analogWrite(ENA, motorSpeed);
  analogWrite(ENB, motorSpeed);

  digitalWrite(motor1pin1, LOW);
  digitalWrite(motor1pin2, HIGH);

  digitalWrite(motor2pin1, LOW);
  digitalWrite(motor2pin2, HIGH);
}


// Function to move backward
void moveBackward() {

  analogWrite(ENA, motorSpeed);
  analogWrite(ENB, motorSpeed);

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
  
  analogWrite(ENA, motorSpeed);  
  analogWrite(ENB, motorSpeed);    

  digitalWrite(motor1pin1, HIGH);   // Left motors move backward
  digitalWrite(motor1pin2, LOW);

  digitalWrite(motor2pin1, LOW);    // Right motors move forward
  digitalWrite(motor2pin2, HIGH);
}


// Function to turn right
void turnRight() {
  
  analogWrite(ENA, motorSpeed);  
  analogWrite(ENB, motorSpeed);    

  digitalWrite(motor1pin1, LOW);    // Left motors move forward
  digitalWrite(motor1pin2, HIGH);

  digitalWrite(motor2pin1, HIGH);   // Right motors move backward
  digitalWrite(motor2pin2, LOW);
}
