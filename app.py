import streamlit as st
import requests
from datetime import datetime

# App setup
st.set_page_config(page_title="Delhi AQI Dashboard", layout="wide")
st.title("🌀 Delhi AQI Live Dashboard")
st.caption("Live data from OpenAQ")

# API Setup
API_KEY = "b5e603105ac2e6a269e65dd8b3659d91eadc422e602b8becd58c5ee70b867907"
API_URL = "https://api.openaq.org/v2/measurements"

# Location options
locations = [
    "Anand Vihar", "R K Puram", "Punjabi Bagh", "Mandir Marg",
    "Alipur", "Ashok Vihar", "Bawana", "Burari Crossing", "Dilshad Garden",
    "Dwarka", "IGI Airport", "Jahangirpuri", "Mundka", "North Campus"
]
location = st.sidebar.selectbox("📍 Select Location", locations)

# Fetch data from OpenAQ
params = {
    "country": "IN",
    "city": "Delhi",
    "location": location,
    "limit": 100,
    "sort": "desc",
    "order_by": "datetime"
}
headers = {"accept": "application/json", "X-API-Key": API_KEY}
response = requests.get(API_URL, headers=headers, params=params)

# Display data
if response.status_code == 200:
    data = response.json().get("results", [])
    if data:
        latest = data[0]
        parameter = latest["parameter"].upper()
        value = latest["value"]
        unit = latest["unit"]
        timestamp = latest["date"]["utc"]
        time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S+00:00").strftime("%d %b %Y, %I:%M %p")

        st.metric(f"{parameter} Level", f"{value} {unit}")
        st.write(f"📍 **Location:** {location}")
        st.write(f"🕒 **Last Updated:** {time} UTC")

        if parameter == "PM2.5":
            if value <= 30:
                st.success("Good 🟢 – Minimal impact.")
            elif value <= 60:
                st.info("Moderate 🟡 – Sensitive groups take care.")
            elif value <= 90:
                st.warning("Poor 🟠 – Avoid outdoor activity if possible.")
            else:
                st.error("Very Poor 🔴 – Stay indoors.")
        
        with st.expander("🔍 Full Raw Data"):
            st.dataframe(data)
    else:
        st.warning("⚠️ No data available for this location.")
else:
    st.error("❌ Could not fetch data from OpenAQ.")
    
# Footer
st.markdown("---")
st.markdown("Created by **Vinam Jain**, Class 12 — Modern School, Barakhamba Road")
