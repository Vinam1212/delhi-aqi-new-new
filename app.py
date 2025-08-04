import requests
import streamlit as st
from datetime import datetime

# ---- PAGE SETUP ----
st.set_page_config(page_title="Delhi AQI Live", layout="wide")
st.title("🟢 Delhi AQI Dashboard – Live Data from OpenAQ")
st.caption("Created by Vinam Jain | Data via OpenAQ")

# ---- API SETUP ----
API_KEY = "b5e603105ac2e6a269e65dd8b3659d91eadc422e602b8becd58c5ee70b867907"
headers = {"x-api-key": API_KEY}
base_url = "https://api.openaq.org/v2/latest"

# ---- FUNCTION TO FETCH DATA ----
@st.cache_data(ttl=300)
def fetch_live_data(city="Delhi"):
    params = {
        "city": city,
        "country": "IN",
        "limit": 100,
        "sort": "desc",
        "order_by": "lastUpdated"
    }
    try:
        r = requests.get(base_url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()["results"]
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return []

# ---- FETCH & DISPLAY DATA ----
data = fetch_live_data()

if not data:
    st.warning("No AQI data available right now for Delhi. Try again later.")
else:
    locations = sorted(set(loc["location"] for loc in data))
    selected_location = st.selectbox("📍 Select Location", locations)

    location_data = next((loc for loc in data if loc["location"] == selected_location), None)

    if location_data:
        st.subheader(f"Live Air Quality – {selected_location}")
        st.write(f"Last Updated: {location_data['measurements'][0]['lastUpdated']}")
        for measure in location_data["measurements"]:
            st.metric(label=f"{measure['parameter'].upper()}", value=f"{measure['value']} {measure['unit']}")
    else:
        st.error("Data not found for selected location.")

# ---- FOOTER ----
st.markdown("---")
st.markdown("📘 This is part of a high school project on Delhi's air quality and environmental data justice.")
st.markdown("🔗 [OpenAQ API](https://docs.openaq.org/)")

