import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Page setup
st.set_page_config(page_title="Delhi AQI Dashboard", layout="wide")
st.title("🟢 Delhi AQI Dashboard – Live Data from OpenAQ")
st.caption("Created by Vinam Jain | Modern School, Barakhamba Road")

API_KEY = "b5e603105ac2e6a269e65dd8b3659d91eadc422e602b8becd58c5ee70b867907"
HEADERS = {"Accept": "application/json", "X-API-Key": API_KEY}

@st.cache_data(ttl=600)
def fetch_locations():
    url = "https://api.openaq.org/v2/locations"
    params = {"city": "Delhi", "country": "IN", "limit": 500}
    resp = requests.get(url, headers=HEADERS, params=params)
    if resp.status_code == 200:
        df = pd.DataFrame(resp.json().get("results", []))
        return sorted(df["name"].dropna().unique())
    return []

@st.cache_data(ttl=600)
def fetch_measurements(location):
    url = "https://api.openaq.org/v2/measurements"
    params = {
        "city": "Delhi",
        "country": "IN",
        "location": location,
        "limit": 500,
        "sort": "desc",
        "order_by": "datetime"
    }
    resp = requests.get(url, headers=HEADERS, params=params)
    if resp.status_code == 200:
        df = pd.DataFrame(resp.json().get("results", []))
        if not df.empty:
            df["datetime"] = pd.to_datetime(df["date"]["utc"])
            return df[["parameter", "value", "unit", "datetime"]]
    return pd.DataFrame()

locations = fetch_locations()
if not locations:
    st.error("⚠️ No Delhi locations loaded. API key or network issue.")
    st.stop()

selected = st.sidebar.selectbox("📍 Select Monitoring Location", locations)
df = fetch_measurements(selected)
if df.empty:
    st.warning(f"No recent data for {selected}. Try another location.")
    st.stop()

st.subheader(f"Live Readings at {selected}")
latest = df.sort_values("datetime", ascending=False).drop_duplicates("parameter")
cols = st.columns(len(latest))
for idx, row in latest.iterrows():
    cols[idx].metric(row["parameter"].upper(), f"{row['value']} {row['unit']}")

# Health advisory based on PM2.5
if "pm25" in latest["parameter"].values:
    pm25_avg = float(latest[latest["parameter"]=="pm25"]["value"])
    if pm25_avg < 50:
        st.success(f"Air Quality: Good — PM2.5 at {pm25_avg} µg/m³.")
    elif pm25_avg < 100:
        st.warning(f"Moderate — PM2.5 at {pm25_avg} µg/m³.")
    else:
        st.error(f"Unhealthy — PM2.5 at {pm25_avg} µg/m³.")
    st.markdown("- Wear an N95 if PM2.5 > 100\n- Limit outdoor activity on poor air days")

with st.expander("📊 Show Historic Data"):
    st.dataframe(df.sort_values("datetime", ascending=False).head(100))

st.markdown("---")
st.markdown("📘 High school project by **Vinam Jain**, Modern School, Barakhamba Road. Powered by OpenAQ.")
