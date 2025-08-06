import streamlit as st
import requests
import pandas as pd
import datetime

# Fixed OpenAQ location details
CITY_NAME = "Delhi"
LOCATION_NAME = "RK Puram"
PARAMETER = "pm25"
API_KEY = "b5e603105ac2e6a269e65dd8b3659d91eadc422e602b8becd58c5ee70b867907"
HEADERS = {"X-API-Key": API_KEY}

# Fake location list for UI only
fake_locations = ["Chandni Chowk", "Anand Vihar", "RK Puram", "Punjabi Bagh", "Civil Lines"]

st.set_page_config(page_title="Delhi AQI (Live)", layout="centered", initial_sidebar_state="auto")

st.markdown(
    "<h1 style='text-align: center; color: white;'>🟫 Delhi AQI: <span style='color:#ffcc00;'>Chandni Chowk (Live)</span></h1>",
    unsafe_allow_html=True,
)

# Simulate location dropdown
user_location = st.selectbox("Select location in Delhi (simulated):", fake_locations, index=0)

# --- Fetch live data function ---
def fetch_aqi():
    try:
        url = f"https://api.openaq.org/v2/latest?city={CITY_NAME}&location={LOCATION_NAME}&parameter={PARAMETER}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                return data["results"][0]["measurements"][0]["value"]
    except:
        pass
    return None

# --- AQI Data ---
aqi_value = fetch_aqi()
if aqi_value is None:
    aqi_value = 110  # fallback value if API fails
    st.warning("⚠️ Showing simulated AQI due to OpenAQ API issue.")

# --- AQI display ---
st.metric(label=f"PM2.5 AQI at {user_location}", value=f"{aqi_value} µg/m³")

# --- Interpretation ---
def interpret_aqi(pm25):
    if pm25 <= 50:
        return "🟩 Good"
    elif pm25 <= 100:
        return "🟨 Moderate"
    elif pm25 <= 150:
        return "🟧 Unhealthy for Sensitive Groups"
    elif pm25 <= 200:
        return "🟥 Unhealthy"
    elif pm25 <= 300:
        return "🟪 Very Unhealthy"
    else:
        return "🟥 Hazardous"

st.info(f"**Air Quality Level:** {interpret_aqi(aqi_value)}")

# --- Footer ---
st.markdown(
    "<hr><center><sub>This project was made by <strong>Vinam Jain</strong>, a high school student at Modern School, Barakhamba Road.<br>Built using live data from OpenAQ API with Streamlit.</sub></center>",
    unsafe_allow_html=True,
)
