// Importing the required libraries 
#include <dht11.h>
#include <ArduinoJson.h>


// Motor Driver Pins
int motor1pin1 = 2;  // Left Motors Forward
int motor1pin2 = 3;  // Left Motors Backward
int motor2pin1 = 4;  // Right Motors Forward
int motor2pin2 = 5;  // Right Motors Backward
int ENA = 9;         // Speed control for Left Motors
int ENB = 10;        // Speed control for Right Motors

// Ultrasonic Sensor Pins
int trigPin = 8;
int echoPin = 7;

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
  
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}


void loop() {

  // counting the current millis
  unsigned long currentMillis = millis();
  
  // Measuring distance using ultrasonic sensor
  int distance = measureDistance();

  // Printing distance for debugging
  Serial.print("Distance: ");
  Serial.println(distance);

  // Checking if there is an obstacle within the threshold distance
  if (distance < distanceThreshold) {
    
    Serial.println("Obstacle detected!");
    
    stopMotors();
    delay(700);

    moveBackward();
    delay(700);

    randomTurn();
    delay(200);
  }
  
  else {
    
    moveForward();
  }

  // Gathering Sensor Data
  StaticJsonDocument<200> doc;
  
  // Reading sensors every 5 seconds
  if (currentMillis - lastDHT11Read >= DHT11_FREQUENCY) {
    
    lastDHT11Read = currentMillis;

    // DHT11 Data
    int dhtData = DHT11.read(DHT11_PIN);
    
    doc["Temperature"] = (float)DHT11.temperature;
    doc["Humidity"] = (float)DHT11.humidity;
    
    // Temperature, Humidity and Gas Sensor Data
    float tempValue = (float)DHT11.temperature ;
    float humValue = (float)DHT11.humidity ; 
    int gasValue = readSensor();

    if (gasValue >= 300 && tempValue >= 50.0 && humValue <= 40.0)  {

      Serial.println("Danger of Fire outbreak!");
    }
    
    // Sending the data over the serial port
    sendSerialData(doc);
  }
  
  // Waiting for 2 seconds before reading again
    delay(2000);
}


// Function to measure distance using ultrasonic sensor
int measureDistance() {
  
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  
  int distance = duration * 0.034 / 2;
  
  return distance;
}


// Function to move forward
void moveForward() {

  analogWrite(ENA, 200);
  analogWrite(ENB, 200);

  digitalWrite(motor1pin1, LOW);
  digitalWrite(motor1pin2, HIGH);

  digitalWrite(motor2pin1, LOW);
  digitalWrite(motor2pin2, HIGH);
}


// Function to move forward
void moveBackward() {

  analogWrite(ENA, 200);
  analogWrite(ENB, 200);

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


// Function to randomly turn left or right
void randomTurn() {

  // 0 = left, 1 = right
  int randomTurnDirection = random(0, 2); 
  
  if (randomTurnDirection == 0) {

    turnLeft();
  }
  
  else {
  
    turnRight();
  }
}


void turnLeft() {

  analogWrite(ENA, 150);  // Power to left motors
  analogWrite(ENB, 0);    // Stop right motors
  
  digitalWrite(motor1pin1, LOW);  // Left motor reverse (moving backward)
  digitalWrite(motor1pin2, HIGH);
  
  digitalWrite(motor2pin1, LOW);   // Right motor stop
  digitalWrite(motor2pin2, LOW);
}


// Function to turn right (stop left motors, move right motors in reverse direction)
void turnRight() {
  
  analogWrite(ENA, 0);    // Stop left motors
  analogWrite(ENB, 150);  // Power to right motors
  
  digitalWrite(motor1pin1, LOW);   // Left motor stop
  digitalWrite(motor1pin2, LOW);
  
  digitalWrite(motor2pin1, LOW);  // Right motor reverse (moving backward)
  digitalWrite(motor2pin2, HIGH);
}


// Function to read and return analog sensor data (gas sensor)
int readSensor() {

  unsigned int sensorValue = analogRead(GAS_PIN);

  return map(sensorValue, 0, 1023, 0, 255);
}


// Function to send the data over Serial
void sendSerialData(StaticJsonDocument<200>& doc) {

  String jsonString;

  serializeJson(doc, jsonString);
  Serial.println(jsonString);  // Sending JSON string over USB serial
}
