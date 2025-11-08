# 🌍 Global Temperature Dashboard - Streamlit Version (Google Drive CSV)
# --------------------------------------------------------------------
import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(page_title="Global Temperature Dashboard 🌍", layout="wide")

st.title("🌡️ Global Climate Change Interactive Dashboard")
st.markdown("Analyze global temperature trends, country patterns, and anomalies.")

# -----------------------------
# LOAD DATA FROM GOOGLE DRIVE
# -----------------------------
# Your Google Drive direct link
drive_url = "https://drive.google.com/uc?id=1RT8dMSKj2123wY_BjELt_3LabFQL0GA4"

@st.cache_data
def load_data():
    df = pd.read_csv(drive_url)
    df['dt'] = pd.to_datetime(df['dt'], errors='coerce')
    df['Year'] = df['dt'].dt.year
    df = df.dropna(subset=['AverageTemperature', 'Country'])
    return df

df = load_data()

# -----------------------------
# SIDEBAR MENU
# -----------------------------
menu = st.sidebar.selectbox(
    "📊 Choose a Visualization:",
    [
        "Select...",
        "Global Temperature Trend",
        "Top 10 Hottest Countries",
        "Top 10 Coldest Countries",
        "Country-wise Temperature Trend",
        "Histogram of Global Temperatures"
    ]
)

# -----------------------------
# VISUALIZATIONS
# -----------------------------
if menu == "Global Temperature Trend":
    st.subheader("🌍 Global Average Temperature Over Time")
    global_temp = df.groupby("Year")["AverageTemperature"].mean().reset_index()
    fig = px.line(global_temp, x="Year", y="AverageTemperature",
                  title="Global Average Temperature Over Time",
                  labels={"AverageTemperature": "Avg Temperature (°C)"})
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Top 10 Hottest Countries":
    st.subheader("🔥 Top 10 Hottest Countries (Average Across All Years)")
    hot_countries = df.groupby("Country")["AverageTemperature"].mean().nlargest(10).reset_index()
    fig = px.bar(hot_countries, x="Country", y="AverageTemperature",
                 color="AverageTemperature", title="Top 10 Hottest Countries")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Top 10 Coldest Countries":
    st.subheader("❄️ Top 10 Coldest Countries (Average Across All Years)")
    cold_countries = df.groupby("Country")["AverageTemperature"].mean().nsmallest(10).reset_index()
    fig = px.bar(cold_countries, x="Country", y="AverageTemperature",
                 color="AverageTemperature", title="Top 10 Coldest Countries")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Country-wise Temperature Trend":
    st.subheader("📈 Country-wise Temperature Trend")
    countries = df["Country"].unique()
    country = st.selectbox("Select a Country:", sorted(countries))
    country_data = df[df["Country"] == country]
    fig = px.line(country_data, x="Year", y="AverageTemperature",
                  title=f"Average Temperature Over Time - {country}")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Histogram of Global Temperatures":
    st.subheader("🌡️ Histogram of Global Temperatures")
    fig = px.histogram(df, x="AverageTemperature", nbins=50,
                       title="Distribution of Global Temperatures")
    st.plotly_chart(fig, use_container_width=True)

