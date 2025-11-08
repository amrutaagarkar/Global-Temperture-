import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
import io
import requests

st.title("🌍 Global Temperature Dashboard (Google Drive Linked)")

# ------------------------------------------------------
# 🔗 STEP 1: Load data from Google Drive ZIP or CSV
# ------------------------------------------------------
drive_link = "https://drive.google.com/file/d/1RT8dMSKj2123wY_BjELt_3LabFQL0GA4/view?usp=drive_link"

# Convert to direct-download link
try:
    file_id = drive_link.split("/d/")[1].split("/")[0]
    download_url = f"https://drive.google.com/uc?id={file_id}"
except Exception:
    st.error("❌ Invalid Google Drive link. Please provide a valid 'file/d/...' link.")
    st.stop()

@st.cache_data
def load_data(url):
    r = requests.get(url)
    if r.status_code != 200:
        st.error("❌ Could not fetch the file from Google Drive.")
        st.stop()

    content = io.BytesIO(r.content)

    # Try reading as ZIP first
    try:
        with zipfile.ZipFile(content, "r") as z:
            csv_name = [f for f in z.namelist() if f.endswith(".csv")][0]
            with z.open(csv_name) as f:
                df = pd.read_csv(f, low_memory=False, on_bad_lines='skip')
                return df
    except zipfile.BadZipFile:
        # Not a zip file — try normal CSV
        try:
            df = pd.read_csv(content, sep=None, engine='python', on_bad_lines='skip')
            return df
        except Exception as e:
            st.error(f"❌ Failed to read CSV: {e}")
            st.stop()

df = load_data(download_url)

# ------------------------------------------------------
# 🧹 STEP 2: Clean and prepare data
# ------------------------------------------------------
if 'dt' not in df.columns:
    st.warning("⚠️ 'dt' column (date) not found — please check your dataset headers!")
    st.write("Columns detected:", list(df.columns))
    st.stop()

# Convert date and clean up
df['dt'] = pd.to_datetime(df['dt'], errors='coerce')
df['Year'] = df['dt'].dt.year

if 'AverageTemperature' not in df.columns:
    possible_cols = [c for c in df.columns if 'temp' in c.lower()]
    st.warning(f"⚠️ 'AverageTemperature' column missing. Possible matches: {possible_cols}")
    st.stop()

if 'Country' not in df.columns:
    st.warning("⚠️ 'Country' column missing. Please check dataset structure.")
    st.stop()

df = df.dropna(subset=['AverageTemperature', 'Country'])

# ------------------------------------------------------
# 📊 STEP 3: Sidebar menu
# ------------------------------------------------------
menu = st.sidebar.selectbox(
    "Select Visualization:",
    [
        "Global Temperature Trend",
        "Top 10 Hottest Countries",
        "Top 10 Coldest Countries",
        "Country-wise Temperature Trend",
        "Histogram of Global Temperatures"
    ]
)

# ------------------------------------------------------
# 📈 STEP 4: Visualizations
# ------------------------------------------------------

# 1️⃣ Global Trend
if menu == "Global Temperature Trend":
    global_temp = df.groupby("Year")['AverageTemperature'].mean().reset_index()
    fig = px.line(global_temp, x='Year', y='AverageTemperature',
                  title='🌡️ Global Average Temperature Trend (Yearly)',
                  color_discrete_sequence=["firebrick"])
    st.plotly_chart(fig, use_container_width=True)

# 2️⃣ Top 10 Hottest
elif menu == "Top 10 Hottest Countries":
    hot = df.groupby("Country")['AverageTemperature'].mean().nlargest(10).reset_index()
    fig = px.bar(hot, x='AverageTemperature', y='Country', orientation='h',
                 title='🔥 Top 10 Hottest Countries', color='AverageTemperature',
                 color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

# 3️⃣ Top 10 Coldest
elif menu == "Top 10 Coldest Countries":
    cold = df.groupby("Country")['AverageTemperature'].mean().nsmallest(10).reset_index()
    fig = px.bar(cold, x='AverageTemperature', y='Country', orientation='h',
                 title='❄️ Top 10 Coldest Countries', color='AverageTemperature',
                 color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

# 4️⃣ Country Trend
elif menu == "Country-wise Temperature Trend":
    country = st.selectbox("🌎 Select Country", sorted(df['Country'].unique()))
    sub = df[df['Country'] == country].groupby("Year")['AverageTemperature'].mean().reset_index()
    fig = px.line(sub, x='Year', y='AverageTemperature',
                  title=f"🌍 Temperature Trend of {country}",
                  color_discrete_sequence=["green"])
    st.plotly_chart(fig, use_container_width=True)

# 5️⃣ Histogram
elif menu == "Histogram of Global Temperatures":
    fig = px.histogram(df, x='AverageTemperature', nbins=40,
                       title='📊 Global Temperature Distribution',
                       color_discrete_sequence=["royalblue"])
    st.plotly_chart(fig, use_container_width=True)
