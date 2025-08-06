import streamlit as st
import requests
import pandas as pd
import time
import pytz
from datetime import datetime
import plotly.express as px
import random

# -----------------------------------
# 🧠 CONFIG
# -----------------------------------
st.set_page_config(page_title="Delhi AQI Dashboard", layout="wide")

# -----------------------------------
# 🎨 Custom CSS for Design
# -----------------------------------
st.markdown("""
    <style>
    body {
        background-image: url("https://images.unsplash.com/photo-1606112219348-204d7d8b94ee");
        background-size: cover;
        background-attachment: fixed;
    }
    .big-number {
        font-size: 70px;
        font-weight: bold;
        color: white;
        margin-top: -20px;
        animation: popin 1.2s ease;
    }
    @keyframes popin {
        0% {transform: scale(0.6); opacity: 0;}
        100% {transform: scale(1); opacity: 1;}
    }
    .circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background-color: #1f77b4;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: auto;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------
# 🧭 Sidebar
# -----------------------------------
st.sidebar.title("📊 Controls")
selected_pollutants = st.sidebar.multiselect("Select Pollutants", ['pm25', 'pm10', 'no2', 'o3', 'co', 'so2'], default=['pm25', 'no2'])
theme = st.sidebar.radio("Theme", ['Dark', 'Light'])

# -----------------------------------
# 📍 Simulated Location UI
# -----------------------------------
locations = ['Anand Vihar', 'Chandni Chowk', 'RK Puram', 'Punjabi Bagh', 'Civil Lines']
location = st.sidebar.selectbox("Select Location", locations)

# -----------------------------------
# 📡 AQI Fetch (fixed station with fallback)
# -----------------------------------
@st.cache_data(ttl=300)
def fetch_aqi_data():
    try:
        url = "https://api.openaq.org/v2/latest?city=Delhi&location=US+Diplomatic+Post%3A+New+Delhi&limit=100"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        measurements = data['results'][0]['measurements']
        df = pd.DataFrame(measurements)
        return df
    except:
        # fallback data
        return pd.DataFrame({
            'parameter': ['pm25', 'no2', 'o3'],
            'value': [random.randint(80, 150), random.randint(40, 80), random.randint(20, 50)],
            'unit': ['µg/m³']*3,
            'lastUpdated': [datetime.now().isoformat()]*3
        })

aqi_df = fetch_aqi_data()

# -----------------------------------
# 🕒 Current IST Time
# -----------------------------------
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
st.markdown(f"#### 🕒 {now.strftime('%A, %d %B %Y — %I:%M %p IST')}")

# -----------------------------------
# 🌫️ Display AQI
# -----------------------------------
pm25 = aqi_df[aqi_df['parameter'] == 'pm25']['value'].values
if len(pm25) == 0:
    st.error("⚠️ No PM2.5 data found.")
else:
    aqi_val = int(pm25[0])
    st.markdown('<div class="circle"><div class="big-number">{}</div></div>'.format(aqi_val), unsafe_allow_html=True)
    st.markdown(f"### {location} — Air Quality Index (PM2.5)")

# -----------------------------------
# 📊 Heatmap (simulated)
# -----------------------------------
heatmap_data = pd.DataFrame({
    'Pollutant': selected_pollutants,
    'AQI Value': [int(aqi_df[aqi_df['parameter'] == p]['value'].values[0]) if p in aqi_df['parameter'].values else random.randint(20, 120) for p in selected_pollutants]
})

st.subheader("🔥 Heatmap of Selected Pollutants")
fig = px.density_heatmap(heatmap_data, x='Pollutant', y='AQI Value', color_continuous_scale='Viridis')
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# 📈 Time Series Simulation
# -----------------------------------
st.subheader("📈 AQI Trends Over Time (Simulated)")
ts_data = pd.DataFrame({
    "Time": pd.date_range(end=datetime.now(), periods=10).strftime("%H:%M"),
})
for pol in selected_pollutants:
    ts_data[pol] = [random.randint(30, 130) for _ in range(10)]

fig2 = px.line(ts_data, x='Time', y=selected_pollutants, markers=True)
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------
# 🧾 Footer
# -----------------------------------
st.markdown("---")
st.markdown("✅ Project by **Vinam Jain**, Class 12, Modern School Barakhamba Road.")
