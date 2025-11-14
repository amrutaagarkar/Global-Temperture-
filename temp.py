import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
import io
import requests

st.set_page_config(page_title="🌍 Temperature Dashboard (Google Drive)", layout="wide")
st.title("🌡️ Global Temperature Dashboard ")


# ------------------------------------------------------
# ENTER YOUR GOOGLE DRIVE FILE ID HERE
# ------------------------------------------------------
file_id = "1RT8dMSKj2123wY_BjELt_3LabFQL0GA4"   # <-- CHANGE THIS
download_url = f"https://drive.google.com/uc?export=download&id={file_id}"


# ------------------------------------------------------
# LOAD ZIP OR CSV FROM GOOGLE DRIVE
# ------------------------------------------------------
@st.cache_data
def load_data_from_gdrive(url):
    try:
        st.info("📥 Downloading file from Google Drive...")
        response = requests.get(url)
        response.raise_for_status()
        content = response.content

        # Is it ZIP?
        if content[:2] == b'PK':
            st.success("📦 ZIP file detected! Extracting...")
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                csv_files = [f for f in z.namelist() if f.endswith(".csv")]
                if not csv_files:
                    st.error("❌ No CSV found inside ZIP.")
                    return None
                csv_name = csv_files[0]
                st.info(f"Found CSV: {csv_name}")
                with z.open(csv_name) as f:
                    df = pd.read_csv(f)
                    return df
        else:
            st.success("📄 CSV file detected! Loading...")
            return pd.read_csv(io.BytesIO(content))

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


# ------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------
df = load_data_from_gdrive(download_url)

if df is None:
    st.stop()

st.success("✅ File loaded successfully!")
st.dataframe(df.head())


# ------------------------------------------------------
# CLEAN DATA
# ------------------------------------------------------
df.columns = [c.strip() for c in df.columns]

date_col = next((c for c in df.columns if "dt" in c.lower() or "date" in c.lower()), None)
temp_col = next((c for c in df.columns if "temp" in c.lower()), None)
country_col = next((c for c in df.columns if "country" in c.lower()), None)

if not (date_col and temp_col and country_col):
    st.error("❌ Required columns not found.")
    st.stop()

df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df["Year"] = df[date_col].dt.year
df = df.dropna(subset=[temp_col, country_col])


# ------------------------------------------------------
# SIDEBAR MENU
# ------------------------------------------------------
menu = st.sidebar.selectbox("📊 Select Visualization", [
    "Global Temperature Trend",
    "Top 10 Hottest Countries",
    "Top 10 Coldest Countries",
    "Country-wise Temperature Trend",
    "Histogram of Global Temperatures",
])


# ------------------------------------------------------
# VISUALIZATIONS
# ------------------------------------------------------

# 1) Global Trend
if menu == "Global Temperature Trend":
    global_temp = df.groupby("Year")[temp_col].mean().reset_index()
    fig = px.line(global_temp, x="Year", y=temp_col, title="🌡️ Global Temperature Trend")
    st.plotly_chart(fig, use_container_width=True)

# 2) Top 10 Hottest Countries
elif menu == "Top 10 Hottest Countries":
    hot = df.groupby(country_col)[temp_col].mean().nlargest(10).reset_index()
    fig = px.bar(hot, x=temp_col, y=country_col, orientation="h",
                 title="🔥 Top 10 Hottest Countries")
    st.plotly_chart(fig, use_container_width=True)

# 3) Top 10 Coldest
elif menu == "Top 10 Coldest Countries":
    cold = df.groupby(country_col)[temp_col].mean().nsmallest(10).reset_index()
    fig = px.bar(cold, x=temp_col, y=country_col, orientation="h",
                 title="❄️ Top 10 Coldest Countries")
    st.plotly_chart(fig, use_container_width=True)

# 4) Country Trend
elif menu == "Country-wise Temperature Trend":
    country = st.selectbox("🌍 Select Country", sorted(df[country_col].unique()))
    trend = df[df[country_col] == country].groupby("Year")[temp_col].mean().reset_index()
    fig = px.line(trend, x="Year", y=temp_col, title=f"Temperature Trend – {country}")
    st.plotly_chart(fig, use_container_width=True)

# 5) Histogram
elif menu == "Histogram of Global Temperatures":
    fig = px.histogram(df, x=temp_col, nbins=40,
                       title="📊 Distribution of Global Temperatures")
    st.plotly_chart(fig, use_container_width=True)
