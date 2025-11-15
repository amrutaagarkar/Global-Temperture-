import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile

st.set_page_config(page_title="Global Climate Dashboard", layout="wide")
st.title("🌍 Global Temperature & Climate Change Dashboard")

# -------- Upload ZIP --------
uploaded = st.file_uploader("📥 Upload ZIP containing CSV", type="zip")
if not uploaded:
    st.stop()

try:
    z = zipfile.ZipFile(uploaded)
    df = pd.read_csv(z.open(z.namelist()[0]))
except Exception as e:
    st.error(f"ZIP Read Error: {e}")
    st.stop()

# -------- Clean Data --------
df['dt'] = pd.to_datetime(df['dt'], errors='coerce')
df = df.dropna(subset=['AverageTemperature', 'Country'])
df['Year'] = df['dt'].dt.year

# -------- Sidebar --------
st.sidebar.header("📊 Menu")
choice = st.sidebar.selectbox(
    "Choose View:",
    ["Global Trend", "Top 10 Hot Countries", "Top 10 Cold Countries",
     "Country Trend", "Temperature Histogram"]
)

smooth = st.sidebar.checkbox("Smooth Line (Rolling Mean)")
animate = st.sidebar.checkbox("Enable Animation")

# -------- Reusable Plot Function --------
def line_plot(data, title):
    if smooth:
        data['Smooth'] = data['AverageTemperature'].rolling(5, min_periods=1).mean()
        y = 'Smooth'
    else:
        y = 'AverageTemperature'

    if animate:
        return px.line(data, x='Year', y=y, title=title, animation_frame='Year')
    else:
        return px.line(data, x='Year', y=y, title=title)

# -------- VIEWS --------
if choice == "Global Trend":
    g = df.groupby("Year")['AverageTemperature'].mean().reset_index()
    st.plotly_chart(line_plot(g, "🌡 Global Temperature Trend"))

elif choice == "Top 10 Hot Countries":
    hot = df.groupby("Country")['AverageTemperature'].mean().nlargest(10).reset_index()
    st.plotly_chart(px.bar(hot, x='AverageTemperature', y='Country', orientation='h',
                           title="🔥 Top 10 Hottest Countries"))

elif choice == "Top 10 Cold Countries":
    cold = df.groupby("Country")['AverageTemperature'].mean().nsmallest(10).reset_index()
    st.plotly_chart(px.bar(cold, x='AverageTemperature', y='Country', orientation='h',
                           title="❄ Top 10 Coldest Countries"))

elif choice == "Country Trend":
    country = st.selectbox("Select Country:", sorted(df['Country'].unique()))
    c = df[df['Country'] == country].groupby('Year')['AverageTemperature'].mean().reset_index()
    st.plotly_chart(line_plot(c, f"🌎 Temperature Trend — {country}"))

elif choice == "Temperature Histogram":
    st.plotly_chart(px.histogram(df, x='AverageTemperature', nbins=40,
                                 title="📊 Global Temperature Distribution"))

