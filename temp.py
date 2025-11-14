import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import zipfile
import io

# -------------------------------------------------------
# PAGE SETTINGS
# -------------------------------------------------------
st.set_page_config(
    page_title="🌍 Global Temperature Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌡️ Recent Global Temperature Dashboard")

# -------------------------------------------------------
# LOAD DATA (Google Drive ZIP)
# -------------------------------------------------------
file_id = "1RT8dMSKj2123wY_BjELt_3LabFQL0GA4"
url = f"https://drive.google.com/uc?export=download&id={file_id}"

@st.cache_data
def load_temperature_data():
    try:
        st.info("📥 Downloading temperature data...")
        r = requests.get(url)
        r.raise_for_status()

        if r.content[:2] != b"PK":
            st.error("❌ File is not a ZIP. Please check Google Drive link.")
            return None

        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            csv_files = [f for f in z.namelist() if f.endswith(".csv")]
            if not csv_files:
                st.error("❌ ZIP contains no CSV file.")
                return None

            with z.open(csv_files[0]) as f:
                df = pd.read_csv(f, low_memory=False)
                return df

    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None

df = load_temperature_data()
if df is None:
    st.stop()

# -------------------------------------------------------
# AUTO-DETECT COLUMNS
# -------------------------------------------------------
date_col = next((c for c in df.columns if "date" in c.lower() or "dt" in c.lower()), None)
temp_col = next((c for c in df.columns if "temp" in c.lower()), None)
country_col = next((c for c in df.columns if "country" in c.lower()), None)

if not all([date_col, temp_col, country_col]):
    st.error("❌ Missing required columns: date, temperature, or country.")
    st.stop()

# Cleaning
df[date_col] = pd.to_datetime(df[date_col], errors="ignore")
df["Year"] = df[date_col].dt.year
df = df.dropna(subset=[temp_col, country_col])

st.success("✅ Data loaded successfully!")

# -------------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------------
st.sidebar.header("📌 Filters")

year_range = st.sidebar.slider(
    "Select Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (2000, df["Year"].max())
)

country_list = ["All Countries"] + sorted(df[country_col].unique())
selected_country = st.sidebar.selectbox("Select Country", country_list)

# Apply filters
filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

if selected_country != "All Countries":
    filtered = filtered[filtered[country_col] == selected_country]

# -------------------------------------------------------
# DASHBOARD CARDS
# -------------------------------------------------------
col1, col2, col3 = st.columns(3)

avg_temp = round(filtered[temp_col].mean(), 2)
hottest_year = int(filtered.groupby("Year")[temp_col].mean().idxmax())
coldest_year = int(filtered.groupby("Year")[temp_col].mean().idxmin())

col1.metric("🌡️ Avg Temperature", f"{avg_temp} °C")
col2.metric("🔥 Hottest Year", hottest_year)
col3.metric("❄️ Coldest Year", coldest_year)

# -------------------------------------------------------
# VISUALIZATIONS
# -------------------------------------------------------
st.subheader("📈 Temperature Trends")

trend = filtered.groupby("Year")[temp_col].mean().reset_index()

fig1 = px.line(
    trend,
    x="Year",
    y=temp_col,
    title="🌍 Global Temperature Trend",
    markers=True
)
st.plotly_chart(fig1, use_container_width=True)

# -------------------------------------------------------
# COUNTRIES COMPARISON (ONLY WHEN ALL COUNTRIES SELECTED)
# -------------------------------------------------------
if selected_country == "All Countries":
    st.subheader("🌡️ Top 10 Hottest Countries")

    hot = filtered.groupby(country_col)[temp_col].mean().nlargest(10).reset_index()
    fig2 = px.bar(
        hot,
        x=temp_col,
        y=country_col,
        orientation="h",
        title="🔥 Top 10 Hottest Countries"
    )
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------------
# HISTOGRAM
# -------------------------------------------------------
st.subheader("📊 Temperature Distribution")

fig3 = px.histogram(
    filtered,
    x=temp_col,
    nbins=40,
    title="📌 Temperature Histogram"
)
st.plotly_chart(fig3, use_container_width=True)

# End
st.write("✔️ Dashboard Updated with Recent Temperature Analysis")
