# 2_ml_prediction_model.py - The AI / Machine Learning Engine
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

print("--- Step 2: Training the AI Machine Learning Model ---")

# 1. Load the data we generated in Phase 1
data_file = "smart_home_energy_data.csv"
try:
    df = pd.read_csv(data_file)
    print(f"Successfully loaded {len(df)} records from {data_file}.")
except FileNotFoundError:
    print(f"ERROR: Could not find {data_file}. Please run 1_data_simulator.py first.")
    exit()

# 2. Data Preprocessing (Preparing data for the AI)
print("Processing data for AI...")
# Convert Timestamp to a usable number (Hour of the day)
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Hour'] = df['Timestamp'].dt.hour

# The AI only understands numbers, not words like "Living_Room_AC".
# We use 'One-Hot Encoding' to turn the Appliance names into numbers.
df_encoded = pd.get_dummies(df, columns=['Appliance'], drop_first=False)

# Define our Features (X) - What the AI looks at to make a prediction
# We look at: Hour of day, Outdoor Temp, and which Appliance it is.
features = ['Hour', 'Outdoor_Temp'] + [col for col in df_encoded.columns if 'Appliance_' in col]
X = df_encoded[features]

# Define our Target (y) - What the AI is trying to predict
y = df_encoded['Energy_Consumed_kWh']

# 3. Split the data into Training Data (80%) and Testing Data (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training AI on {len(X_train)} records, and testing on {len(X_test)} records...")

# 4. Build and Train the AI Model
# We use a Random Forest Regressor because it is excellent at finding complex patterns in data
ai_model = RandomForestRegressor(n_estimators=100, random_state=42)

print("Training the Random Forest model (this might take a few seconds)...")
ai_model.fit(X_train, y_train)

# 5. Evaluate how smart the AI is
predictions = ai_model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("\n--- AI Performance Report ---")
print(f"Mean Absolute Error (MAE): {mae:.4f} kWh (Lower is better)")
print(f"Accuracy Score (R-squared): {r2:.4f} (Closer to 1.0 is better)")

# 6. Save the trained AI model to a file
# This is crucial so our Dashboard can use the AI without retraining it every time!
model_filename = "energy_prediction_model.pkl"
joblib.dump(ai_model, model_filename)

# Also save the list of feature names so our dashboard knows exactly what inputs to provide
joblib.dump(features, "model_features.pkl")

print(f"\nSuccess! The trained AI Brain has been saved as '{model_filename}'.")
print("--- Phase 2 Complete ---")
