# Importing the required libraries 
import warnings
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import metrics
from sklearn.metrics import ConfusionMatrixDisplay
from imblearn.over_sampling import RandomOverSampler


# Ignoring warnings
warnings.filterwarnings('ignore')


# Loading the rainfall dataset
dataset = pd.read_csv('Rainfall.csv')

# Displaying dataset sample and info
print("Dataset Sample:\n", dataset.head())
print("\nDataset Shape:", dataset.shape)
print("\nMissing values:\n", dataset.isnull().sum())

# Dropping the 'Timestamp' column (not needed for prediction)
dataset.drop(columns=['Timestamp'], inplace=True)

# Filling missing values only in numeric columns
dataset.fillna(dataset.select_dtypes(include=['number']).mean(), inplace=True)

# Displaying dataset info after cleaning
print("\nDataset after cleaning:\n", dataset.head())

# Visualizing the distribution of humidity and temperature
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
sb.histplot(dataset['Temperature'], bins=10, kde=True)
plt.title("Temperature Distribution")

plt.subplot(1,2,2)
sb.histplot(dataset['Humidity'], bins=10, kde=True)
plt.title("Humidity Distribution")
plt.show()

# Defining target variable (Rainfall) based on a humidity threshold
# Assuming rainfall occurs when humidity > 75%
dataset['Rainfall'] = (dataset['Humidity'] > 75).astype(int)

# Displaying target variable distribution
plt.pie(dataset['Rainfall'].value_counts(), labels=['No Rain', 'Rain'], autopct='%1.1f%%')
plt.title("Rainfall Distribution")
plt.show()

# Splitting features (X) and target (Y)
X = dataset[['Temperature', 'Humidity']]
Y = dataset['Rainfall']

# Splitting into training and validation sets
X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=0.2, stratify=Y, random_state=2)

# Balancing the dataset using oversampling
balanced_data = RandomOverSampler(sampling_strategy='minority', random_state=22)
X_train_balanced, Y_train_balanced = balanced_data.fit_resample(X_train, Y_train)

# Normalizing the features
scaler = StandardScaler()
X_train_balanced = scaler.fit_transform(X_train_balanced)
X_val = scaler.transform(X_val)

# Defining machine learning models
models = [
    
    XGBClassifier(),
    LogisticRegression(),
    SVC(kernel='rbf', probability=True),
    DecisionTreeClassifier(random_state=42)
]

# Training and evaluating models
for model in models:
    
    model.fit(X_train_balanced, Y_train_balanced)
    
    train_preds = model.predict_proba(X_train_balanced)[:,1]
    
    val_preds = model.predict_proba(X_val)[:,1]

    print(f'Model: {model.__class__.__name__}')
    print('Training Accuracy:', metrics.roc_auc_score(Y_train_balanced, train_preds))
    print('Validation Accuracy:', metrics.roc_auc_score(Y_val, val_preds))
    print()

# Confusion matrix for Logistic Regression (best performing model)
ConfusionMatrixDisplay.from_estimator(models[1], X_val, Y_val)
plt.show()

# Classification report for Logistic Regression
print("\nClassification Report:\n", metrics.classification_report(Y_val, models[1].predict(X_val)))

# Function to predict likelihood of rainfall based on Temperature & Humidity
def predict_rainfall(temperature, humidity):
    
    input_features = scaler.transform([[temperature, humidity]])
    
    # Logistic Regression Model
    prediction = models[1].predict(input_features)[0]
    
    return "Yes" if prediction == 1 else "No"

# Examples prediction
temperature = 19.0
humidity = 54.0
print(f"\nWill it rain if Temperature = {temperature}°C & Humidity = {humidity}%? → {predict_rainfall(temperature, humidity)}")

temperature = 19.0
humidity = 84.0
print(f"\nWill it rain if Temperature = {temperature}°C & Humidity = {humidity}%? → {predict_rainfall(temperature, humidity)}")