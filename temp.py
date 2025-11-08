import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------
# 🔗 STEP 1: LOAD DATA FROM GOOGLE DRIVE
# ----------------------------------------
# Replace this link with YOUR Drive file link
drive_link = "https://drive.google.com/file/d/1RT8dMSKj2123wY_BjELt_3LabFQL0GA4/view?usp=drive_link"

# Convert "view" link to "uc?id=" direct download link
file_id = drive_link.split("/d/")[1].split("/")[0]
download_url = f"https://drive.google.com/uc?id={file_id}"

# Try loading the CSV
try:
    df = pd.read_csv(download_url)
except Exception as e:
    st.error(f"❌ Error loading CSV: {e}")
    st.stop()

# ----------------------------------------
# 🧾 STEP 2: PREVIEW DATA
# ----------------------------------------
st.title("🌍 Global Temperature Dashboard (Google Drive Linked)")

st.sidebar.header("⚙️ Dashboard Controls")
st.sidebar.success("Connected to Google Drive CSV ✅")

# Show columns for debugging
st.subheader("🔍 Dataset Preview")
st.write("**Columns found:**", list(df.columns))
st.dataframe(df.head())

# ----------------------------------------
# 🧩 STEP 3: HANDLE MISSING OR UNKNOWN COLUMNS
# ----------------------------------------
expected_columns = ['dt', 'AverageTemperature', 'Country']

# If missing, show warning
missing_cols = [col for col in expected_columns if col not in df.columns]
if missing_cols:
    st.warning(f"⚠️ Missing expected columns: {missing_cols}")
    st.info("➡️ Please rename them or tell me the actual column names so I can fix the code.")
    st.stop()

# ----------------------------------------
# 🧮 STEP 4: CLEAN & PROCESS DATA
# ----------------------------------------
df['dt'] = pd.to_datetime(df['dt'], errors='coerce')
df['Year'] = df['dt'].dt.year
df = df.dropna(subset=['AverageTemperature', 'Country'])

# ----------------------------------------
# 📊 STEP 5: SIDEBAR MENU
# ----------------------------------------
menu = st.sidebar.selectbox(
    "Select Visualization:",
    [
        "Global Temperature Trend",
        "Top 10 Hottest Countries",
        "Top 10 Coldest Countries",
        "Country-wise Temperature Trend",
        "Histogram of Global Temperatures"
    ]
)

# ----------------------------------------
# 🌡️ STEP 6: VISUALIZATIONS
# ----------------------------------------

# 1️⃣ GLOBAL TEMPERATURE TREND
if menu == "Global Temperature Trend":
    global_temp = df.groupby("Year")['AverageTemperature'].mean().reset_index()
    fig = px.line(
        global_temp,
        x='Year',
        y='AverageTemperature',
        title='🌡️ Global Average Temperature Trend (Yearly)',
        color_discrete_sequence=["firebrick"]
    )
    fig.update_layout(yaxis_title="Average Temperature (°C)")
    st.plotly_chart(fig, use_container_width=True)

# 2️⃣ TOP 10 HOTTEST COUNTRIES
elif menu == "Top 10 Hottest Countries":
    hot = (
        df.groupby("Country")['AverageTemperature']
        .mean()
        .nlargest(10)
        .reset_index()
    )
    fig = px.bar(
        hot,
        x='AverageTemperature',
        y='Country',
        orientation='h',
        title='🔥 Top 10 Hottest Countries (Average Temperature)',
        color='AverageTemperature',
        color_continuous_scale='Reds'
    )
    fig.update_layout(xaxis_title="Average Temperature (°C)")
    st.plotly_chart(fig, use_container_width=True)

# 3️⃣ TOP 10 COLDEST COUNTRIES
elif menu == "Top 10 Coldest Countries":
    cold = (
        df.groupby("Country")['AverageTemperature']
        .mean()
        .nsmallest(10)
        .reset_index()
    )
    fig = px.bar(
        cold,
        x='AverageTemperature',
        y='Country',
        orientation='h',
        title='❄️ Top 10 Coldest Countries (Average Temperature)',
        color='AverageTemperature',
        color_continuous_scale='Blues'
    )
    fig.update_layout(xaxis_title="Average Temperature (°C)")
    st.plotly_chart(fig, use_container_width=True)

# 4️⃣ COUNTRY-WISE TEMPERATURE TREND
elif menu == "Country-wise Temperature Trend":
    countries = sorted(df['Country'].unique())
    selected_country = st.selectbox("🌎 Select Country:", countries)

    if selected_country:
        trend = (
            df[df['Country'] == selected_country]
            .groupby("Year")['AverageTemperature']
            .mean()
            .reset_index()
        )

        fig = px.line(
            trend,
            x='Year',
            y='AverageTemperature',
            title=f"🌍 Temperature Trend of {selected_country}",
            color_discrete_sequence=["green"]
        )
        fig.update_layout(yaxis_title="Average Temperature (°C)")
        st.plotly_chart(fig, use_container_width=True)

# 5️⃣ HISTOGRAM
elif menu == "Histogram of Global Temperatures":
    fig = px.histogram(
        df,
        x='AverageTemperature',
        nbins=40,
        title='📊 Distribution of Global Average Temperatures',
        color_discrete_sequence=["royalblue"]
    )
    fig.update_layout(
        xaxis_title="Average Temperature (°C)",
        yaxis_title="Frequency"
    )
    st.plotly_chart(fig, use_container_width=True)
