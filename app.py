import streamlit as st
import pandas as pd
import requests
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="Delhi AQI Dashboard", layout="wide")

# === Theme Toggle ===
theme = st.sidebar.radio("🌗 Theme Mode", ["Light", "Dark"], index=1)
if theme == "Dark":
    st.markdown("""
        <style>
        body { background-color: #1e1e1e; color: white; }
        .stApp { background-color: #1e1e1e; color: white; }
        </style>
    """, unsafe_allow_html=True)

# === Location List ===
LOCATIONS = ["Anand Vihar", "Chandni Chowk", "Punjabi Bagh", "RK Puram", "Mandir Marg", "Ashok Vihar"]

# === Sidebar Filters ===
st.sidebar.title("📍 Filters")
selected_location = st.sidebar.selectbox("Monitoring Station", LOCATIONS)

# === Fetch Live Data from OpenAQ ===
@st.cache_data(ttl=3600)
def fetch_live_data(location_name):
    base_url = "https://api.openaq.org/v2/measurements"
    params = {
        "city": "Delhi",
        "location": location_name,
        "parameter": ["pm25", "pm10", "no2", "o3", "so2", "co"],
        "limit": 1000,
        "date_from": (datetime.utcnow() - timedelta(days=14)).isoformat(),
        "date_to": datetime.utcnow().isoformat(),
        "sort": "desc",
        "order_by": "datetime"
    }
    response = requests.get(base_url, params=params)
    results = response.json().get("results", [])
    df = pd.DataFrame(results)
    if not df.empty:
        df["datetime"] = pd.to_datetime(df["date"].apply(lambda x: x["utc"]))
        df["parameter"] = df["parameter"].str.lower()
        df["location"] = df["location"].str.strip()
        df = df.rename(columns={"value": "value", "parameter": "parameter"})
    return df

df = fetch_live_data(selected_location)

# === Title ===
st.title("🧪 Delhi AQI Dashboard")
st.markdown("Real-time air quality data from Delhi's OpenAQ stations. View trends, summaries, and health impacts.")

# === Live AQI Summary Panel ===
st.subheader("📡 Live AQI")

def get_health_advice(aqi_val):
    if aqi_val < 50:
        return "🟢 Good — Enjoy outdoor activities."
    elif aqi_val < 100:
        return "🟡 Moderate — Sensitive individuals should take care."
    elif aqi_val < 200:
        return "🟠 Poor — Consider reducing prolonged outdoor exertion."
    else:
        return "🔴 Hazardous — Avoid outdoor exposure, wear a mask."

pm25_val = None
if not df.empty and "parameter" in df.columns and "value" in df.columns:
    pm25_data = df[df["parameter"] == "pm25"]
    if not pm25_data.empty:
        pm25_val = pm25_data["value"].iloc[0]

if pm25_val is not None:
    st.markdown(f"""
    ### Today's PM2.5 AQI: **{pm25_val:.0f} µg/m³**  
    **Status**: {get_health_advice(pm25_val)}  
    **Location**: {selected_location}
    """)
else:
    st.warning("⚠️ PM2.5 data is currently unavailable for this location. Try switching to another station.")

# === Health & Safety Section ===
st.subheader("🏥 Health & Safety")
st.markdown("""
Air pollution, especially PM2.5 and NO₂, can worsen asthma, lung issues, and cardiovascular risks.

- Children, elderly, and those with respiratory illness should **limit outdoor time**.
- Wear **N95 masks** if AQI is over 150.
- Consider **HEPA purifiers** for indoor spaces.
""")

# === Past Trends (Line Graph) ===
st.subheader("📈 Fortnightly Trends")
if not df.empty:
    trend_df = df.groupby(["datetime", "parameter"])["value"].mean().unstack()
    fig, ax = plt.subplots(figsize=(12, 4))
    trend_df.plot(ax=ax)
    ax.set_ylabel("Concentration (µg/m³)")
    ax.set_xlabel("Time")
    plt.xticks(rotation=45)
    plt.title(f"14-Day Trend at {selected_location}")
    st.pyplot(fig)
else:
    st.warning("No time trend data available.")

# === Correlation Heatmap ===
st.subheader("🌡️ Heatmap of Pollutant Correlations")
heatmap_data = df.pivot_table(index="datetime", columns="parameter", values="value").dropna()
if not heatmap_data.empty:
    corr = heatmap_data.corr()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax2)
    st.pyplot(fig2)
else:
    st.warning("Insufficient data for correlation analysis.")

# === Summary Statistics ===
st.subheader("📌 Summary Statistics")
if not df.empty:
    stats = df.groupby("parameter")["value"].agg(["mean", "max", "min", "count"]).round(2)
    st.dataframe(stats)
else:
    st.info("No data available for summary statistics.")

# === Data Preview ===
st.subheader("📄 Raw Data Preview")
if not df.empty:
    st.dataframe(df.reset_index(drop=True))
else:
    st.info("No data to preview.")

# === Download Button ===
if not df.empty:
    st.download_button(
        label="📥 Download Live AQI Data",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_location}_aqi_data.csv",
        mime="text/csv"
    )

# === Project Footer ===
st.markdown("---")
st.markdown("""
#### 🧾 About This Project  
This AQI Dashboard was developed by **Vinam Jain**, a high school student at **Modern School, Barakhamba Road**.

The project tracks real-time pollution levels in Delhi using OpenAQ data.  
It visualizes pollutant trends, gives health recommendations, and promotes awareness on environmental health and justice.

_Week 4: Independent Research Project | CollegePass_
""")

