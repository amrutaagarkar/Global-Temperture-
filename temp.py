# 🌍 Global Temperature Dashboard (Streamlit + Google Drive CSV)
# --------------------------------------------------------------

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
@st.cache_data
def load_data():
    # 🔗 Google Drive direct link (converted)
    drive_url = "https://drive.google.com/uc?id=1RT8dMSKj2123wY_BjELt_3LabFQL0GA4"

    df = pd.read_csv(drive_url)

    # Show column names for debugging
    st.write("🧾 CSV Columns Detected:", df.columns.tolist())

    # Try to detect the date column automatically
    possible_date_cols = ['dt', 'Date', 'date', 'timestamp', 'year']
    date_col = None
    for col in possible_date_cols:
        if col in df.columns:
            date_col = col
            break

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df['Year'] = df[date_col].dt.year
    else:
        st.warning("⚠️ No date column found — using row index as Year.")
        df['Year'] = range(1, len(df) + 1)

    # Clean missing data safely
    for col in ['AverageTemperature', 'Country']:
        if col not in df.columns:
            st.error(f"❌ Missing expected column: {col}")
            st.stop()

    df = df.dropna(subset=['AverageTemperature', 'Country'])
    return df


# Load data
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
    st.subheader("🌡️ Global Average Temperature Over Time")
    global_trend = df.groupby("Year")["AverageTemperature"].mean().reset_index()
    fig = px.line(global_trend, x="Year", y="AverageTemperature",
                  title="Global Temperature Trend Over the Years",
                  labels={"AverageTemperature": "Average Temperature (°C)"},
                  color_discrete_sequence=["red"])
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Top 10 Hottest Countries":
    st.subheader("🔥 Top 10 Hottest Countries (Average Temperature)")
    top_countries = df.groupby("Country")["AverageTemperature"].mean().nlargest(10).reset_index()
    fig = px.bar(top_countries, x="Country", y="AverageTemperature",
                 color="AverageTemperature", title="Top 10 Hottest Countries")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Top 10 Coldest Countries":
    st.subheader("❄️ Top 10 Coldest Countries (Average Temperature)")
    cold_countries = df.groupby("Country")["AverageTemperature"].mean().nsmallest(10).reset_index()
    fig = px.bar(cold_countries, x="Country", y="AverageTemperature",
                 color="AverageTemperature", title="Top 10 Coldest Countries")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Country-wise Temperature Trend":
    st.subheader("📈 Country-wise Temperature Trend")
    country = st.selectbox("Select a Country:", sorted(df["Country"].unique()))
    country_data = df[df["Country"] == country].groupby("Year")["AverageTemperature"].mean().reset_index()
    fig = px.line(country_data, x="Year", y="AverageTemperature",
                  title=f"Temperature Trend for {country}",
                  color_discrete_sequence=["blue"])
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Histogram of Global Temperatures":
    st.subheader("🌍 Distribution of Global Average Temperatures")
    fig = px.histogram(df, x="AverageTemperature", nbins=40,
                       title="Histogram of Global Temperatures",
                       color_discrete_sequence=["green"])
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👈 Use the sidebar to select a visualization.")
