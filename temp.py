import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
import io

st.title("🌍 Global Temperature Dashboard")

# ----------------------------------
# UPLOAD ZIP FROM USER
# ----------------------------------
uploaded = st.file_uploader("📥 Upload ZIP file containing CSV", type=["zip"])

if uploaded is None:
    st.warning("Please upload a ZIP file to continue.")
    st.stop()

# Read ZIP file
try:
    z = zipfile.ZipFile(uploaded)
    csv_name = z.namelist()[0]       # first CSV inside ZIP
    df = pd.read_csv(z.open(csv_name))
except Exception as e:
    st.error(f"Error reading ZIP file: {e}")
    st.stop()

# ----------------------------------
# CLEAN DATA
# ----------------------------------
df['dt'] = pd.to_datetime(df['dt'], errors='coerce')
df['Year'] = df['dt'].dt.year
df = df.dropna(subset=['AverageTemperature', 'Country'])

# ----------------------------------
# SIDEBAR SELECTION
# ----------------------------------
st.sidebar.title("📊 Visualization Menu")
choice = st.sidebar.selectbox(
    "Choose view:",
    [
        "Select...",
        "Global Temperature Trend",
        "Top 10 Hottest Countries",
        "Top 10 Coldest Countries",
        "Country-wise Temperature Trend",
        "Histogram of Global Temperatures"
    ]
)

# ----------------------------------
# GRAPHS
# ----------------------------------

if choice == "Global Temperature Trend":
    st.subheader("🌡️ Global Temperature Trend")
    global_temp = df.groupby("Year")['AverageTemperature'].mean().reset_index()
    fig = px.line(global_temp, x='Year', y='AverageTemperature')
    st.plotly_chart(fig)

elif choice == "Top 10 Hottest Countries":
    st.subheader("🔥 Top 10 Hottest Countries")
    hot = df.groupby("Country")['AverageTemperature'].mean().nlargest(10).reset_index()
    fig = px.bar(hot, x='AverageTemperature', y='Country', orientation='h')
    st.plotly_chart(fig)

elif choice == "Top 10 Coldest Countries":
    st.subheader("❄️ Top 10 Coldest Countries")
    cold = df.groupby("Country")['AverageTemperature'].mean().nsmallest(10).reset_index()
    fig = px.bar(cold, x='AverageTemperature', y='Country', orientation='h')
    st.plotly_chart(fig)

elif choice == "Country-wise Temperature Trend":
    st.subheader("🌎 Country-wise Trend")
    countries = sorted(df['Country'].unique())
    selected = st.selectbox("Select Country:", countries)
    country_df = df[df['Country'] == selected]
    trend = country_df.groupby('Year')['AverageTemperature'].mean().reset_index()
    fig = px.line(trend, x='Year', y='AverageTemperature', title=selected)
    st.plotly_chart(fig)

elif choice == "Histogram of Global Temperatures":
    st.subheader("📊 Temperature Distribution")
    fig = px.histogram(df, x='AverageTemperature', nbins=40)
    st.plotly_chart(fig)
