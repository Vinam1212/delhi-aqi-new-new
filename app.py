import streamlit as st
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(page_title="Delhi AQI Dashboard", layout="wide")

# OpenAQ API Key
API_KEY = "b5e603105ac2e6a269e65dd8b3659d91eadc422e602b8becd58c5ee70b867907"
HEADERS = {"X-API-Key": API_KEY}

# Sidebar theme switch
st.sidebar.title("⚙️ Settings")
theme = st.sidebar.radio("🌗 Theme Mode", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("""
        <style>
        body, .stApp {background-color:#111; color:#fff;}
        .css-1d391kg {background-color:#222;}
        </style>
    """, unsafe_allow_html=True)

st.title("🌆 Delhi AQI Dashboard – Live Data")
st.markdown("Created by **Vinam Jain**, Modern School Barakhamba Road")

@st.cache_data(ttl=3600)
def get_delhi_locations():
    url = "https://api.openaq.org/v2/locations"
    params = {
        "country": "IN",
        "city": "Delhi",
        "limit": 100,
        "sort": "desc"
    }
    r = requests.get(url, headers=HEADERS, params=params)
    results = r.json().get("results", [])
    return sorted([loc["name"] for loc in results if "name" in loc])

@st.cache_data(ttl=600)
def get_station_data(station_name):
    url = "https://api.openaq.org/v2/measurements"
    params = {
        "city": "Delhi",
        "location": station_name,
        "limit": 1000,
        "sort": "desc",
        "order_by": "datetime"
    }
    r = requests.get(url, headers=HEADERS, params=params)
    data = r.json().get("results", [])
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame()
    df["datetime"] = pd.to_datetime(df["date"].apply(lambda d: d["utc"]))
    df["parameter"] = df["parameter"].str.lower()
    return df[["datetime", "parameter", "value"]]

# UI: Station Selector
locations = get_delhi_locations()
if not locations:
    st.error("⚠️ Could not load locations. Check API key or try later.")
    st.stop()

selected_station = st.sidebar.selectbox("📍 Select Station", locations)
data = get_station_data(selected_station)

if data.empty:
    st.warning("No recent AQI data found for this station.")
    st.stop()

# Trend Chart
st.subheader(f"📈 AQI Trend at {selected_station}")
pivot_df = data.pivot(index="datetime", columns="parameter", values="value")
st.line_chart(pivot_df)

# Stats
st.subheader("📊 Summary Statistics")
stats = data.groupby("parameter")["value"].agg(["mean", "max", "count"]).round(2)
st.dataframe(stats)

# Health advisory
if "pm25" in pivot_df.columns:
    avg_pm25 = pivot_df["pm25"].mean()
    if avg_pm25 < 50:
        msg = "🟢 Good"
    elif avg_pm25 < 100:
        msg = "🟡 Moderate"
    elif avg_pm25 < 200:
        msg = "🟠 Unhealthy"
    else:
        msg = "🔴 Hazardous"
    st.subheader("🩺 Health Advisory")
    st.markdown(f"**Avg PM2.5:** {avg_pm25:.1f} µg/m³ — **{msg}**")
    st.markdown("- Avoid outdoor activity if air is Unhealthy or worse\n"
                "- Use air purifiers and N95 masks indoors")

# Correlation Heatmap
if pivot_df.shape[1] >= 2:
    st.subheader("🔗 Pollutant Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(pivot_df.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    st.pyplot(fig)

# Raw Table
st.subheader("🧾 Recent Raw Data")
st.dataframe(data.sort_values("datetime", ascending=False).head(50))

# Footer
st.markdown("---")
st.markdown("""
**Project by Vinam Jain**, Class 12, Modern School Barakhamba Road  
Built using **Streamlit**, powered by **OpenAQ**  
""")
