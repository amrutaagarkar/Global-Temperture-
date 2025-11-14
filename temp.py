# ---------------------------------------------------------
# 🌍 Global Temperature Dashboard (Streamlit Version)
# Loads CSV automatically from Google Drive ZIP
# ---------------------------------------------------------

import streamlit as st
import pandas as pd
import requests
import zipfile
import io
import plotly.express as px

st.set_page_config(page_title="Global Temperature Dashboard", layout="wide")

# ----------------------------
# 1) Convert Google Drive link
# ----------------------------
def get_drive_download_url(url):
    # Extract file ID
    file_id = url.split("/d/")[1].split("/")[0]
    return f"https://drive.google.com/uc?export=download&id={file_id}"

# ----------------------------
# 2) Download + Extract CSV
# ----------------------------
@st.cache_data
def load_csv_from_drive_zip(drive_link):
    st.info("📥 Downloading file from Google Drive...")

    download_url = get_drive_download_url(drive_link)
    r = requests.get(download_url)

    if r.status_code != 200:
        st.error("❌ Failed to download file. Check your Google Drive link.")
        return None

    st.success("📦 File downloaded! Extracting ZIP...")

    z = zipfile.ZipFile(io.BytesIO(r.content))

    # Find CSV in ZIP
    csv_name = None
    for f in z.namelist():
        if f.endswith(".csv"):
            csv_name = f
            break

    if not csv_name:
        st.error("❌ No CSV found inside ZIP file!")
        return None

    df = pd.read_csv(z.open(csv_name))

    # required columns
    expected = ['dt', 'AverageTemperature', 'AverageTemperatureUncertainty', 'Country']
    df = df[expected]

    df["dt"] = pd.to_datetime(df["dt"])

    return df


# ----------------------------
# 3) Load user-provided Drive link
# ----------------------------
st.title("🌡️ Global Temperature Dashboard (Streamlit)")
st.write("Loads data directly from your Google Drive ZIP file")

drive_link = st.text_input(
    "Paste your Google Drive ZIP file link:",
    "https://drive.google.com/file/d/1rIv7ciWzHOmGjl6QPwIeDhChTwCuTS_n/view?usp=drive_link"
)

if drive_link:
    df = load_csv_from_drive_zip(drive_link)

    if df is not None:
        st.success("✅ Data loaded successfully!")

        # ----------------------------
        # Sidebar filters
        # ----------------------------
        st.sidebar.header("Filters")

        countries = sorted(df["Country"].dropna().unique())
        selected_country = st.sidebar.selectbox("Select Country", countries, index=countries.index("India"))

        # ----------------------------
        # Filtered data
        # ----------------------------
        dff = df[df["Country"] == selected_country]

        # ----------------------------
        # Line Chart
        # ----------------------------
        st.subheader(f"📈 Average Temperature Over Time — {selected_country}")

        fig = px.line(
            dff,
            x="dt",
            y="AverageTemperature",
            labels={"dt": "Year", "AverageTemperature": "Average Temperature (°C)"},
        )

        st.plotly_chart(fig, use_container_width=True)

        # ----------------------------
        # Show raw data
        # ----------------------------
        with st.expander("📄 Show Raw Data Table"):
            st.dataframe(dff)
