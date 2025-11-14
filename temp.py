import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.set_page_config(page_title="Global Temperature Dashboard", layout="wide")
st.title("🌡️ Global Temperature Dashboard")
st.write("Interactive Temperature Analysis using Streamlit")

# ---------------------------------------------------
# GOOGLE DRIVE CSV LINK
# ---------------------------------------------------
st.subheader("📂 Loading Temperature Dataset from Google Drive")

# Your Google Drive file ID
file_id = "1rIv7ciWzHOmGjl6QPwIeDhChTwCuTS_n"

# Convert Drive link to direct download URL
raw_url = f"https://drive.google.com/uc?export=download&id={file_id}"

st.info("📥 Downloading CSV from Google Drive...")

# ---------------------------------------------------
# LOAD CSV WITH ENCODING FIX
# ---------------------------------------------------
try:
    try:
        df = pd.read_csv(raw_url)
    except UnicodeDecodeError:
        df = pd.read_csv(raw_url, encoding="latin1")

    st.success("✔ File loaded successfully!")

    # ---------------------------------------------------
    # CLEANING
    # ---------------------------------------------------
    df["dt"] = pd.to_datetime(df["dt"], errors="coerce")

    if "AverageTemperature" not in df.columns:
        st.error("❌ Required column 'AverageTemperature' not found in your CSV.")
        st.stop()

    if "Country" not in df.columns:
        st.error("❌ Required column 'Country' not found in your CSV.")
        st.stop()

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
    # 1️⃣ GLOBAL TEMPERATURE TREND
    # ---------------------------------------------------
    if choice == "Global Temperature Trend":
        st.subheader("🌍 Global Average Temperature Trend")
        global_temp = df.groupby("Year")["AverageTemperature"].mean().reset_index()
        fig = px.line(
            global_temp,
            x="Year",
            y="AverageTemperature",
            title="Global Temperature Trend (Yearly)",
            markers=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------
    # 2️⃣ HOTTEST COUNTRIES
    # ---------------------------------------------------
    elif choice == "Top 10 Hottest Countries":
        st.subheader("🔥 Top 10 Hottest Countries")
        hot = (
            df.groupby("Country")["AverageTemperature"]
            .mean()
            .nlargest(10)
            .reset_index()
        )
        fig = px.bar(
            hot,
            x="AverageTemperature",
            y="Country",
            orientation="h",
            title="Top 10 Hottest Countries",
            color="AverageTemperature",
            color_continuous_scale="Reds",
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------
    # 3️⃣ COLDEST COUNTRIES
    # ---------------------------------------------------
    elif choice == "Top 10 Coldest Countries":
        st.subheader("❄️ Top 10 Coldest Countries")
        cold = (
            df.groupby("Country")["AverageTemperature"]
            .mean()
            .nsmallest(10)
            .reset_index()
        )
        fig = px.bar(
            cold,
            x="AverageTemperature",
            y="Country",
            orientation="h",
            title="Top 10 Coldest Countries",
            color="AverageTemperature",
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------
    # 4️⃣ COUNTRY-WISE TREND
    # ---------------------------------------------------
    elif choice == "Country-wise Temperature Trend":
        st.subheader("🌎 Country-wise Temperature Trend")

        country = st.sidebar.selectbox(
            "Select Country:", sorted(df["Country"].unique())
        )
        country_df = df[df["Country"] == country]
        trend = country_df.groupby("Year")["AverageTemperature"].mean().reset_index()

        fig = px.line(
            trend,
            x="Year",
            y="AverageTemperature",
            title=f"Temperature Trend of {country}",
            markers=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------
    # 5️⃣ HISTOGRAM
    # ---------------------------------------------------
    elif choice == "Histogram of Global Temperatures":
        st.subheader("📊 Histogram of Global Temperatures")
        fig = px.histogram(
            df,
            x="AverageTemperature",
            title="Global Temperature Distribution",
            nbins=40,
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# HANDLE ERRORS
# ---------------------------------------------------
except Exception as e:
    st.error(f"❌ Error loading file: {e}")
