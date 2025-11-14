import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

st.set_page_config(page_title="Global Temperature Dashboard", layout="wide")
st.title("🌡️ Global Temperature Dashboard")
st.write("Interactive Temperature Analysis using Streamlit")

# ---------------------------------------------------
# SELECT INPUT METHOD
# ---------------------------------------------------
option = st.selectbox(
    "📂 How do you want to load the data?",
    ["Upload CSV file", "Google Drive Link"]
)

# Function: Safe CSV loader (encoding fix)
def load_csv_safe(content):
    encodings = ["utf-8", "latin1", "ISO-8859-1"]

    for enc in encodings:
        try:
            return pd.read_csv(io.BytesIO(content), encoding=enc)
        except:
            pass

    # last resort: python engine autodetect
    return pd.read_csv(io.BytesIO(content), sep=None, engine="python")

# ---------------------------------------------------
# OPTION 1 → UPLOAD CSV
# ---------------------------------------------------
if option == "Upload CSV file":
    uploaded = st.file_uploader("📥 Upload CSV", type=["csv"])

    if uploaded:
        content = uploaded.read()
        df = load_csv_safe(content)
        st.success("✔ File loaded successfully")

    else:
        st.stop()

# ---------------------------------------------------
# OPTION 2 → GOOGLE DRIVE LINK
# ---------------------------------------------------
elif option == "Google Drive Link":
    gdrive_link = st.text_input("Paste Google Drive CSV link:")

    if gdrive_link:
        try:
            # Extract file ID
            if "id=" in gdrive_link:
                file_id = gdrive_link.split("id=")[1]
            else:
                file_id = gdrive_link.split("/d/")[1].split("/")[0]

            raw_url = f"https://drive.google.com/uc?export=download&id={file_id}"

            st.info("📥 Downloading from Google Drive...")
            response = requests.get(raw_url)

            content = response.content
            df = load_csv_safe(content)

            st.success("✔ File loaded successfully")

        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
            st.stop()
    else:
        st.stop()

# ---------------------------------------------------
# CHECK REQUIRED COLUMNS
# ---------------------------------------------------
required = ["dt", "AverageTemperature", "Country"]
for col in required:
    if col not in df.columns:
        st.error(f"❌ Column missing: {col}")
        st.stop()

# CLEANING
df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
df["Year"] = df["dt"].dt.year
df = df.dropna(subset=["AverageTemperature", "Country"])

# ---------------------------------------------------
# SIDEBAR VISUALIZATION OPTIONS
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
    ]
)

# ---------------------------------------------------
# VISUALIZATIONS
# ---------------------------------------------------

if choice == "Global Temperature Trend":
    st.subheader("🌍 Global Average Temperature Trend")
    global_temp = df.groupby("Year")["AverageTemperature"].mean().reset_index()
    fig = px.line(global_temp, x="Year", y="AverageTemperature", markers=True)
    st.plotly_chart(fig, use_container_width=True)

elif choice == "Top 10 Hottest Countries":
    hot = df.groupby("Country")["AverageTemperature"].mean().nlargest(10).reset_index()
    fig = px.bar(hot, x="AverageTemperature", y="Country", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

elif choice == "Top 10 Coldest Countries":
    cold = df.groupby("Country")["AverageTemperature"].mean().nsmallest(10).reset_index()
    fig = px.bar(cold, x="AverageTemperature", y="Country", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

elif choice == "Country-wise Temperature Trend":
    country = st.sidebar.selectbox("Select Country:", sorted(df["Country"].unique()))
    country_df = df[df["Country"] == country]
    trend = country_df.groupby("Year")["AverageTemperature"].mean().reset_index()
    fig = px.line(trend, x="Year", y="AverageTemperature", markers=True)
    st.plotly_chart(fig, use_container_width=True)

elif choice == "Histogram of Global Temperatures":
    fig = px.histogram(df, x="AverageTemperature", nbins=40)
    st.plotly_chart(fig, use_container_width=True)
