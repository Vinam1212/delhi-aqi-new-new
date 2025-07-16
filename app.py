import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Delhi AQI Dashboard", layout="wide")

# === Load AQI Data ===
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
selected_location = st.sidebar.selectbox(
    "Select Location",
    locations,
    index=locations.index("Chandni Chowk, Delhi - IITM") if "Chandni Chowk, Delhi - IITM" in locations else 0
)

df = df[df["location_name"] == selected_location]

pollutants = sorted(df["parameter"].unique())
selected_pollutants = st.sidebar.multiselect("Select Pollutants", pollutants, default=pollutants)

# === Filter data ===
df = df[df["parameter"].isin(selected_pollutants)]

# === App Title ===
st.title("🧪 Delhi Air Quality Dashboard")
st.markdown("This dashboard visualizes pollution levels from AQI monitoring stations in Delhi.")

# === Category-wise Distribution ===
st.subheader("📊 Pollutant Concentration Distribution")
if not df.empty:
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df, x="parameter", y="value", ax=ax)
    ax.set_ylabel("Concentration")
    ax.set_xlabel("Pollutant")
    plt.xticks(rotation=30)
    st.pyplot(fig)
else:
    st.warning("No data found for selected filters.")

# === Time Series Plot ===
st.subheader("📈 Time Trend of Pollutants")
time_df = df.pivot_table(index="datetimelocal", columns="parameter", values="value", aggfunc="mean")

if not time_df.empty:
    fig2, ax2 = plt.subplots(figsize=(12, 4))
    time_df.plot(ax=ax2)
    ax2.set_ylabel("Concentration")
    ax2.set_xlabel("Time")
    plt.xticks(rotation=45)
    plt.title("Hourly Concentration Trend")
    st.pyplot(fig2)
else:
    st.warning("Not enough data to show time trends.")

# === Summary Statistics ===
st.subheader("📌 Summary Statistics")
sum_stats = df.groupby("parameter")["value"].agg(["mean", "max", "min", "count"]).round(2)
st.dataframe(sum_stats)

# === Data Preview ===
st.subheader("📄 Full AQI Raw Data Preview")
st.dataframe(df.reset_index(drop=True))

# === CSV Download ===
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_aqi_data.csv",
    mime="text/csv"
)
