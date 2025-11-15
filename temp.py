import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile

st.title("🌍 Global Temperature & Climate Change Dashboard")

# --------------------------
# CSS for Output Outline Box
# --------------------------
st.markdown("""
<style>
.output-box {
    border: 2px solid #4CAF50;
    padding: 15px;
    border-radius: 12px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# Upload ZIP
# --------------------------
uploaded = st.file_uploader("📥 Upload ZIP file containing CSV", type="zip")
if not uploaded:
    st.stop()

try:
    with zipfile.ZipFile(uploaded) as z:
        df = pd.read_csv(z.open(z.namelist()[0]))
except:
    st.error("Invalid ZIP file")
    st.stop()

# --------------------------
# Clean Data
# --------------------------
df["dt"] = pd.to_datetime(df["dt"], errors="ignore")
df["Year"] = df["dt"].dt.year
df = df.dropna(subset=["AverageTemperature", "Country"])

# --------------------------
# Sidebar Menu
# --------------------------
menu = st.sidebar.selectbox(
    "📊 Select View",
    [
        "Top 10 Hottest Countries",
        "Top 10 Coldest Countries",
        "Country-wise Temperature Trend",
        "Histogram of Global Temperatures",
    ],
)

# --------------------------
# Colors
# --------------------------
colors = {
    "hot": "#FF0000",
    "cold": "#0077FF",
    "line": "#2ECC71",
    "hist": "#8E44AD",
}

# --------------------------
# Views With Outline Box
# --------------------------
if menu == "Top 10 Hottest Countries":
    data = df.groupby("Country")["AverageTemperature"].mean().nlargest(10).reset_index()
    st.markdown('<div class="output-box">', unsafe_allow_html=True)
    st.subheader("🔥 Top 10 Hottest Countries")
    st.plotly_chart(px.bar(data, x="AverageTemperature", y="Country",
                           orientation="h", color_discrete_sequence=[colors["hot"]]),
                    use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Top 10 Coldest Countries":
    data = df.groupby("Country")["AverageTemperature"].mean().nsmallest(10).reset_index()
    st.markdown('<div class="output-box">', unsafe_allow_html=True)
    st.subheader("❄️ Top 10 Coldest Countries")
    st.plotly_chart(px.bar(data, x="AverageTemperature", y="Country",
                           orientation="h", color_discrete_sequence=[colors["cold"]]),
                    use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Country-wise Temperature Trend":
    country = st.selectbox("Select Country", sorted(df["Country"].unique()))
    data = df[df["Country"] == country].groupby("Year")["AverageTemperature"].mean().reset_index()
    st.markdown('<div class="output-box">', unsafe_allow_html=True)
    st.subheader(f"🌎 Temperature Trend — {country}")
    st.plotly_chart(px.line(data, x="Year", y="AverageTemperature",
                            color_discrete_sequence=[colors["line"]]),
                    use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Histogram of Global Temperatures":
    st.markdown('<div class="output-box">', unsafe_allow_html=True)
    st.subheader("📊 Temperature Distribution")
    st.plotly_chart(px.histogram(df, x="AverageTemperature",
                                 nbins=40, color_discrete_sequence=[colors["hist"]]),
                    use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
