# 1_data_simulator.py - Simulates Smart Home IoT Sensors (HEAVY USAGE EDITION)
import pandas as pd
import numpy as np
import datetime
import random

print("--- Step 1: Generating MASSIVE Smart Home Energy Data ---")

# We increased the power (Watts) to simulate heavy-duty appliances
APPLIANCES = {
    "Living_Room_AC": {"power": 2500, "type": "cooling"},  # Heavy 2-Ton AC
    "Bedroom_AC": {"power": 2000, "type": "cooling"},      # 1.5-Ton AC
    "Living_Room_Fan": {"power": 100, "type": "circulation"},
    "Kitchen_Lights": {"power": 150, "type": "lighting"},  # Multiple bright lights
    "TV": {"power": 300, "type": "entertainment"}          # Big screen TV
}

def generate_usage_data(days=30):
    data = []
    start_date = datetime.datetime.now().replace(minute=0, second=0, microsecond=0) - datetime.timedelta(days=days)
    print(f"Simulating {days} days of heavy energy usage data...")
    
    for day in range(days):
        for hour in range(24):
            current_time = start_date + datetime.timedelta(days=day, hours=hour)
            is_daytime = 8 <= hour <= 18
            is_evening = 18 < hour <= 23
            is_night = hour < 8
            
            # Hotter base temperatures to force AC usage
            outdoor_temp = random.uniform(28, 42) if is_daytime else random.uniform(24, 32)
            
            for appliance, details in APPLIANCES.items():
                status = 0
                
                # --- AGGRESSIVE USAGE LOGIC ---
                if "AC" in appliance:
                    if outdoor_temp > 28: 
                        # If it's hot, 90% chance the AC is ON (Day or Night)
                        status = np.random.choice([0, 1], p=[0.1, 0.9])
                    elif is_night and "Bedroom" in appliance:
                        # 80% chance bedroom AC is on at night regardless of temp
                        status = np.random.choice([0, 1], p=[0.2, 0.8])
                        
                elif "Fan" in appliance:
                    status = np.random.choice([0, 1], p=[0.2, 0.8]) # Fans almost always on
                    
                elif "Lights" in appliance:
                    if is_evening or is_night:
                        status = np.random.choice([0, 1], p=[0.05, 0.95])
                    else:
                        # Sometimes left on during the day by mistake (wasting power!)
                        status = np.random.choice([0, 1], p=[0.7, 0.3]) 
                        
                elif "TV" in appliance:
                    if is_evening or is_daytime:
                        status = np.random.choice([0, 1], p=[0.3, 0.7])

                # Calculate energy
                energy_consumed_kwh = 0
                if status == 1:
                    fluctuation = random.uniform(0.9, 1.1) 
                    energy_consumed_kwh = (details["power"] * fluctuation) / 1000.0

                data.append({
                    "Timestamp": current_time,
                    "Appliance": appliance,
                    "Type": details["type"],
                    "Status_ON_OFF": status,
                    "Energy_Consumed_kWh": round(energy_consumed_kwh, 3),
                    "Outdoor_Temp": round(outdoor_temp, 1)
                })

    df = pd.DataFrame(data)
    return df

dataset = generate_usage_data(days=30)
dataset.to_csv("smart_home_energy_data.csv", index=False)
print("Success! Heavy usage data saved. Ready for AI Training.")