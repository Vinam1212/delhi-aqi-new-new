import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Delhi AQI Dashboard")
st.title("Delhi AQI Dashboard")
st.markdown("Built by **Vinam Jain**, Modern School Barakhamba Road.")

@st.cache_data(ttl=3600)
def get_delhi_locations():
    url = "https://api.openaq.org/v3/locations"
    params = {"city": "Delhi", "limit": 500}
    resp = requests.get(url, params=params).json().get("results", [])
    df = pd.DataFrame(resp)
    return sorted(df["location"].dropna().unique()) if "location" in df else []

@st.cache_data(ttl=600)
def fetch_measurements(location):
    url = "https://api.openaq.org/v3/measurements"
    params = {
        "city": "Delhi",
        "location": location,
        "limit": 1000,
        "sort": "desc",
        "order_by": "datetime"
    }
    r = requests.get(url, params=params)
    results = r.json().get("results", [])
    df = pd.DataFrame(results)
    if df.empty:
        return df
    df["datetime"] = pd.to_datetime(df["date"].apply(lambda d: d["utc"]))
    df["parameter"] = df["parameter"].str.lower()
    return df[["location", "parameter", "value", "unit", "datetime"]]

locations = get_delhi_locations()
if not locations:
    st.error("❌ No Delhi locations available.")
    st.stop()

station = st.sidebar.selectbox("📍 Choose Station", locations)
df = fetch_measurements(station)
if df.empty:
    st.warning(f"No data for *{station}*. Try another station.")
    st.stop()

# Show latest values
latest = df.sort_values("datetime", ascending=False).drop_duplicates("parameter")
cols = st.columns(len(latest))
for i, row in latest.iterrows():
    cols[i].metric(row["parameter"].upper(), f"{row['value']} {row['unit']}")

# Time trend
st.subheader("Trends (Last ~1000 points)")
trend = df.groupby(["datetime", "parameter"])["value"].mean().unstack().fillna(0)
st.line_chart(trend)

# Correlation heatmap
st.subheader("Pollutant Correlations")
corr = trend.corr()
fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
st.pyplot(fig)

# Health tips
st.subheader("Health & Safety Advisory")
avg_pm25 = df[df["parameter"] == "pm25"]["value"].mean()
if pd.notna(avg_pm25):
    advice = "Good" if avg_pm25 < 50 else "Moderate" if avg_pm25 < 100 else "Poor"
    st.markdown(f"PM2.5 average is **{avg_pm25:.1f} µg/m³** — **{advice}**")
st.markdown("- Masks if PM2.5 > 100\n- Keep windows closed on peak pollution days\n- Children & elderly should limit outdoor exposure")

# Footer
st.markdown("---")
st.markdown("© 2025 Vinam Jain • Modern School Barakhamba Road")



