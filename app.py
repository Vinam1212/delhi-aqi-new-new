import streamlit as st
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Delhi AQI Dashboard", layout="wide")
st.title("🌆 Delhi AQI Dashboard – Live Data")
st.caption("Created by Vinam Jain, Modern School Barakhamba Road")

API_KEY = "b5e603105ac2e6a269e65dd8b3659d91eadc422e602b8becd58c5ee70b867907"
HEADERS = {"X-API-Key": API_KEY}

@st.cache_data(ttl=300)
def fetch_latest_city(city="Delhi", country="IN"):
    url = "https://api.openaq.org/v1/latest"
    params = {"city": city, "country": country}
    resp = requests.get(url, headers=HEADERS, params=params)
    return resp.json().get("results", [])

data = fetch_latest_city()

if not data:
    st.error("⚠️ No data available from OpenAQ for Delhi right now.")
    st.stop()

# convert to DataFrame
df = pd.json_normalize(data, record_path=["measurements"],
                       meta=[["location"], ["city"]])
df["parameter"] = df["parameter"].str.lower()
df["datetime"] = pd.to_datetime(df["lastUpdated"])

st.subheader("📊 Latest Measurements across Delhi")
st.dataframe(df[["location", "parameter", "value", "unit", "datetime"]].head(100))

stats = df.groupby("parameter")["value"].agg(["mean", "max", "count"]).round(2)
st.subheader("📌 Summary Statistics")
st.dataframe(stats)

pivot = df.pivot_table(index="location", columns="parameter", values="value")
if pivot.shape[1] >= 2:
    st.subheader("🔗 Pollutant Correlations Across Locations")
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(pivot.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    st.pyplot(fig)

if "pm25" in stats.index:
    avg_pm25 = stats.loc["pm25", "mean"]
    advice = ("Good🟢" if avg_pm25<50 else
              "Moderate🟡" if avg_pm25<100 else
              "Poor🟠" if avg_pm25<200 else
              "Hazardous🔴")
    st.subheader("🩺 Health Advisory")
    st.markdown(f"**Avg PM2.5 (city‑wide):** {avg_pm25:.1f} µg/m³ — **{advice}**")
    st.markdown("- Sensitive persons limit outdoor exposure\n"
                "- Use N95 masks indoors on poor air days")

st.markdown("---")
st.markdown("""
#### About This Project  
Developed by **Vinam Jain**, Class 12, Modern School Barakhamba Road.  
Uses OpenAQ v1 API to fetch pollution data city‑wide for Delhi, visualize pollutant stats and offer health safety guidance.
""")
