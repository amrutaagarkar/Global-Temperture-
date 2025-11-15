import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile

# -----------------------------
# LOAD DATA
# -----------------------------
st.title("🌍 Global Temperature Dashboard")

zip_path = r"C:\Users\amrut\Downloads\GlobalLandTemperaturesByCity.csv (1).zip"
with zipfile.ZipFile(zip_path, 'r') as z:

    csv_name = z.namelist()[0]
    df = pd.read_csv(z.open(csv_name))

# Clean data
df['dt'] = pd.to_datetime(df['dt'], errors='coerce')
df['Year'] = df['dt'].dt.year
df = df.dropna(subset=['AverageTemperature', 'Country'])

# -----------------------------
# SIDEBAR MENU
# -----------------------------
st.sidebar.title("📊 Select a Visualization")
choice = st.sidebar.selectbox(
    "Choose:",
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
# 1️⃣ GLOBAL TEMPERATURE TREND
# -----------------------------
if choice == "Global Temperature Trend":
    st.subheader("🌡️ Global Average Temperature Trend")
    global_temp = df.groupby("Year")['AverageTemperature'].mean().reset_index()

    fig = px.line(
        global_temp,
        x='Year',
        y='AverageTemperature',
        title='Global Average Temperature Trend'
    )
    st.plotly_chart(fig)

# -----------------------------
# 2️⃣ TOP 10 HOTTEST COUNTRIES
# -----------------------------
elif choice == "Top 10 Hottest Countries":
    st.subheader("🔥 Top 10 Hottest Countries")
    hot = df.groupby("Country")['AverageTemperature'].mean().nlargest(10).reset_index()

    fig = px.bar(
        hot,
        x='AverageTemperature',
        y='Country',
        orientation='h',
        title='Top 10 Hottest Countries'
    )
    st.plotly_chart(fig)

# -----------------------------
# 3️⃣ TOP 10 COLDEST COUNTRIES
# -----------------------------
elif choice == "Top 10 Coldest Countries":
    st.subheader("❄️ Top 10 Coldest Countries")
    cold = df.groupby("Country")['AverageTemperature'].mean().nsmallest(10).reset_index()

    fig = px.bar(
        cold,
        x='AverageTemperature',
        y='Country',
        orientation='h',
        title='Top 10 Coldest Countries'
    )
    st.plotly_chart(fig)

# -----------------------------
# 4️⃣ COUNTRY-WISE TEMPERATURE TREND
# -----------------------------
elif choice == "Country-wise Temperature Trend":
    st.subheader("🌎 Country-wise Temperature Trend")

    countries = sorted(df['Country'].unique())
    selected = st.selectbox("Select a Country:", countries)

    country_df = df[df['Country'] == selected]
    trend = country_df.groupby('Year')['AverageTemperature'].mean().reset_index()

    fig = px.line(
        trend,
        x='Year',
        y='AverageTemperature',
        title=f"Temperature Trend - {selected}"
    )
    st.plotly_chart(fig)

# -----------------------------
# 5️⃣ HISTOGRAM OF GLOBAL TEMPERATURES
# -----------------------------
elif choice == "Histogram of Global Temperatures":
    st.subheader("📊 Distribution of Global Temperatures")

    fig = px.histogram(
        df,
        x='AverageTemperature',
        nbins=40,
        title='Distribution of Global Temperatures'
    )
    st.plotly_chart(fig)
