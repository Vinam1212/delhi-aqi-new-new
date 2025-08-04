import streamlit as st
import pandas as pd
import requests
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Delhi AQI Dashboard")
st.title("📊 Delhi Air Quality Dashboard")
st.markdown("Created by **Vinam Jain**, a high school student at *Modern School Barakhamba Road*.")

# ----- Load Live Data from OpenAQ -----
@st.cache_data(ttl=3600)
def fetch_openaq_data(locations):
    url = "https://api.openaq.org/v2/measurements"
    dfs = []
    for loc in locations:
        params = {
            "city": "Delhi",
            "location": loc,
            "limit": 1000,
            "sort": "desc",
            "order_by": "datetime"
        }
        res = requests.get(url, params=params)
        if res.status_code == 200:
            data = res.json()["results"]
            if data:
                df = pd.DataFrame(data)
                dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

# ---- UI Layout ----
st.sidebar.markdown("📍 **Filters**")
locations_list = ["Chandni Chowk", "Anand Vihar", "R K Puram", "Mandir Marg", "Punjabi Bagh"]
selected_location = st.sidebar.selectbox("Monitoring Station", locations_list)

df = fetch_openaq_data([selected_location])

if df.empty:
    st.warning("⚠️ No data available for the selected station. Try another location.")
    st.stop()

# Fix datetime column
df["datetime"] = pd.to_datetime(df["date"]["utc"])
df["parameter"] = df["parameter"].str.upper()
df = df[["datetime", "parameter", "value"]]

# ---- 1. Trend Line ----
st.subheader("📈 AQI Trend Over Time")
latest = df.groupby("datetime")["value"].mean().reset_index()
if not latest.empty:
    st.line_chart(latest.rename(columns={"datetime": "index"}).set_index("index"))
else:
    st.info("No time trend data available.")

# ---- 2. Heatmap of Pollutants ----
st.subheader("🧪 Heatmap of Pollutant Correlations")
try:
    heatmap_data = df.pivot_table(index="datetime", columns="parameter", values="value").dropna()
    corr = heatmap_data.corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)
except KeyError:
    st.error("Not enough data to generate heatmap.")

# ---- 3. Health & Safety Tips ----
st.subheader("🛡️ Health & Safety Recommendations")
avg_pm25 = df[df["parameter"] == "PM25"]["value"].mean()
if avg_pm25:
    if avg_pm25 < 50:
        msg = "✅ Air quality is good. Enjoy outdoor activities."
    elif avg_pm25 < 100:
        msg = "🟡 Moderate AQI. Sensitive individuals should limit prolonged outdoor exertion."
    else:
        msg = "🔴 Poor air quality. Avoid outdoor exercise. Wear a mask if needed."
    st.success(msg)

# ---- 4. Project Summary ----
st.subheader("📚 Project Summary")
st.markdown("""
This dashboard displays real-time air quality measurements from OpenAQ for different locations in Delhi. 
It helps identify trends, correlations between pollutants, and offers health tips based on PM2.5 levels.

**Data Source:** [OpenAQ](https://openaq.org)  
**Author:** Vinam Jain, Class 12  
**School:** Modern School Barakhamba Road
""")

# ---- Footer ----
st.markdown("---")
st.markdown("© 2025 Vinam Jain | Built using Streamlit")
