# 3_optimization_logic.py - The Smart Home Decision Engine
import pandas as pd
import joblib
import datetime

print("--- Step 3: Smart Energy Optimization Logic ---")

# 1. Load the trained AI Brain
try:
    ai_model = joblib.load("energy_prediction_model.pkl")
    features = joblib.load("model_features.pkl")
    print("AI Model loaded successfully!\n")
except FileNotFoundError:
    print("ERROR: AI model files not found. Please run Step 2 first.")
    exit()

# 2. Simulate the "Current Environment" (Pretend it's 2 PM and nice weather)
current_hour = 14      # 14:00 = 2:00 PM
current_temp = 24.5    # 24.5°C outside (Cool weather)

print(f"[LIVE SENSORS] Time: {current_hour}:00 | Outdoor Temp: {current_temp}°C\n")

# List of appliances in our smart home
appliances = ["Living_Room_AC", "Bedroom_AC", "Living_Room_Fan", "Kitchen_Lights", "TV"]

# 3. Prepare the data for the AI to predict "Normal" usage
input_data = []
for app in appliances:
    row = {'Hour': current_hour, 'Outdoor_Temp': current_temp}
    # Tell the AI which appliance we are asking about using the encoded features
    for f in features:
        if f.startswith('Appliance_'):
            row[f] = 1 if f == f'Appliance_{app}' else 0
    input_data.append(row)

# Format data exactly how the AI expects it
df_current = pd.DataFrame(input_data)[features] 

# 4. Ask the AI: "What is the predicted energy usage if we do nothing?"
predicted_normal_usage = ai_model.predict(df_current)

total_normal_kwh = 0
total_optimized_kwh = 0

print("--- Optimization Engine Decisions ---")

# 5. Apply Smart Rules (The Decision Making)
for i, app in enumerate(appliances):
    normal_kwh = predicted_normal_usage[i]
    optimized_kwh = normal_kwh
    action = "Keep ON"
    reason = "User usually has this on, and conditions require it."

    # RULE 1: If it's cool outside (< 26°C), forcefully turn OFF ACs to save power
    if "AC" in app and current_temp < 26.0:
        action = "TURN OFF (Auto-Save)"
        reason = f"Weather is cool ({current_temp}°C). AC is wasting energy."
        optimized_kwh = 0.0

    # RULE 2: If it's daytime (8 AM to 5 PM), turn OFF lights (use natural sunlight)
    elif "Lights" in app and 8 <= current_hour <= 17:
        action = "TURN OFF (Auto-Save)"
        reason = "It is daytime. Using natural sunlight instead."
        optimized_kwh = 0.0

    # RULE 3: If the AI predicts the user normally has it off anyway (close to 0 usage)
    if normal_kwh < 0.05:
        action = "Leave OFF"
        reason = "AI predicts user does not need this right now."
        optimized_kwh = 0.0

    # Print the decision for each device
    print(f"Device: {app}")
    print(f"  - AI Predicted Usage: {normal_kwh:.3f} kWh")
    print(f"  - System Action:      {action} -> {reason}")
    print(f"  - Optimized Usage:    {optimized_kwh:.3f} kWh\n")

    total_normal_kwh += normal_kwh
    total_optimized_kwh += optimized_kwh

# 6. Calculate and display the final savings
savings = total_normal_kwh - total_optimized_kwh

print("--- Final Energy Report for this Hour ---")
print(f"Predicted Total Usage (No AI):  {total_normal_kwh:.3f} kWh")
print(f"Optimized Total Usage (With AI): {total_optimized_kwh:.3f} kWh")
print(f"Total Energy Saved:              {savings:.3f} kWh")
print("-----------------------------------------")
print("\n--- Phase 3 Complete ---")