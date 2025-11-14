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

# ---------------------------------------------------
# DATA SOURCE SELECTION
# ---------------------------------------------------
st.sidebar.title("📥 Data Input Options")
data_source = st.sidebar.radio("Choose Data Source:", [
    "Upload File",
    "Google Drive Link",
])

df = None  # initialize empty dataframe

# ---------------------------------------------------
# OPTION 1: FILE UPLOAD
# ---------------------------------------------------
if data_source == "Upload File":
    uploaded = st.file_uploader("https://drive.google.com/file/d/1rIv7ciWzHOmGjl6QPwIeDhChTwCuTS_n/view?usp=drive_link", type=["zip", "csv"])

    if uploaded is not None:
        try:
            if uploaded.name.endswith(".zip"):
                with zipfile.ZipFile(uploaded) as z:
                    csv_name = [f for f in z.namelist() if f.endswith(".csv")][0]
                    st.success(f"CSV found inside ZIP → {csv_name}")
                    df = pd.read_csv(z.open(csv_name))
            else:
                df = pd.read_csv(uploaded)

        except Exception as e:
            st.error(f"❌ Error loading file: {e}")

# ---------------------------------------------------
# OPTION 2: GOOGLE DRIVE LINK
# ---------------------------------------------------
elif data_source == "Google Drive Link":
    gdrive_url = st.text_input("Paste Google Drive Share Link:")

    if st.button("Load from Google Drive"):
        try:
            # Extract FILE ID
            if "id=" in gdrive_url:
                file_id = gdrive_url.split("id=")[1]
            else:
                file_id = gdrive_url.split("/d/")[1].split("/")[0]

            # Download link
            download_url = f"https://drive.google.com/uc?id={file_id}&export=download"

            st.info("📥 Downloading file from Google Drive...")

            response = requests.get(download_url)
            file_bytes = io.BytesIO(response.content)

            # Check if ZIP or CSV
            if gdrive_url.endswith(".zip"):
                with zipfile.ZipFile(file_bytes) as z:
                    csv_name = [f for f in z.namelist() if f.endswith(".csv")][0]
                    st.success(f"CSV found inside ZIP → {csv_name}")
                    df = pd.read_csv(z.open(csv_name))
            else:
                df = pd.read_csv(file_bytes)

            st.success("✅ File loaded successfully!")

        except Exception as e:
            st.error(f"❌ Error loading Google Drive file: {e}")

# ---------------------------------------------------
# PROCESS AND VISUALIZE IF DATA LOADED
# ---------------------------------------------------
if df is not None:
    try:
        df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
        df["Year"] = df["dt"].dt.year
        df = df.dropna(subset=["AverageTemperature", "Country"])

        st.success("✔ Dataset cleaned and ready!")

        # ---------------------------------------------------
        # SIDEBAR OPTIONS
        # ---------------------------------------------------
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

        # ---------------------------------------------------
        # GRAPHS
        # ---------------------------------------------------

        if choice == "Global Temperature Trend":
            st.subheader("🌍 Global Average Temperature Trend")
            global_temp = df.groupby("Year")["AverageTemperature"].mean().reset_index()
            fig = px.line(global_temp, x="Year", y="AverageTemperature",
                          title="Global Temperature Trend (Yearly)", markers=True)
            st.plotly_chart(fig, use_container_width=True)

        elif choice == "Top 10 Hottest Countries":
            st.subheader("🔥 Top 10 Hottest Countries")
            hot = df.groupby("Country")["AverageTemperature"].mean().nlargest(10).reset_index()
            fig = px.bar(hot, x="AverageTemperature", y="Country",
                         orientation="h", title="Top 10 Hottest Countries",
                         color="AverageTemperature", color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)

        elif choice == "Top 10 Coldest Countries":
            st.subheader("❄️ Top 10 Coldest Countries")
            cold = df.groupby("Country")["AverageTemperature"].mean().nsmallest(10).reset_index()
            fig = px.bar(cold, x="AverageTemperature", y="Country",
                         orientation="h", title="Top 10 Coldest Countries",
                         color="AverageTemperature", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)

        elif choice == "Country-wise Temperature Trend":
            st.subheader("🌎 Country-wise Temperature Trend")
            country = st.sidebar.selectbox("Select Country:", sorted(df["Country"].unique()))
            country_df = df[df["Country"] == country]
            trend = country_df.groupby("Year")["AverageTemperature"].mean().reset_index()
            fig = px.line(trend, x="Year", y="AverageTemperature",
                          title=f"Temperature Trend of {country}", markers=True)
            st.plotly_chart(fig, use_container_width=True)

        elif choice == "Histogram of Global Temperatures":
            st.subheader("📊 Histogram of Global Temperatures")
            fig = px.histogram(df, x="AverageTemperature",
                               title="Global Temperature Distribution", nbins=40)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Visualization Error: {e}")

else:
    st.info("📥 Upload a file or enter Google Drive link to begin.")
