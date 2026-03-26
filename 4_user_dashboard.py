# 4_user_dashboard.py - The Interactive Web Dashboard (SCI-FI FONTS & VIDEO FIX)
import streamlit as st
import pandas as pd
import joblib
import requests
import base64
import os
from datetime import datetime, time, timezone, timedelta

# 1. Setup the Web Page & Timezone (IST)
st.set_page_config(page_title="Smart Home AI", page_icon="⚡", layout="wide")
IST = timezone(timedelta(hours=5, minutes=30))

# --- THE MAGIC BACKGROUND & FONT FUNCTION ---
def set_dynamic_background(hour):
    if 6 <= hour < 17:
        video_file = "morning.mp4"
    elif 17 <= hour < 19:
        video_file = "afternoon.mp4"
    else:
        video_file = "night.mp4"
        
    if os.path.exists(video_file):
        with open(video_file, 'rb') as f:
            video_bytes = f.read()
        b64 = base64.b64encode(video_bytes).decode()
        
        # Inject custom HTML/CSS for Videos AND Futuristic Fonts!
        st.markdown(f"""
            <style>
            /* 1. Import futuristic fonts from Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Rajdhani:wght@500;600;700&display=swap');

            /* 2. Apply Rajdhani to all standard text */
            html, body, [class*="st-"] {{
                font-family: 'Rajdhani', sans-serif !important;
                font-size: 1.1rem;
            }}

            /* 3. Apply Orbitron to all Headers and Titles for that Sci-Fi look */
            h1, h2, h3, .stMetric label {{
                font-family: 'Orbitron', sans-serif !important;
                letter-spacing: 1px;
            }}

            /* 4. Make the metric numbers huge, bold, and glowing Neon Cyan */
            [data-testid="stMetricValue"] {{
                font-family: 'Orbitron', sans-serif !important;
                font-size: 2.5rem !important;
                color: #00E5FF !important; 
                text-shadow: 0px 0px 10px rgba(0, 229, 255, 0.5); 
            }}

            /* 5. Keep the transparent video background */
            .stApp {{
                background-color: transparent !important;
            }}
            .my-bg-video {{
                position: fixed;
                right: 0;
                bottom: 0;
                min-width: 100%;
                min-height: 100%;
                z-index: -1;
                opacity: 0.35; 
                object-fit: cover;
            }}

            /* 6. Glowing glass-morphism panels for data */
            .stMetric, .stDataFrame {{
                background-color: rgba(15, 20, 25, 0.75);
                padding: 15px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0, 229, 255, 0.15);
                border: 1px solid rgba(0, 229, 255, 0.2);
            }}
            </style>
            <video autoplay muted loop playsinline class="my-bg-video" id="vid-{hour}" src="data:video/mp4;base64,{b64}"></video>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.error(f"⚠️ Missing background video: {video_file}")
# -----------------------------------

st.title("⚡ Smart Home Energy Optimization")
st.write("Welcome to your AI-powered home energy manager.")

# 2. Load the AI Model securely
@st.cache_resource
def load_model():
    try:
        model = joblib.load("energy_prediction_model.pkl")
        features = joblib.load("model_features.pkl")
        return model, features
    except Exception as e:
        return None, None

ai_model, features = load_model()

if ai_model is None:
    st.error("⚠️ AI Model not found! Please run Phase 2 first.")
    st.stop()

# --- Function to get live weather ---
@st.cache_data(ttl=900)
def get_live_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=17.3850&longitude=78.4867&current_weather=true"
        response = requests.get(url)
        data = response.json()
        return float(data['current_weather']['temperature'])
    except:
        return 30.0

# 3. Sidebar: Control Mode & Financials
st.sidebar.header("🎛️ System Control Mode")
app_mode = st.sidebar.radio("Select Operating Mode:", ("🟢 Auto Mode (Live Sensors)", "🔴 Demo Mode (Manual Sliders)"))

st.sidebar.divider()
st.sidebar.header("💰 Financial Settings")
elec_rate = st.sidebar.number_input("Electricity Rate (₹ per kWh)", value=8.50, step=0.50)

st.sidebar.divider()
st.sidebar.header("🌡️ Environment Data")

if app_mode == "🟢 Auto Mode (Live Sensors)":
    now_ist = datetime.now(IST)
    current_hour = now_ist.hour
    display_time = now_ist.strftime("%I:%M %p") 
    current_temp = get_live_weather()
    
    st.sidebar.success(f"**🕒 Live Time (IST):** {display_time}")
    st.sidebar.success(f"**🌤️ Live Temp:** {current_temp} °C")
else:
    st.sidebar.warning("Manual Override Active")
    selected_time = st.sidebar.slider(
        "Set Time", 
        min_value=time(0, 0), 
        max_value=time(23, 0), 
        value=time(14, 0), 
        format="hh:mm a"
    )
    current_hour = selected_time.hour
    current_temp = st.sidebar.slider("Set Outdoor Temperature (°C)", 10.0, 45.0, 24.5, 0.5)

# Trigger Background Video & Fonts
set_dynamic_background(current_hour)

# 4. Prepare data for the AI
appliances = ["Living_Room_AC", "Bedroom_AC", "Living_Room_Fan", "Kitchen_Lights", "TV"]
input_data = []

for app in appliances:
    row = {'Hour': current_hour, 'Outdoor_Temp': current_temp}
    for f in features:
        if f.startswith('Appliance_'):
            row[f] = 1 if f == f'Appliance_{app}' else 0
    input_data.append(row)

df_current = pd.DataFrame(input_data)[features]

# 5. Get AI Predictions
predictions = ai_model.predict(df_current)

# 6. Apply Optimization Rules & Calculate Savings
total_normal_kwh = 0.0
total_optimized_kwh = 0.0
appliance_results = []

for i, app in enumerate(appliances):
    normal_kwh = predictions[i]
    optimized_kwh = normal_kwh
    action = "Keep ON"
    status_icon = "🟢 ON"

    if "AC" in app and current_temp < 26.0:
        action = "TURN OFF (Auto-Save: Cool Weather)"
        optimized_kwh = 0.0
        status_icon = "🔴 OFF"
    elif "Lights" in app and 8 <= current_hour <= 17:
        action = "TURN OFF (Auto-Save: Daytime)"
        optimized_kwh = 0.0
        status_icon = "🔴 OFF"
    elif normal_kwh < 0.05:
        action = "Leave OFF (AI Prediction)"
        optimized_kwh = 0.0
        status_icon = "⚪ OFF"

    total_normal_kwh += normal_kwh
    total_optimized_kwh += optimized_kwh

    appliance_results.append({
        "Appliance": app.replace("_", " "),
        "Status": status_icon,
        "System Action": action,
        "Predicted (kWh)": f"{normal_kwh:.3f}",
        "Optimized (kWh)": f"{optimized_kwh:.3f}"
    })

savings_kwh = total_normal_kwh - total_optimized_kwh
cost_normal = total_normal_kwh * elec_rate
cost_optimized = total_optimized_kwh * elec_rate
savings_rupees = cost_normal - cost_optimized
projected_monthly_savings = savings_rupees * 8 * 30 

# 7. Display Metrics on the Dashboard
st.subheader("💰 Financial Impact (Real-Time)")
st.write(f"Based on current rate: **₹{elec_rate:.2f} / kWh**")
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Predicted Cost/Hr", value=f"₹{cost_normal:.2f}")
col2.metric(label="Optimized Cost/Hr", value=f"₹{cost_optimized:.2f}", delta=f"-₹{savings_rupees:.2f}", delta_color="inverse")
col3.metric(label="Money Saved This Hour", value=f"₹{savings_rupees:.2f}")
col4.metric(label="🚀 Projected Monthly Savings", value=f"₹{projected_monthly_savings:.0f}", delta="Huge Impact!", delta_color="normal")

st.markdown("---")

st.subheader("📊 Energy Metrics (kWh)")
col1, col2, col3 = st.columns(3)
col1.metric(label="Predicted Usage", value=f"{total_normal_kwh:.3f} kWh")
col2.metric(label="Optimized Usage", value=f"{total_optimized_kwh:.3f} kWh", delta=f"-{savings_kwh:.3f} kWh", delta_color="inverse")
col3.metric(label="Total Energy Saved", value=f"{savings_kwh:.3f} kWh")

# 8. Display Appliance Control Status
st.subheader("📱 Appliance Control Status")
results_df = pd.DataFrame(appliance_results)
st.dataframe(results_df, use_container_width=True)

# 9. Historical Chart
st.subheader("📈 Average Daily Energy Profile")
try:
    history_df = pd.read_csv("smart_home_energy_data.csv")
    history_df['Timestamp'] = pd.to_datetime(history_df['Timestamp'])
    history_df['Hour'] = history_df['Timestamp'].dt.hour
    
    chart_data = history_df.groupby('Hour')['Energy_Consumed_kWh'].mean()
    st.area_chart(chart_data)
except FileNotFoundError:
    st.write("No historical data found to display.")

st.success("✅ Financial Engine Active. AI is maximizing your ROI.")