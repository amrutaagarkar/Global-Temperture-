import streamlit as st
import pandas as pd
import zipfile
import io
import requests
import plotly.express as px

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.set_page_config(page_title="Global Temperature Dashboard", layout="wide")
st.title("🌡️ Global Temperature Dashboard")
st.write("Interactive Temperature Analysis using Streamlit")

st.header("📥 Load Dataset From Google Drive")

# ---------------------------------------------------
# GOOGLE DRIVE LINK INPUT
# ---------------------------------------------------
gdrive_url = st.text_input("https://drive.google.com/file/d/1rIv7ciWzHOmGjl6QPwIeDhChTwCuTS_n/view?usp=drive_link")

df = None

if st.button("Load Data"):
    try:
        # Extract file ID
        if "id=" in gdrive_url:
            file_id = gdrive_url.split("id=")[1]
        else:
            file_id = gdrive_url.split("/d/")[1].split("/")[0]

        # Direct download URL
        download_url = f"https://drive.google.com/uc?id={file_id}&export=download"

        st.info("📥 Downloading file from Google Drive...")

        response = requests.get(download_url)
        file_bytes = io.BytesIO(response.content)

        # Check if ZIP or CSV:
        if gdrive_url.endswith(".zip"):
            with zipfile.ZipFile(file_bytes) as z:
                csv_name = [f for f in z.namelist() if f.endswith(".csv")][0]
                st.success(f"CSV found inside ZIP → {csv_name}")
                df = pd.read_csv(z.open(csv_name))
        else:
            df = pd.read_csv(file_bytes)

        st.success("✅ File loaded successfully!")

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")


# ---------------------------------------------------
# PROCESS + DASHBOARD (RUN ONLY IF DATA LOADED)
# ---------------------------------------------------
if df is not None:
    try:
        # Clean dataset
        df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
        df["Year"] = df["dt"].dt.year
        df = df.dropna(subset=["AverageTemperature", "Country"])

        st.success("✔ Dataset cleaned and ready!")

        # Sidebar options
        st.sidebar.header("📊 Select Visualization")
        choice = st.sidebar.selectbox(
            "Choose a graph:",
            [
                "Global Temperature Trend",
                "Top 10 Hottest Countries",
                "Top 10 Coldest Countries",
                "Country-wise Temperature Trend",
                "Histogram of Global Temperatures",
            ],
        )

        # 1️⃣ Global Trend
        if choice == "Global Temperature Trend":
            st.subheader("🌍 Global Average Temperature Trend")
            global_temp = df.groupby("Year")["AverageTemperature"].mean().reset_index()
            fig = px.line(global_temp, x="Year", y="AverageTemperature",
                          title="Global Temperature Trend (Yearly)", markers=True)
            st.plotly_chart(fig, use_container_width=True)

        # 2️⃣ Hottest Countries
        elif choice == "Top 10 Hottest Countries":
            st.subheader("🔥 Top 10 Hottest Countries")
            hot = df.groupby("Country")["AverageTemperature"].mean().nlargest(10).reset_index()
            fig = px.bar(hot, x="AverageTemperature", y="Country",
                         orientation="h", title="Top 10 Hottest Countries",
                         color="AverageTemperature", color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)

        # 3️⃣ Coldest Countries
        elif choice == "Top 10 Coldest Countries":
            st.subheader("❄️ Top 10 Coldest Countries")
            cold = df.groupby("Country")["AverageTemperature"].mean().nsmallest(10).reset_index()
            fig = px.bar(cold, x="AverageTemperature", y="Country",
                         orientation="h", title="Top 10 Coldest Countries",
                         color="AverageTemperature", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)

        # 4️⃣ Country Trend
        elif choice == "Country-wise Temperature Trend":
            st.subheader("🌎 Country-wise Temperature Trend")
            country = st.sidebar.selectbox("Select Country:", sorted(df["Country"].unique()))
            country_df = df[df["Country"] == country]
            trend = country_df.groupby("Year")["AverageTemperature"].mean().reset_index()
            fig = px.line(trend, x="Year", y="AverageTemperature",
                          title=f"Temperature Trend of {country}", markers=True)
            st.plotly_chart(fig, use_container_width=True)

        # 5️⃣ Histogram
        elif choice == "Histogram of Global Temperatures":
            st.subheader("📊 Histogram of Global Temperatures")
            fig = px.histogram(df, x="AverageTemperature",
                               title="Global Temperature Distribution", nbins=40)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Visualization Error: {e}")
