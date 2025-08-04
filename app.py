import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Delhi AQI Dashboard", layout="wide")

# Title & Subtitle
st.title("📊 Delhi Air Quality Dashboard")
st.markdown("Created by **Vinam Jain**, a high school student at *Modern School Barakhamba Road*.")

# Station list
stations = [
    "Anand Vihar", "R K Puram", "Mandir Marg", "Punjabi Bagh",
    "Chandni Chowk", "ITO", "Ashok Vihar", "Dwarka", "Jahangirpuri"
]

# Sidebar
st.sidebar.header("📍 Filters")
selected_station = st.sidebar.selectbox("Monitoring Station", stations)

# Fetch OpenAQ data
@st.cache_data(ttl=600)
def fetch_openaq_data(city="Delhi"):
    url = f"https://api.openaq.org/v2/measurements?city={city}&limit=1000&sort=desc"
    r = requests.get(url)
    data = r.json()

    if "results" not in data:
        return pd.DataFrame()

    df = pd.DataFrame(data["results"])
    if df.empty:
        return df

    df = df[["location", "parameter", "value", "unit", "date"]]
    df["datetime"] = pd.to_datetime(df["date"].apply(lambda x: x["utc"]))
    return df.drop(columns=["date"])

# Load and filter data
data = fetch_openaq_data()

filtered = data[data["location"].str.lower().str.strip() == selected_station.lower().strip()]

if filtered.empty:
    st.warning("⚠️ No data available for the selected station. Try another location.")
else:
    latest = filtered.sort_values("datetime", ascending=False).head(10)
    st.success(f"✅ Latest Readings from **{selected_station}**")
    st.dataframe(latest[["datetime", "parameter", "value", "unit"]])

    # Plot
    chart_data = filtered.groupby(["datetime", "parameter"])["value"].mean().unstack().fillna(0)
    st.line_chart(chart_data)

# Health & Safety Info
with st.expander("🛡️ Health & Safety Recommendations"):
    st.markdown("""
- **PM2.5 > 100**: Avoid outdoor activities.
- **PM10 > 150**: Wear a mask.
- **NO₂ > 80**: Risky for people with asthma.
- **General Tip**: Use air purifiers indoors if available.
""")

# Project Summary
with st.expander("📘 Project Summary"):
    st.markdown("""
This dashboard shows real-time air quality data from OpenAQ for Delhi.
It helps users monitor pollutants like PM2.5, PM10, and NO₂ at key locations.
The goal is to promote awareness and health-focused decisions using environmental data.
""")

# Credits
st.markdown("---")
st.markdown("© 2025 | Dashboard developed by **Vinam Jain** | Data from [OpenAQ](https://openaq.org)")

