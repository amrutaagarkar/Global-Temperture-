import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global Temperature Dashboard", layout="wide")
st.title("🌡️ Global Temperature Dashboard")
st.write("Interactive Temperature Analysis using Streamlit")

# ---------------------------------------------------
# GOOGLE DRIVE FILE
# ---------------------------------------------------
file_id = "1rIv7ciWzHOmGjl6QPwIeDhChTwCuTS_n"
raw_url = f"https://drive.google.com/uc?export=download&id={file_id}"

st.info("📥 Downloading CSV from Google Drive...")


# ---------------------------------------------------
# FIX 1: ENCODING + DELIMITER AUTO-DETECT
# ---------------------------------------------------
def load_with_encodings(url):
    encodings = ["utf-8", "latin1", "ISO-8859-1", "cp1252"]
    delimiters = [",", ";", "\t", "|"]

    for enc in encodings:
        for d in delimiters:
            try:
                return pd.read_csv(url, encoding=enc, delimiter=d)
            except:
                continue

    # last attempt → automatic
    return pd.read_csv(url, encoding="latin1", sep=None, engine="python")


# ---------------------------------------------------
# LOAD FILE
# ---------------------------------------------------
try:
    df = load_with_encodings(raw_url)
    st.success("✔ CSV file loaded successfully!")

    # Required columns check
    required = ["dt", "AverageTemperature", "Country"]
    for col in required:
        if col not in df.columns:
            st.error(f"❌ Missing required column: {col}")
            st.stop()

    # CLEANING
    df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
    df["Year"] = df["dt"].dt.year
    df = df.dropna(subset=["AverageTemperature", "Country"])

    st.success("✔ Data cleaned and ready for analysis!")

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
    # VISUALS
    # ---------------------------------------------------
    if choice == "Global Temperature Trend":
        st.subheader("🌍 Global Average Temperature Trend")
        global_temp = df.groupby("Year")["AverageTemperature"].mean().reset_index()
        fig = px.line(global_temp, x="Year", y="AverageTemperature",
                      markers=True)
        st.plotly_chart(fig, use_container_width=True)

    elif choice == "Top 10 Hottest Countries":
        st.subheader("🔥 Top 10 Hottest Countries")
        hot = df.groupby("Country")["AverageTemperature"].mean().nlargest(10).reset_index()
        fig = px.bar(hot, x="AverageTemperature", y="Country", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    elif choice == "Top 10 Coldest Countries":
        st.subheader("❄️ Top 10 Coldest Countries")
        cold = df.groupby("Country")["AverageTemperature"].mean().nsmallest(10).reset_index()
        fig = px.bar(cold, x="AverageTemperature", y="Country", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    elif choice == "Country-wise Temperature Trend":
        st.subheader("🌎 Country-wise Temperature Trend")
        country = st.sidebar.selectbox("Select Country:", sorted(df["Country"].unique()))
        country_df = df[df["Country"] == country]
        trend = country_df.groupby("Year")["AverageTemperature"].mean().reset_index()
        fig = px.line(trend, x="Year", y="AverageTemperature", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    elif choice == "Histogram of Global Temperatures":
        st.subheader("📊 Histogram of Global Temperatures")
        fig = px.histogram(df, x="AverageTemperature", nbins=40)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error loading file: {e}")
