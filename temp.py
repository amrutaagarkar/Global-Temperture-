import streamlit as st
import pandas as pd
import io
import requests
import plotly.express as px
import zipfile

# -------------------------------------------------------
# APP TITLE
# -------------------------------------------------------
st.set_page_config(page_title="🌍 Global Temperature Dashboard", layout="wide")
st.title("🌡️ Global Temperature Dashboard (Google Drive ZIP Linked)")

# -------------------------------------------------------
# GOOGLE DRIVE DIRECT DOWNLOAD LINK
# -------------------------------------------------------
file_id = "1RT8dMSKj2123wY_BjELt_3LabFQL0GA4"   # your ZIP file ID
download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

# -------------------------------------------------------
# LOAD ZIP → EXTRACT CSV → LOAD DATAFRAME
# -------------------------------------------------------
@st.cache_data
def load_data(url):
    """Download ZIP from Google Drive and extract CSV inside it"""
    try:
        st.info("📥 Downloading ZIP from Google Drive...")
        response = requests.get(url)
        response.raise_for_status()

        content = response.content

        # ZIP file signature = PK
        if content[:2] != b'PK':
            st.error("❌ The file downloaded is NOT a ZIP file.")
            return None

        st.success("📦 ZIP file detected! Extracting CSV...")

        with zipfile.ZipFile(io.BytesIO(content)) as z:

            # find CSV inside ZIP
            csv_files = [f for f in z.namelist() if f.lower().endswith(".csv")]
            if not csv_files:
                st.error("❌ No CSV found inside ZIP.")
                return None

            csv_name = csv_files[0]
            st.info(f"📄 Found CSV inside ZIP: {csv_name}")

            with z.open(csv_name) as f:
                df = pd.read_csv(f, low_memory=False)
                return df

    except Exception as e:
        st.error(f"❌ Error loading ZIP/CSV: {e}")
        return None


# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------
df = load_data(download_url)

if df is None:
    st.warning("⚠️ No data loaded. Please check your file.")
    st.stop()


# -------------------------------------------------------
# DATA PREVIEW
# -------------------------------------------------------
st.success("✅ File loaded successfully!")
st.write("### 🔍 Preview of Data:")
st.dataframe(df.head())


# -------------------------------------------------------
# AUTO-DETECT KEY COLUMNS
# -------------------------------------------------------
date_col = None
temp_col = None
country_col = None

for c in df.columns:
    cl = c.lower()
    if "date" in cl or "dt" in cl:
        date_col = c
    elif "temp" in cl:
        temp_col = c
    elif "country" in cl:
        country_col = c

if not all([date_col, temp_col, country_col]):
    st.error("❌ Could not detect required columns (date, temp, country).")
    st.stop()

st.success(f"✅ Detected columns: **{date_col}**, **{temp_col}**, **{country_col}**")


# -------------------------------------------------------
# CLEANING
# -------------------------------------------------------
df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df["Year"] = df[date_col].dt.year
df = df.dropna(subset=[temp_col, country_col])


# -------------------------------------------------------
# SIDEBAR MENU
# -------------------------------------------------------
menu = st.sidebar.selectbox(
    "📊 Select Visualization",
    [
        "Global Temperature Trend",
        "Top 10 Hottest Countries",
        "Top 10 Coldest Countries",
        "Country-wise Temperature Trend",
        "Histogram of Global Temperatures"
    ]
)


# -------------------------------------------------------
# VISUALIZATIONS
# -------------------------------------------------------

# 1) Global Trend
if menu == "Global Temperature Trend":
    global_temp = df.groupby("Year")[temp_col].mean().reset_index()
    fig = px.line(global_temp, x="Year", y=temp_col,
                  title="🌡️ Global Average Temperature Over Time",
                  color_discrete_sequence=["red"])
    st.plotly_chart(fig, use_container_width=True)

# 2) Top 10 Hot Countries
elif menu == "Top 10 Hottest Countries":
    hot = df.groupby(country_col)[temp_col].mean().nlargest(10).reset_index()
    fig = px.bar(hot, x=temp_col, y=country_col, orientation="h",
                 title="🔥 Top 10 Hottest Countries",
                 color=temp_col, color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)

# 3) Top 10 Cold Countries
elif menu == "Top 10 Coldest Countries":
    cold = df.groupby(country_col)[temp_col].mean().nsmallest(10).reset_index()
    fig = px.bar(cold, x=temp_col, y=country_col, orientation="h",
                 title="❄️ Top 10 Coldest Countries",
                 color=temp_col, color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)

# 4) Country Trend
elif menu == "Country-wise Temperature Trend":
    country = st.selectbox("🌍 Select a Country", sorted(df[country_col].unique()))
    trend = df[df[country_col] == country].groupby("Year")[temp_col].mean().reset_index()

    fig = px.line(trend, x="Year", y=temp_col,
                  title=f"🌍 Temperature Trend of {country}",
                  color_discrete_sequence=["green"])
    st.plotly_chart(fig, use_container_width=True)

# 5) Histogram
elif menu == "Histogram of Global Temperatures":
    fig = px.histogram(df, x=temp_col, nbins=40,
                       title="📊 Distribution of Global Average Temperatures",
                       color_discrete_sequence=["royalblue"])
    st.plotly_chart(fig, use_container_width=True)
