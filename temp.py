import streamlit as st
import pandas as pd
import zipfile
import io
import plotly.express as px

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.set_page_config(page_title="Global Temperature Dashboard", layout="wide")
st.title("🌡️ Global Temperature Dashboard")
st.write("Interactive Temperature Analysis using Streamlit")

# ---------------------------------------------------
# FILE UPLOAD (ZIP or CSV)
# ---------------------------------------------------
uploaded = "https://drive.google.com/file/d/1rIv7ciWzHOmGjl6QPwIeDhChTwCuTS_n/view?usp=drive_link"
data = pd.read_csv(uploaded)


        # ---------------------------
        # If CSV uploaded
        # ---------------------------
       

        # ---------------------------
        # CLEANING
        # ---------------------------
        df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
        df["Year"] = df["dt"].dt.year
        df = df.dropna(subset=["AverageTemperature", "Country"])

        st.success("✔ Dataset loaded successfully!")

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
            fig = px.line(global_temp, x="Year", y="AverageTemperature",
                          title="Global Temperature Trend (Yearly)",
                          markers=True)
            st.plotly_chart(fig, use_container_width=True)

        # ---------------------------------------------------
        # 2️⃣ HOTTEST COUNTRIES
        # ---------------------------------------------------
        elif choice == "Top 10 Hottest Countries":
            st.subheader("🔥 Top 10 Hottest Countries")
            hot = df.groupby("Country")["AverageTemperature"].mean().nlargest(10).reset_index()
            fig = px.bar(hot, x="AverageTemperature", y="Country",
                         orientation="h", title="Top 10 Hottest Countries",
                         color="AverageTemperature", color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)

        # ---------------------------------------------------
        # 3️⃣ COLDEST COUNTRIES
        # ---------------------------------------------------
        elif choice == "Top 10 Coldest Countries":
            st.subheader("❄️ Top 10 Coldest Countries")
            cold = df.groupby("Country")["AverageTemperature"].mean().nsmallest(10).reset_index()
            fig = px.bar(cold, x="AverageTemperature", y="Country",
                         orientation="h", title="Top 10 Coldest Countries",
                         color="AverageTemperature", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)

        # ---------------------------------------------------
        # 4️⃣ COUNTRY-WISE TREND
        # ---------------------------------------------------
        elif choice == "Country-wise Temperature Trend":
            st.subheader("🌎 Country-wise Temperature Trend")

            country = st.sidebar.selectbox("Select Country:", sorted(df["Country"].unique()))
            country_df = df[df["Country"] == country]
            trend = country_df.groupby("Year")["AverageTemperature"].mean().reset_index()

            fig = px.line(trend, x="Year", y="AverageTemperature",
                          title=f"Temperature Trend of {country}",
                          markers=True)
            st.plotly_chart(fig, use_container_width=True)

        # ---------------------------------------------------
        # 5️⃣ HISTOGRAM
        # ---------------------------------------------------
        elif choice == "Histogram of Global Temperatures":
            st.subheader("📊 Histogram of Global Temperatures")
            fig = px.histogram(df, x="AverageTemperature",
                               title="Global Temperature Distribution",
                               nbins=40)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("📥 Upload a ZIP/CSV file to begin.") 
