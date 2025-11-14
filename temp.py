import pandas as pd
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display
import requests
import zipfile
import io

# -------------------------------------------------------
# LOAD DATA FROM GOOGLE DRIVE ZIP
# -------------------------------------------------------

file_id = "1RT8dMSKj2123wY_BjELt_3LabFQL0GA4"
url = f"https://drive.google.com/uc?export=download&id={file_id}"

response = requests.get(url)
content = response.content

# Extract ZIP → CSV
with zipfile.ZipFile(io.BytesIO(content)) as z:
    csv_files = [f for f in z.namelist() if f.endswith(".csv")]
    csv_name = csv_files[0]
    with z.open(csv_name) as f:
        df = pd.read_csv(f, low_memory=False)

# -------------------------------------------------------
# AUTO DETECT IMPORTANT COLUMNS
# -------------------------------------------------------
date_col = [c for c in df.columns if "date" in c.lower() or "dt" in c.lower()][0]
temp_col = [c for c in df.columns if "temp" in c.lower()][0]
country_col = [c for c in df.columns if "country" in c.lower()][0]

df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
df["Year"] = df[date_col].dt.year
df = df.dropna(subset=[temp_col, country_col])

# -------------------------------------------------------
# DROPDOWN MENU
# -------------------------------------------------------
dropdown = widgets.Dropdown(
    options=[
        "Select...",
        "Global Temperature Trend",
        "Top 10 Hottest Countries",
        "Top 10 Coldest Countries",
        "Country-wise Trend",
        "Temperature Distribution"
    ],
    description="View:",
    style={'description_width': 'initial'}
)

output = widgets.Output()

# -------------------------------------------------------
# CALLBACK FUNCTION
# -------------------------------------------------------
def show_graph(change):
    output.clear_output()
    with output:
        choice = change['new']

        # ----------------------------------------
        # GLOBAL TREND
        # ----------------------------------------
        if choice == "Global Temperature Trend":
            temp = df.groupby("Year")[temp_col].mean().reset_index()
            fig = px.line(
                temp,
                x="Year", y=temp_col,
                title="🌡️ Global Average Temperature (Yearly)"
            )
            fig.show()

        # ----------------------------------------
        # TOP 10 HOTTEST COUNTRIES
        # ----------------------------------------
        elif choice == "Top 10 Hottest Countries":
            hot = df.groupby(country_col)[temp_col].mean().nlargest(10).reset_index()
            fig = px.bar(
                hot, 
                x=temp_col, 
                y=country_col, 
                orientation='h',
                title="🔥 Top 10 Hottest Countries",
                color=temp_col
            )
            fig.show()

        # ----------------------------------------
        # TOP 10 COLDEST COUNTRIES
        # ----------------------------------------
        elif choice == "Top 10 Coldest Countries":
            cold = df.groupby(country_col)[temp_col].mean().nsmallest(10).reset_index()
            fig = px.bar(
                cold, 
                x=temp_col, 
                y=country_col,
                orientation='h',
                title="❄️ Top 10 Coldest Countries",
                color=temp_col
            )
            fig.show()

        # ----------------------------------------
        # COUNTRY WISE TREND
        # ----------------------------------------
        elif choice == "Country-wise Trend":
            country_selector = widgets.Dropdown(
                options=sorted(df[country_col].unique()),
                description="Country:"
            )

            display(country_selector)

            def show_country(change2):
                output.clear_output(wait=True)
                with output:
                    c = change2['new']
                    temp = df[df[country_col] == c].groupby("Year")[temp_col].mean().reset_index()

                    fig = px.line(
                        temp, 
                        x="Year", y=temp_col,
                        title=f"🌍 Temperature Trend — {c}"
                    )
                    fig.show()

            country_selector.observe(show_country, names='value')

        # ----------------------------------------
        # TEMPERATURE HISTOGRAM
        # ----------------------------------------
        elif choice == "Temperature Distribution":
            fig = px.histogram(
                df, 
                x=temp_col,
                nbins=40,
                title="📊 Temperature Distribution"
            )
            fig.show()

# -------------------------------------------------------
# BIND DROPDOWN
# -------------------------------------------------------
dropdown.observe(show_graph, names='value')

# -------------------------------------------------------
# DISPLAY WIDGETS
# -------------------------------------------------------
display(dropdown, output)
