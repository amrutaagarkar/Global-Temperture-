# 🌍 Global Temperature Dashboard - Streamlit Version
# ---------------------------------------------------
import pandas as pd
import plotly.express as px
import streamlit as st
import zipfile

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(page_title="Global Temperature Dashboard 🌍", layout="wide")

st.title("🌡️ Global Climate Change Interactive Dashboard")
st.markdown("Analyze global temperature trends, country patterns, and anomalies.")

# -----------------------------
# LOAD DATA
# -----------------------------
# ✅ Update this with your correct ZIP/CSV file path
zip_path = r"C:\Users\amrut\Downloads\GlobalLandTemperaturesByCity.csv (1).zip"

with zipfile.ZipFile(zip_path, 'r') as z:
    csv_name = [name for name in z.namelist() if name.endswith('.csv')][0]
    with z.open(csv_name) as f:
        df = pd.read_csv(f)

# Convert date column to datetime and extract year
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
# VISUALIZ
