import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
import requests
import io

st.title("🌍 Global Temperature & Climate Change Dashboard")

# --------------------------
# Custom CSS Styling
# --------------------------
st.markdown("""
<style>

/* Change main background */
.main {
    background-color: #F7FBFF;
}

/* Title styling */
h1 {
    color: #004AAD;
    text-align: center;
    font-weight: 700;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #E9F0FF;
    border-right: 2px solid #BDD4FF;
}

/* All subheaders */
h2, h3 {
    color: #003D7A;
}

/* Improve chart layout spacing */
.block-container {
    padding-top: 1.2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Dropdown styling */
.stSelectbox div div {
    background-color: white;
    border-radius: 8px;
}

/* Fix Streamlit widget font */
html, body, p, span, label {
    font-family: 'Segoe UI', sans-serif;
    font-size: 15px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------
# Load ZIP from Google Drive (Silent Mode)
# --------------------------
drive_url = "https://drive.google.com/uc?export=download&id=1rIv7ciWzHOmGjl6QPwIeDhChTwCuTS_n"

try:
    response = requests.get(drive_url)
    response.raise_for_status()

    z = zipfile.ZipFile(io.BytesIO(response.content))
    csv_name = [f for f in z.namelist() if f.endswith(".csv")][0]
    df = pd.read_csv(z.open(csv_name), encoding="latin1")

except Exception as e:
    st.error(f"❌ Error loading CSV: {e}")
    st.stop()

# --------------------------
# Clean Data
# --------------------------
df["dt"] = pd.to_datetime(df["dt"], errors="ignore")
df["Year"] = df["dt"].dt.year
df = df.dropna(subset=["AverageTemperature", "Country"])

# --------------------------
# Sidebar Menu
# --------------------------
menu = st.sidebar.selectbox(
    "📊 Select View",
    [
        "Top 10 Hottest Countries",
        "Top 10 Coldest Countries",
        "Country-wise Temperature Trend",
        "Histogram of Global Temperatures",
    ]
)
# Stop execution until user selects an option
if menu == "-- Select View --":
    st.info("👈 Please select a chart from the sidebar.")
    st.stop()

# --------------------------
# Colors
# --------------------------
colors = {
    "hot": "#FF0000",
    "cold": "#0077FF",
    "line": "#2ECC71",
    "hist": "#8E44AD",
}

# --------------------------
# Views
# --------------------------
if menu == "Top 10 Hottest Countries":
    data = df.groupby("Country")["AverageTemperature"].mean().nlargest(10).reset_index()
    st.subheader("🔥 Top 10 Hottest Countries")
    st.plotly_chart(px.bar(
        data, x="AverageTemperature", y="Country",
        orientation="h", color_discrete_sequence=[colors["hot"]]
    ))

elif menu == "Top 10 Coldest Countries":
    data = df.groupby("Country")["AverageTemperature"].mean().nsmallest(10).reset_index()
    st.subheader("❄️ Top 10 Coldest Countries")
    st.plotly_chart(px.bar(
        data, x="AverageTemperature", y="Country",
        orientation="h", color_discrete_sequence=[colors["cold"]]
    ))

elif menu == "Country-wise Temperature Trend":
    country = st.selectbox("Select Country", sorted(df["Country"].unique()))
    data = df[df["Country"] == country].groupby("Year")["AverageTemperature"].mean().reset_index()
    st.subheader(f"🌎 Temperature Trend — {country}")
    st.plotly_chart(px.line(
        data, x="Year", y="AverageTemperature",
        color_discrete_sequence=[colors["line"]]
    ))

elif menu == "Histogram of Global Temperatures":
    st.subheader("📊 Temperature Distribution")
    st.plotly_chart(px.histogram(
        df, x="AverageTemperature",
        nbins=40, color_discrete_sequence=[colors["hist"]]
    ))
