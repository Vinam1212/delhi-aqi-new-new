import streamlit as st
import requests
from datetime import datetime

# OpenAQ API setup
API_KEY = "b5e603105ac2e6a269e65dd8b3659d91eadc422e602b8becd58c5ee70b867907"
HEADERS = {"x-api-key": API_KEY}
BASE_URL = "https://api.openaq.org/v2/measurements"

st.set_page_config(page_title="Delhi AQI Dashboard", layout="wide", initial_sidebar_state="auto")
st.markdown("<h1 style='color:white;'>Delhi AQI Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p><b>Built by Vinam Jain, Modern School Barakhamba Road.</b></p>", unsafe_allow_html=True)

# Get list of locations in Delhi
@st.cache_data(ttl=3600)
def fetch_delhi_locations():
    url = "https://api.openaq.org/v2/locations"
    params = {
        "city": "Delhi",
        "country": "IN",
        "limit": 100,
        "sort": "asc"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        results = response.json().get("results", [])
        return [loc["name"] for loc in results]
    return []

locations = fetch_delhi_locations()

if not locations:
    st.error("🚫 No Delhi locations available. Please check your API key or network.")
    st.stop()

selected_location = st.selectbox("📍 Select a Delhi AQI Monitoring Location:", locations)

# Fetch latest AQI data for selected location
def get_aqi_data(location):
    params = {
        "city": "Delhi",
        "country": "IN",
        "limit": 50,
        "sort": "desc",
        "order_by": "datetime",
        "location": location
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []

data = get_aqi_data(selected_location)

if not data:
    st.warning("No recent AQI data found for this location.")
    st.stop()

# Show AQI readings
st.subheader(f"📊 Latest AQI Measurements at {selected_location}")

for entry in data[:5]:  # Show top 5 readings
    parameter = entry["parameter"].upper()
    value = entry["value"]
    unit = entry["unit"]
    time = datetime.fromisoformat(entry["date"]["utc"][:-1]).strftime("%Y-%m-%d %H:%M")
    st.info(f"**{parameter}**: {value} {unit} (as of {time} UTC)")

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size: 0.9em;'>🌍 Data from <a href='https://openaq.org' target='_blank'>OpenAQ</a> | Created for educational use.</p>",
    unsafe_allow_html=True
)
