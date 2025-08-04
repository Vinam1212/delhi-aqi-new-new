import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# --- SETTINGS ---
st.set_page_config(page_title="Delhi AQI", layout="wide")
st.title("📊 Delhi Air Quality Dashboard")
st.markdown("Created by **Vinam Jain**, a high school student at *Modern School Barakhamba Road*.")

# --- SIDEBAR ---
st.sidebar.header("📍 Filters")
stations = ["Anand Vihar", "Chandni Chowk", "R K Puram", "Mandir Marg"]
selected_station = st.sidebar.selectbox("Monitoring Station", stations)

# --- HELPER FUNCTION TO FETCH LIVE DATA ---
@st.cache_data(ttl=300)
def fetch_openaq_data(location):
    try:
        url = f"https://api.openaq.org/v2/measurements"
        params = {
            "city": "Delhi",
            "location": location,
            "limit": 100,
            "sort": "desc",
            "order_by": "datetime"
        }
        res = requests.get(url, params=params)
        json_data = res.json()

        if "results" in json_data and len(json_data["results"]) > 0:
            df = pd.DataFrame(json_data["results"])
            df["datetime"] = pd.to_datetime(df["date"].apply(lambda x: x["utc"]))
            df["parameter"] = df["parameter"].str.upper()
            return df[["location", "parameter", "value", "unit", "datetime"]]
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# --- LOAD DATA ---
data = fetch_openaq_data(selected_station)

if data.empty or "location" not in data.columns:
    st.warning("⚠️ No data available for the selected station. Try another station or check back later.")
else:
    # --- METRICS ---
    latest = data.sort_values("datetime", ascending=False).drop_duplicates("parameter")
    st.subheader("📈 Latest Readings")
    cols = st.columns(len(latest))
    for i, row in latest.iterrows():
        with cols[i]:
            st.metric(label=row["parameter"], value=f"{row['value']} {row['unit']}")

    # --- HISTORICAL CHART ---
    st.subheader("📉 Trend over Time")
    for pollutant in data["parameter"].unique():
        df_pollutant = data[data["parameter"] == pollutant]
        st.line_chart(df_pollutant.set_index("datetime")["value"], height=200, use_container_width=True)

    # --- HEALTH & SAFETY INFO ---
    st.subheader("🚨 Health & Safety Guidelines")
    st.markdown("""
    - **PM2.5 > 100**: Avoid outdoor activities.
    - **NO2 > 80**: Risk of respiratory issues.
    - Wear masks and keep windows closed.
    - Check AQI before planning travel or exercise.
    """)

    # --- PROJECT SUMMARY ---
    st.subheader("📝 About This Project")
    st.markdown("""
    This dashboard tracks live air quality data across major Delhi stations using the [OpenAQ API](https://docs.openaq.org/).
    
    **Features:**
    - Live data display
    - Historical trends
    - Health advisories
    - Support for multiple locations
    
    **Created as part of a high school research project** on data inequality and environmental monitoring.
    """)

# --- FOOTER ---
st.markdown("---")
st.markdown("© 2025 Vinam Jain | Modern School Barakhamba Road")


