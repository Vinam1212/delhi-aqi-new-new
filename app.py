# streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- Config ---
st.set_page_config(page_title="Delhi AQI Dashboard", layout="wide")

# --- Sidebar ---
st.sidebar.title("🔧 Controls")
pollutant_choice = st.sidebar.selectbox("Select Pollutant", ["pm25", "no2", "o3"])
theme = st.sidebar.radio("Theme", ["Dark", "Light"])
location_display = st.sidebar.selectbox("Location", ["Chandni Chowk", "Anand Vihar", "RK Puram (simulated)"])

# --- Style ---
if theme == "Dark":
    st.markdown(
        """
        <style>
        body { background-color: #1e1e1e; color: white; }
        .main { background-color: #1e1e1e; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# --- AQI Data Setup ---
FIXED_LOCATION = "Anand Vihar"
API_URL = "https://api.openaq.org/v2/measurements"

params = {
    "city": "Delhi",
    "location": FIXED_LOCATION,
    "parameter": pollutant_choice,
    "limit": 100,
    "sort": "desc",
    "order_by": "datetime"
}

try:
    r = requests.get(API_URL, params=params)
    data = r.json()["results"]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"]["utc"].apply(lambda x: x))
    df.sort_values("date", inplace=True)
except:
    # Fallback simulated data
    df = pd.DataFrame({
        "date": pd.date_range(end=pd.Timestamp.now(), periods=24, freq="H"),
        "value": np.random.randint(20, 80, size=24)
    })

# --- Centered AQI ---
latest_aqi = int(df["value"].iloc[-1]) if not df.empty else 0

st.markdown("""
    <style>
        .aqi-box {
            margin-top: 20px;
            font-size: 60px;
            font-weight: bold;
            color: red;
            background-color: white;
            border-radius: 50%;
            width: 120px;
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-left: auto;
            margin-right: auto;
            box-shadow: 0px 0px 15px rgba(255,0,0,0.4);
            animation: pop 1s ease-in-out;
        }
        @keyframes pop {
            0% { transform: scale(0.7); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }
    </style>
    <div class="aqi-box">{}</div>
""".format(latest_aqi), unsafe_allow_html=True)

# --- Date & Time (IST) ---
ist_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
st.markdown(
    f"<div style='text-align:right; font-size:16px;'>🕒 {ist_now.strftime('%A, %d %B %Y | %I:%M %p')} IST</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# --- Heatmap ---
st.subheader("🕓 24-Hour Heatmap")
heatmap_data = df.set_index("date").resample("H").mean().fillna(method="ffill")
fig, ax = plt.subplots(figsize=(10, 1))
heatmap_array = heatmap_data["value"].values.reshape(1, -1)
im = ax.imshow(heatmap_array, cmap="Reds", aspect="auto")
ax.set_yticks([])
ax.set_xticks(np.arange(len(heatmap_data)))
ax.set_xticklabels([dt.strftime("%H:%M") for dt in heatmap_data.index], rotation=90)
plt.colorbar(im, orientation="vertical", ax=ax)
st.pyplot(fig)

# --- Time Graph ---
st.subheader(f"📊 {pollutant_choice.upper()} Trend Over Time")
fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(df["date"], df["value"], marker="o", color="green")
ax2.set_xlabel("Time")
ax2.set_ylabel(f"{pollutant_choice.upper()} (µg/m³)")
ax2.set_title(f"{pollutant_choice.upper()} Concentration Over Last 24 Hours")
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
fig2.autofmt_xdate()
st.pyplot(fig2)

# --- Footer ---
st.markdown(
    "<hr><center><small>Project by Vinam Jain · Class 12 · Modern School Barakhamba Road</small></center>",
    unsafe_allow_html=True
)
