# Importing necessary libraries 
import warnings
import pandas as pd
import seaborn as sb
from joblib import dump
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay


# Ignoring warnings
warnings.filterwarnings('ignore')

# Loading dataset
dataset = pd.read_csv('sensorData.csv')

# Removing spaces
dataset.columns = dataset.columns.str.strip()

# Dropping timestamp if present
if 'Timestamp' in dataset.columns:
    
    dataset.drop(columns=['Timestamp'], inplace=True)

# Dropping duplicates and filling missing values
dataset.drop_duplicates(inplace=True)
dataset.fillna(dataset.select_dtypes(include='number').mean(), inplace=True)

# Selecting relevant features
X = dataset[['Temperature', 'Humidity', 'Gas']]

# Target variable (Anomaly column)
y = dataset['Anomaly']

# Normalizing features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    
    X_scaled,
    y,
    test_size=0.25, 
    random_state=42,
    stratify=y
)

# Random Forest Classifier model
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')

# Training model
model.fit(X_train, y_train)

# Saving model and scaler
dump(model, 'randomForest_Model.joblib')
dump(scaler, 'randomForest_Scaler.joblib')

# Evaluation
y_pred = model.predict(X_test)

print("\n--- Evaluation Report (Random Forest) ---")

print(classification_report(y_test, y_pred, target_names=["Normal", "Anomaly"]))

print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Confusion Matrix Plot
disp = ConfusionMatrixDisplay.from_estimator(
                                             
    model,
    X_test,
    y_test,
    display_labels=["Normal", "Anomaly"],
    cmap="coolwarm"
)

plt.title("Random Forest Confusion Matrix")
plt.tight_layout()
plt.show()

# Feature importance plot
importances = model.feature_importances_
features = ['Temperature', 'Humidity', 'Gas']

plt.figure(figsize=(6, 4))
sb.barplot(x=importances, y=features)
plt.title("Feature Importance (Random Forest)")
plt.tight_layout()
plt.show()


# Function to detect anomaly for new input
def detect_anomaly_rf(temperature, humidity, gas):
    
    input_scaled = scaler.transform([[temperature, humidity, gas]])
    
    prediction = model.predict(input_scaled)[0]
    
    proba = model.predict_proba(input_scaled)[0][1]  # probability of anomaly

    label = "Anomaly Detected (Smoke/Fire Possible)" if prediction == 1 else "Normal"

    return f"{label} | Anomaly Probability: {proba:.4f}"


# Example predictions
print("\nExample Prediction 1:")
print(detect_anomaly_rf(25.0, 60.0, 100))  # likely normal

print("\nExample Prediction 2:")
print(detect_anomaly_rf(40.0, 20.0, 350))  # likely anomaly