import streamlit as st
import pandas as pd
import requests
import zipfile
import io

# ---------------------------------------------------
# STREAMLIT APP TITLE
# ---------------------------------------------------
st.set_page_config(page_title="Temperature Dashboard", layout="wide")
st.title("🌡️ Temperature Dataset Loader (Google Drive Supported)")

# ---------------------------------------------------
# INPUT: Google Drive File Link
# ---------------------------------------------------
drive_link = st.text_input(
    "📥 Enter your Google Drive CSV/ZIP link:",
    "https://drive.google.com/file/d/1rIv7ciWzHOmGjl6QPwIeDhChTwCuTS_n/view?usp=drive_link"
)

if st.button("Load Data"):
    try:
        # -------------------------------------------
        # Extract File ID
        # -------------------------------------------
        if "id=" in drive_link:
            file_id = drive_link.split("id=")[1]
        else:
            file_id = drive_link.split("/d/")[1].split("/")[0]

        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

        st.info("📥 Downloading file from Google Drive... Please wait...")

        response = requests.get(download_url)
        response.raise_for_status()
        content = response.content

        # -------------------------------------------
        # ZIP file
        # -------------------------------------------
        if content[:2] == b"PK":
            st.success("📦 ZIP file detected! Extracting CSV...")
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                csv_files = [f for f in z.namelist() if f.endswith(".csv")]
                if not csv_files:
                    st.error("❌ No CSV found in ZIP!")
                    st.stop()
                csv_name = csv_files[0]
                st.write(f"📄 Found CSV: **{csv_name}**")
                df = pd.read_csv(z.open(csv_name))

        # -------------------------------------------
        # CSV file
        # -------------------------------------------
        else:
            st.success("📄 CSV file detected! Loading...")
            df = pd.read_csv(io.BytesIO(content))

        # -------------------------------------------
        # SHOW DATA + COLUMN NAMES
        # -------------------------------------------
        st.success("✅ File loaded successfully!")
        st.write("### 🔍 First 5 Rows:")
        st.dataframe(df.head())

        st.write("### 📌 Column Names Detected:")
        st.code(list(df.columns))

        st.warning("⚠️ Send me these column names so I can finish the dashboard.")

    except Exception as e:
        st.error(f"❌ Error: {e}")
