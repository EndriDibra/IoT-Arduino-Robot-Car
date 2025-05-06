# Importing the required libraries 
import warnings
import pandas as pd
import seaborn as sb
from joblib import dump
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# Ignoring warnings
warnings.filterwarnings('ignore')

# Loading the sensor dataset
dataset = pd.read_csv('sensorData.csv')

# Dropping irrelevant columns
if 'Timestamp' in dataset.columns:

    dataset.drop(columns=['Timestamp'], inplace=True)

# Removing duplicate rows, if any
dataset.drop_duplicates(inplace=True)

# Displaying dataset sample and info
print("Dataset Sample:\n", dataset.head())
print("\nDataset Shape:", dataset.shape)
print("\nMissing values:\n", dataset.isnull().sum())

# Filling missing values only in numeric columns
dataset.fillna(dataset.select_dtypes(include=['number']).mean(), inplace=True)

# Displaying cleaned dataset
print("\nDataset after cleaning process:\n", dataset.head())

# Visualizing the distribution of Temperature, Humidity, and Gas
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
sb.histplot(dataset['Temperature'], bins=10, kde=True)
plt.title("Temperature Distribution")

plt.subplot(1, 3, 2)
sb.histplot(dataset['Humidity'], bins=10, kde=True)
plt.title("Humidity Distribution")

plt.subplot(1, 3, 3)
sb.histplot(dataset['Gas'], bins=10, kde=True)
plt.title("Gas Sensor Distribution")

plt.tight_layout()
plt.show()

# Selecting relevant features
X = dataset[['Temperature', 'Humidity', 'Gas']]

# Normalizing the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Fitting the Isolation Forest model, "Unsupervised Learning"
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X_scaled)

# Saving the trained model and scaler for use in the server
dump(model, 'model.joblib')
dump(scaler, 'scaler.joblib')

# Predicting anomalies: -1 = anomaly, 1 = normal
dataset['Anomaly'] = model.predict(X_scaled)

# Displaying detected anomalies
anomalies = dataset[dataset['Anomaly'] == -1]

print(f"\nTotal Anomalies Detected: {len(anomalies)}")
print(anomalies)

# A plot of Temperature vs. Gas with anomaly markers
plt.figure(figsize=(8, 6))
sb.scatterplot(data=dataset, x='Temperature', y='Gas', hue='Anomaly', palette={1: 'green', -1: 'red'})
plt.title("Anomaly Detection: Temperature vs. Gas")
plt.show()


# Function to detect anomaly for new input
def detect_anomaly(temperature, humidity, gas):

    input_scaled = scaler.transform([[temperature, humidity, gas]])
    
    prediction = model.predict(input_scaled)[0]

    return "Anomaly Detected (Smoke/Fire Possible)" if prediction == -1 else "Normal"


# Example predictions
print("\nExample Prediction 1:")
print(detect_anomaly(25.0, 60.0, 100))  # likely normal

print("\nExample Prediction 2:")
print(detect_anomaly(40.0, 40.0, 350))  # possibly fire/smoke