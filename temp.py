import streamlit as st
import pandas as pd
import io
import requests
import plotly.express as px

# -----------------------------
# APP TITLE
# -----------------------------
st.set_page_config(page_title="🌍 Global Temperature Dashboard", layout="wide")
st.title("🌡️ Global Temperature Dashboard ")

# -----------------------------
# DOWNLOAD CSV FROM GOOGLE DRIVE
# -----------------------------
  # from your link
download_url = f"https://drive.google.com/uc?export=download&id={"1RT8dMSKj2123wY_BjELt_3LabFQL0GA4}"

@st.cache_data
def load_data(url):
    try:
        st.info("📥 Downloading data from Google Drive...")
        response = requests.get(url)
        response.raise_for_status()

        # Try reading as CSV
        df = pd.read_csv(io.BytesIO(response.content), low_memory=False)
        return df
    except Exception as e:
        st.error(f"❌ Error loading CSV: {e}")
        return None

df = load_data(download_url)

# -----------------------------
# VALIDATE DATA
# -----------------------------
if df is not None:
    st.success("✅ File loaded successfully!")
    st.write("### Preview of Data:")
    st.dataframe(df.head())

    # Try to detect the key columns automatically
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

    if date_col and temp_col and country_col:
        st.success(f"✅ Detected columns: {date_col}, {temp_col}, {country_col}")
    else:
        st.error("❌ Could not detect temperature or country columns automatically.")
        st.stop()

    # -----------------------------
    # CLEAN DATA
    # -----------------------------
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df['Year'] = df[date_col].dt.year
    df = df.dropna(subset=[temp_col, country_col])

    # -----------------------------
    # MENU SELECTION
    # -----------------------------
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

    # -----------------------------
    # PLOTS
    # -----------------------------
    if menu == "Global Temperature Trend":
        global_temp = df.groupby("Year")[temp_col].mean().reset_index()
        fig = px.line(global_temp, x="Year", y=temp_col,
                      title="🌡️ Global Average Temperature Over Time",
                      color_discrete_sequence=["red"])
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "Top 10 Hottest Countries":
        hot = df.groupby(country_col)[temp_col].mean().nlargest(10).reset_index()
        fig = px.bar(hot, x=temp_col, y=country_col, orientation="h",
                     title="🔥 Top 10 Hottest Countries",
                     color=temp_col, color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "Top 10 Coldest Countries":
        cold = df.groupby(country_col)[temp_col].mean().nsmallest(10).reset_index()
        fig = px.bar(cold, x=temp_col, y=country_col, orientation="h",
                     title="❄️ Top 10 Coldest Countries",
                     color=temp_col, color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "Country-wise Temperature Trend":
        country = st.selectbox("🌍 Select a Country", sorted(df[country_col].unique()))
        trend = df[df[country_col] == country].groupby("Year")[temp_col].mean().reset_index()
        fig = px.line(trend, x="Year", y=temp_col,
                      title=f"🌍 Temperature Trend of {country}",
                      color_discrete_sequence=["green"])
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "Histogram of Global Temperatures":
        fig = px.histogram(df, x=temp_col, nbins=40,
                           title="📊 Distribution of Global Average Temperatures",
                           color_discrete_sequence=["royalblue"])
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ No data loaded. Please check your Google Drive link or CSV format.")
