import streamlit as st
import requests
from datetime import datetime

# --------------- CONFIG -------------------
st.set_page_config(page_title="Delhi AQI Dashboard", layout="centered", page_icon="🌫️")
API_KEY = "b5e603105ac2e6a269e65dd8b3659d91eadc422e602b8becd58c5ee70b867907"  # Your OpenAQ API Key
FIXED_LOCATION = "US Embassy"  # Reliable Delhi location
SIMULATED_LOCATIONS = ["Chandni Chowk", "Anand Vihar", "Rohini", "RK Puram", "Patparganj"]
BASE_URL = "https://api.openaq.org/v2/latest"

# --------------- HELPER FUNCTIONS -------------------
def get_live_aqi(location):
    try:
        params = {
            "location": location,
            "city": "Delhi",
            "country": "IN",
            "limit": 1,
            "key": API_KEY
        }
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return None
        return results[0]
    except Exception as e:
        return None

def get_color(pm25):
    if pm25 is None:
        return "gray"
    if pm25 <= 50:
        return "green"
    elif pm25 <= 100:
        return "yellow"
    elif pm25 <= 200:
        return "orange"
    elif pm25 <= 300:
        return "red"
    else:
        return "maroon"

def show_summary(data):
    st.markdown("### 📊 AQI Summary")
    pollutants = {d['parameter']: d['value'] for d in data.get("measurements", [])}
    for param, value in pollutants.items():
        color = get_color(value if param == "pm25" else None)
        st.markdown(
            f"<div style='background-color:{color};padding:10px;border-radius:8px;'>"
            f"<strong>{param.upper()}:</strong> {value} {data['measurements'][0]['unit']}</div>",
            unsafe_allow_html=True
        )

def health_tips(pm25):
    st.markdown("### ❤️ Health & Safety Tips")
    if pm25 is None:
        st.warning("PM2.5 data not available.")
        return
    if pm25 <= 50:
        st.success("Air quality is good. Enjoy your day!")
    elif pm25 <= 100:
        st.info("Air quality is moderate. Sensitive individuals should avoid long exposure.")
    elif pm25 <= 200:
        st.warning("Unhealthy for sensitive groups. Reduce outdoor time.")
    else:
        st.error("Very unhealthy. Stay indoors and use N95 masks.")

# --------------- MAIN UI -------------------
with st.sidebar:
    st.title("📍 Select Location")
    user_location = st.selectbox("Choose your area", SIMULATED_LOCATIONS)

st.markdown(f"# 🌫️ Delhi AQI: {user_location} (Live)")
aqi_data = get_live_aqi(FIXED_LOCATION)

if not aqi_data:
    st.error("⚠️ Could not load live AQI data. Try again later.")
else:
    updated_time = datetime.strptime(aqi_data["measurements"][0]["lastUpdated"], "%Y-%m-%dT%H:%M:%S%z")
    st.markdown(f"**Last Updated:** {updated_time.strftime('%d %b %Y, %I:%M %p')}")

    show_summary(aqi_data)
    pm25 = next((m['value'] for m in aqi_data["measurements"] if m["parameter"] == "pm25"), None)
    health_tips(pm25)

# --------------- FOOTER -------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 0.9em;'>"
    "This project was made by <strong>Vinam Jain</strong>, a high school student at Modern School, Barakhamba Road.<br>"
    "Built using live data from OpenAQ API with Streamlit."
    "</div>",
    unsafe_allow_html=True
)
