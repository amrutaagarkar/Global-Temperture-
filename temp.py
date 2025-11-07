# 🌍 Global Temperature Dashboard - Streamlit Version
# ---------------------------------------------------
import pandas as pd
import plotly.express as px
import streamlit as st
import zipfile
import io

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(page_title="Global Temperature Dashboard 🌍", layout="wide")

st.title("🌡️ Global Climate Change Interactive Dashboard")
st.markdown("Analyze global temperature trends, country patterns, and anomalies.")

# -----------------------------
# LOAD DATA
# -----------------------------
# ✅ Update your ZIP or CSV path here
zip_path = r"C:\Users\amrut\Downloads\GlobalLandTemperaturesByCity.csv (1).zip"

# Read CSV from ZIP safely
with zipfile.ZipFile(zip_path, 'r') as z:
    csv_name = [name for name in z.namelist() if name.endswith('.csv')][0]
    with z.open(csv_name) as f:
        df = pd.read_csv(f)

# Convert date column
df['dt'] = pd.to_datetime(df['dt'], errors='coerce')
df['Year'] = df['dt'].dt.year
df = df.dropna(subset=['AverageTemperature', 'Country'])

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

# 1️⃣ GLOBAL TEMPERATURE TREND
if menu == "Global Temperature Trend":
    st.subheader("🌡️ Global Average Temperature Trend (Yearly)")
    global_temp = df.groupby("Year")['AverageTemperature'].mean().reset_index()
    fig = px.line(
        global_temp,
        x='Year',
        y='AverageTemperature',
        title='Global Average Temperature Trend',
        color_discrete_sequence=["firebrick"]
    )
    st.plotly_chart(fig, use_container_width=True)

# 2️⃣ TOP 10 HOTTEST COUNTRIES
elif menu == "Top 10 Hottest Countries":
    st.subheader("🔥 Top 10 Hottest Countries (Average Temperature)")
    hot = (
        df.groupby("Country")['AverageTemperature']
        .mean()
        .nlargest(10)
        .reset_index()
    )
    fig = px.bar(
        hot,
        x='AverageTemperature',
        y='Country',
        orientation='h',
        color='AverageTemperature',
        color_continuous_scale='Reds',
        title='Top 10 Hottest Countries'
    )
    st.plotly_chart(fig, use_container_width=True)

# 3️⃣ TOP 10 COLDEST COUNTRIES
elif menu == "Top 10 Coldest Countries":
    st.subheader("❄️ Top 10 Coldest Countries (Average Temperature)")
    cold = (
        df.groupby("Country")['AverageTemperature']
        .mean()
        .nsmallest(10)
        .reset_index()
    )
    fig = px.bar(
        cold,
        x='AverageTemperature',
        y='Country',
        orientation='h',
        color='AverageTemperature',
        color_continuous_scale='Blues',
        title='Top 10 Coldest Countries'
    )
    st.plotly_chart(fig, use_container_width=True)

# 4️⃣ COUNTRY-WISE TEMPERATURE TREND
elif menu == "Country-wise Temperature Trend":
    st.subheader("🌍 Country-wise Temperature Trend")
    country_list = sorted(df['Country'].unique())
    selected_country = st.selectbox("Select a Country:", country_list)

    country_df = df[df['Country'] == selected_country]
    trend = country_df.groupby('Year')['AverageTemperature'].mean().reset_index()

    fig = px.line(
        trend,
        x='Year',
        y='AverageTemperature',
        title=f'Temperature Trend of {selected_country}',
        color_discrete_sequence=["green"]
    )
    st.plotly_chart(fig, use_container_width=True)

# 5️⃣ HISTOGRAM OF GLOBAL TEMPERATURES
elif menu == "Histogram of Global Temperatures":
    st.subheader("📊 Distribution of Global Average Temperatures")
    fig =
