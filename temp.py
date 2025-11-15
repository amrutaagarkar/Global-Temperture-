import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile

st.title("🌍 Global Temperature & Climate Change Dashboard")

# --------------------------
# File Upload
# --------------------------
uploaded = st.file_uploader("📥 Upload ZIP file containing CSV", type="zip")
if not uploaded:
    st.warning("Please upload a ZIP file to continue.")
    st.stop()

try:
    with zipfile.ZipFile(uploaded) as z:
        df = pd.read_csv(z.open(z.namelist()[0]))
except Exception as e:
    st.error(f"Error reading ZIP file: {e}")
    st.stop()

# --------------------------
# Clean Data
# --------------------------
df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
df["Year"] = df["dt"].dt.year
df = df.dropna(subset=["AverageTemperature", "Country"])

# --------------------------
# Sidebar Menu
# --------------------------
menu = st.sidebar.selectbox(
    "📊 Select View:",
    [
        "Global Temperature Trend",
        "Top 10 Hottest Countries",
        "Top 10 Coldest Countries",
        "Country-wise Temperature Trend",
        "Histogram of Global Temperatures",
    ],
)

# --------------------------
# Helper Functions
# --------------------------
def line_chart(data, title):
    st.subheader(title)
    st.plotly_chart(px.line(data, x="Year", y="AverageTemperature"), use_container_width=True)

def bar_chart(data, title):
    st.subheader(title)
    st.plotly_chart(
        px.bar(data, x="AverageTemperature", y="Country", orientation="h"),
        use_container_width=True,
    )

# --------------------------
# Views
# --------------------------
if menu == "Global Temperature Trend":
    global_temp = df.groupby("Year")["AverageTemperature"].mean().reset_index()
    line_chart(global_temp, "🌡️ Global Temperature Trend")

elif menu == "Top 10 Hottest Countries":
    hot = df.groupby("Country")["AverageTemperature"].mean().nlargest(10).reset_index()
    bar_chart(hot, "🔥 Top 10 Hottest Countries")

elif menu == "Top 10 Coldest Countries":
    cold = df.groupby("Country")["AverageTemperature"].mean().nsmallest(10).reset_index()
    bar_chart(cold, "❄️ Top 10 Coldest Countries")

elif menu == "Country-wise Temperature Trend":
    st.subheader("🌎 Country-wise Temperature Trend")
    country = st.selectbox("Select Country:", sorted(df["Country"].unique()))
    cdf = df[df["Country"] == country].groupby("Year")["AverageTemperature"].mean().reset_index()
    line_chart(cdf, f"Temperature Trend — {country}")

elif menu == "Histogram of Global Temperatures":
    st.subheader("📊 Temperature Distribution")
    st.plotly_chart(px.histogram(df, x="AverageTemperature", nbins=40), use_container_width=True)
