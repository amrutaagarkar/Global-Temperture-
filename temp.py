import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
import io
import requests

st.title("🌍 Global Temperature Dashboard (Google Drive Linked)")

# ------------------------------------------------------
# 🔗 Google Drive Link (update if needed)
# ------------------------------------------------------
drive_link = "https://drive.google.com/file/d/1RT8dMSKj2123wY_BjELt_3LabFQL0GA4/view?usp=drive_link"

try:
    file_id = drive_link.split("/d/")[1].split("/")[0]
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
except Exception:
    st.error("❌ Invalid Google Drive link format.")
    st.stop()


@st.cache_data
def load_data(url):
    r = requests.get(url)
    if r.status_code != 200:
        st.error("❌ Could not download file from Google Drive.")
        st.stop()

    content = io.BytesIO(r.content)

    # Try reading as ZIP first
    try:
        with zipfile.ZipFile(content, "r") as z:
            csv_name = [f for f in z.namelist() if f.lower().endswith((".csv", ".xls", ".xlsx"))][0]
            with z.open(csv_name) as f:
                try:
                    df = pd.read_csv(f, sep=",", on_bad_lines="skip", low_memory=False)
                except Exception:
                    f.seek(0)
                    df = pd.read_csv(f, sep=";", encoding="latin1", on_bad_lines="skip", low_memory=False)
            return df
    except zipfile.BadZipFile:
        # Try plain CSV
        try:
            df = pd.read_csv(content, sep=",", on_bad_lines="skip", low_memory=False)
            return df
        except Exception:
            try:
                content.seek(0)
                df = pd.read_csv(content, sep=";", encoding="latin1", on_bad_lines="skip", low_memory=False)
                return df
            except Exception as e:
                st.error(f"❌ Failed to read CSV file. Error: {e}")
                st.stop()


df = load_data(download_url)

# ------------------------------------------------------
# 🧹 Show columns
# ------------------------------------------------------
st.write("✅ File loaded successfully! Columns detected:")
st.write(df.columns.tolist())

# Show a preview of the data
st.dataframe(df.head(10))


# ------------------------------------------------------
# 🧹 Prepare columns
# ------------------------------------------------------
date_col = next((c for c in df.columns if "dt" in c.lower() or "date" in c.lower()), None)
temp_col = next((c for c in df.columns if "temp" in c.lower()), None)
country_col = next((c for c in df.columns if "country" in c.lower()), None)

if not temp_col or not country_col:
    st.error("❌ Could not detect temperature or country columns automatically.")
    st.stop()

if date_col:
    df["dt"] = pd.to_datetime(df[date_col], errors="coerce")
    df["Year"] = df["dt"].dt.year
else:
    df["Year"] = range(1, len(df) + 1)

df = df.dropna(subset=[temp_col, country_col])

# ------------------------------------------------------
# 📊 Sidebar menu
# ------------------------------------------------------
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

# ------------------------------------------------------
# 📈 Visualizations
# ------------------------------------------------------
if menu == "Global Temperature Trend":
    global_temp = df.groupby("Year")[temp_col].mean().reset_index()
    fig = px.line(global_temp, x="Year", y=temp_col,
                  title="🌡️ Global Average Temperature Trend (Yearly)",
                  color_discrete_sequence=["firebrick"])
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Top 10 Hottest Countries":
    hot = df.groupby(country_col)[temp_col].mean().nlargest(10).reset_index()
    fig = px.bar(hot, x=temp_col, y=country_col, orientation="h",
                 title="🔥 Top 10 Hottest Countries", color=temp_col,
                 color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Top 10 Coldest Countries":
    cold = df.groupby(country_col)[temp_col].mean().nsmallest(10).reset_index()
    fig = px.bar(cold, x=temp_col, y=country_col, orientation="h",
                 title="❄️ Top 10 Coldest Countries", color=temp_col,
                 color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Country-wise Temperature Trend":
    country = st.selectbox("🌎 Select Country", sorted(df[country_col].unique()))
    sub = df[df[country_col] == country].groupby("Year")[temp_col].mean().reset_index()
    fig = px.line(sub, x="Year", y=temp_col,
                  title=f"🌍 Temperature Trend of {country}",
                  color_discrete_sequence=["green"])
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Histogram of Global Temperatures":
    fig = px.histogram(df, x=temp_col, nbins=40,
                       title="📊 Distribution of Global Temperatures",
                       color_discrete_sequence=["royalblue"])
    st.plotly_chart(fig, use_container_width=True)
