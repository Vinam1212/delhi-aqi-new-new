import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from streamlit_option_menu import option_menu

# Fake fallback AQI data for Chandni Chowk
def load_fallback_data():
    now = dt.datetime.now()
    hours = [now - dt.timedelta(hours=i) for i in range(24)][::-1]
    data = {
        "datetime": hours,
        "PM2.5": np.random.randint(80, 150, 24),
        "NO2": np.random.randint(30, 90, 24),
        "O3": np.random.randint(10, 50, 24),
        "CO": np.round(np.random.uniform(0.5, 2.0, 24), 2),
        "SO2": np.random.randint(10, 40, 24),
    }
    return pd.DataFrame(data)

df = load_fallback_data()

# Sidebar configuration
st.set_page_config(layout="wide", page_title="Delhi AQI Dashboard")

with st.sidebar:
    st.title("🧭 Navigation")
    location = st.selectbox("📍 Select Location", ["Chandni Chowk", "Anand Vihar", "R K Puram", "Punjabi Bagh", "Mandir Marg"])
    pollutant = st.selectbox("💨 Select Pollutant", ["PM2.5", "NO2", "O3", "CO", "SO2"])
    theme = st.radio("🌓 Theme", ["Light", "Dark"])

# Apply theme colors
if theme == "Dark":
    st.markdown(
        """
        <style>
        body, .stApp {
            background-color: #1E1E1E;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# AQI background banner
st.markdown(
    """
    <div style="background-image: linear-gradient(to right, #1a936f, #114b5f); padding: 20px; border-radius: 10px; text-align:center">
        <h1 style="color:white">🌀 Delhi Air Quality Dashboard</h1>
        <p style="color:white">Simulated real-time data from Chandni Chowk • Static fallback enabled</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Date and time display
now = dt.datetime.now().strftime("%A, %d %B %Y | %I:%M %p")
st.markdown(f"<p style='text-align:right;font-size:16px;'>🕒 {now}</p>", unsafe_allow_html=True)

# Show AQI card
st.markdown("---")
current_value = df[pollutant].iloc[-1]
st.markdown(f"""
<div style="display: flex; justify-content: center;">
    <div style="background-color: #f4f4f4; padding: 25px 50px; border-radius: 50px; text-align: center; box-shadow: 2px 2px 10px #ccc;">
        <h2 style="margin: 0;">{pollutant}</h2>
        <h1 style="margin: 5px 0; color: #d7263d;">{current_value}</h1>
        <p style="margin: 0;">Current AQI Level</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Heatmap section
st.markdown("### 🔥 24-Hour Heatmap")
pivot_df = df[["datetime", pollutant]]
pivot_df["Hour"] = pivot_df["datetime"].dt.strftime("%H:%M")
pivot_df = pivot_df.set_index("Hour").drop("datetime", axis=1).T

fig, ax = plt.subplots(figsize=(12, 2))
im = ax.imshow(pivot_df, cmap="Reds", aspect="auto")
ax.set_yticks([0])
ax.set_yticklabels([pollutant])
ax.set_xticks(range(24))
ax.set_xticklabels(pivot_df.columns, rotation=90)
plt.colorbar(im, ax=ax, orientation='vertical')
st.pyplot(fig)

# Line graph
st.markdown("### 📈 Time Series")
st.line_chart(df.set_index("datetime")[pollutant])

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:gray;'>© 2025 Vinam Jain • Modern School Barakhamba Road</p>",
    unsafe_allow_html=True
)
