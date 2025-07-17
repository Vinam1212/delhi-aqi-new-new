import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Delhi AQI Dashboard", layout="wide")

# === Theme Toggle ===
theme = st.sidebar.radio("🌗 Theme Mode", ["Light", "Dark"], index=1)
if theme == "Dark":
    st.markdown(
        """
        <style>
        body { background-color: #1e1e1e; color: white; }
        .stApp { background-color: #1e1e1e; color: white; }
        </style>
        """,
        unsafe_allow_html=True
    )

# === Load Data ===
@st.cache_data
def load_data():
    df = pd.read_csv("AQI DATA.csv", parse_dates=["datetimeLocal"])
    df.columns = df.columns.str.strip().str.lower()
    df["parameter"] = df["parameter"].str.lower()
    df["location_name"] = df["location_name"].str.strip()
    return df

df = load_data()

# === Sidebar Filters ===
st.sidebar.title("📍 Filters")
locations = sorted(df["location_name"].unique())
selected_location = st.sidebar.selectbox("Select Location", locations)

df = df[df["location_name"] == selected_location]

pollutants = sorted(df["parameter"].unique())
selected_pollutants = st.sidebar.multiselect("Select Pollutants", pollutants, default=pollutants)

df = df[df["parameter"].isin(selected_pollutants)]

# === Title ===
st.title("🧪 Delhi AQI Dashboard")
st.markdown("Monitor pollution trends from Delhi’s AQI sensors. View pollutant distributions, time trends, and overall stats.")

# === Health Advisory Box ===
def get_health_advice(aqi_val):
    if aqi_val < 50:
        return "🟢 Good — Enjoy outdoor activities."
    elif aqi_val < 100:
        return "🟡 Moderate — Sensitive individuals should take care."
    elif aqi_val < 200:
        return "🟠 Poor — Consider reducing prolonged outdoor exertion."
    else:
        return "🔴 Hazardous — Avoid outdoor exposure, wear a mask."

st.subheader("📋 Health Advisory")
avg_pm25 = df[df["parameter"] == "pm25"]["value"].mean()
if pd.notna(avg_pm25):
    st.markdown(f"**PM2.5 Average: {avg_pm25:.1f} µg/m³** — {get_health_advice(avg_pm25)}")
else:
    st.info("PM2.5 data not available for current filters.")

# === Distribution Plot ===
st.subheader("📊 Pollutant Distribution")
if not df.empty:
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df, x="parameter", y="value", ax=ax)
    ax.set_ylabel("Concentration")
    ax.set_xlabel("Pollutant")
    plt.xticks(rotation=30)
    st.pyplot(fig)
else:
    st.warning("No data found for selected filters.")

# === Time Series ===
st.subheader("📈 Time Trend")
time_df = df.pivot_table(index="datetimelocal", columns="parameter", values="value", aggfunc="mean")
if not time_df.empty:
    fig2, ax2 = plt.subplots(figsize=(12, 4))
    time_df.plot(ax=ax2)
    ax2.set_ylabel("Concentration")
    ax2.set_xlabel("Time")
    plt.xticks(rotation=45)
    plt.title("Hourly Trends")
    st.pyplot(fig2)
else:
    st.warning("No time trend available.")

# === Correlation Heatmap ===
st.subheader("🌡️ Heatmap of Correlations")
heatmap_data = df.pivot_table(index="datetimelocal", columns="parameter", values="value", aggfunc="mean").dropna()
if not heatmap_data.empty:
    corr = heatmap_data.corr()
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax3)
    st.pyplot(fig3)
else:
    st.warning("Not enough data for heatmap.")

# === Stats ===
st.subheader("📌 Summary Statistics")
stats = df.groupby("parameter")["value"].agg(["mean", "max", "min", "count"]).round(2)
st.dataframe(stats)

# === Data Preview ===
st.subheader("📄 Raw AQI Data")
st.dataframe(df.reset_index(drop=True))

# === Download Button ===
st.download_button(
    label="📥 Download Filtered Data",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_aqi_data.csv",
    mime="text/csv"
)
