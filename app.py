import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Title and Description
st.set_page_config(page_title="Delhi AQI Dashboard", layout="centered")
st.markdown("### 🟢 Delhi AQI Dashboard – Live Data from OpenAQ")
st.caption("Created by Vinam Jain | Data via OpenAQ")

# Your API Key
API_KEY = "b5e603105ac2e6a269e65dd8b3659d91eadc422e602b8becd58c5ee70b867907"

# Define headers
headers = {
    "Accept": "application/json",
    "X-API-Key": API_KEY
}

# API call to get latest measurements in Delhi
params = {
    "country": "IN",
    "city": "Delhi",
    "limit": 100,
    "sort": "desc",
    "order_by": "datetime"
}
url = "https://api.openaq.org/v3/measurements"

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if "results" in data and len(data["results"]) > 0:
        df = pd.DataFrame(data["results"])
        df["datetime"] = pd.to_datetime(df["date"]["utc"])
        df = df[["location", "parameter", "value", "unit", "datetime"]]

        st.success(f"Fetched {len(df)} recent measurements for Delhi.")
        st.dataframe(df)

        # Optional: Health tip based on PM2.5
        pm25 = df[df["parameter"] == "pm25"]
        if not pm25.empty:
            avg_pm25 = pm25["value"].mean()
            st.markdown(f"**Average PM2.5**: {avg_pm25:.2f} µg/m³")

            if avg_pm25 <= 50:
                st.success("Air quality is good.")
            elif avg_pm25 <= 100:
                st.warning("Air quality is moderate.")
            else:
                st.error("Air quality is poor. Consider wearing a mask.")
    else:
        st.warning("No AQI data available for Delhi right now. Try again later.")

except requests.exceptions.RequestException as e:
    st.error(f"Failed to fetch data: {e}")

# Footer
st.markdown("---")
st.markdown("📘 This is part of a high school project on Delhi's air quality and environmental data justice.")
st.markdown("[🔗 OpenAQ API](https://docs.openaq.org/)")



