import pandas as pd
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display

# -----------------------------
# LOAD DATA
# -----------------------------
# ✅ Update this with your correct ZIP/CSV file path
# Example: GlobalLandTemperaturesByCity.csv inside ZIP
temp_url = (r"C:\Users\amrut\Downloads\GlobalLandTemperaturesByCity.csv (1).zip")

df = pd.read_csv(temp_url)

# Convert date column to datetime and extract year
df['dt'] = pd.to_datetime(df['dt'], errors='coerce')
df['Year'] = df['dt'].dt.year

# Drop nulls for safety
df = df.dropna(subset=['AverageTemperature', 'Country'])

# -----------------------------
# DROPDOWN WIDGET
# -----------------------------
dropdown = widgets.Dropdown(
    options=[
        "Select...",
        "Global Temperature Trend",
        "Top 10 Hottest Countries",
        "Top 10 Coldest Countries",
        "Country-wise Temperature Trend",
        "Histogram of Global Temperatures"
    ],
    description="📊 View:",
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='65%')
)

output = widgets.Output()

# -----------------------------
# FUNCTIONS FOR EACH GRAPH
# -----------------------------

def show_graph(change):
    output.clear_output()
    choice = change['new']

    with output:

        # ---------------------------------------
        # 1️⃣ GLOBAL TEMPERATURE TREND
        # ---------------------------------------
        if choice == "Global Temperature Trend":
            global_temp = df.groupby("Year")['AverageTemperature'].mean().reset_index()

            fig = px.line(
                global_temp,
                x='Year',
                y='AverageTemperature',
                title='🌡️ Global Average Temperature Trend (Yearly)',
                color_discrete_sequence=["firebrick"]
            )
            fig.update_layout(yaxis_title="Average Temperature (°C)")
            fig.show()

        # ---------------------------------------
        # 2️⃣ TOP 10 HOTTEST COUNTRIES
        # ---------------------------------------
        elif choice == "Top 10 Hottest Countries":
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
            fig.show()

        # ---------------------------------------
        # 3️⃣ TOP 10 COLDEST COUNTRIES
        # ---------------------------------------
        elif choice == "Top 10 Coldest Countries":
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
            fig.show()

        # ---------------------------------------
        # 4️⃣ COUNTRY-WISE TEMPERATURE TREND
        # ---------------------------------------
        elif choice == "Country-wise Temperature Trend":
            country_list = sorted(df['Country'].unique())

            country_dd = widgets.Dropdown(
                options=country_list,
                description="🌎 Country:",
                layout=widgets.Layout(width='50%')
            )
            out2 = widgets.Output()

            def plot_country(c_change):
                out2.clear_output()
                with out2:
                    selected = c_change['new']
                    country_df = df[df['Country'] == selected]
                    trend = country_df.groupby('Year')['AverageTemperature'].mean().reset_index()

                    fig = px.line(
                        trend,
                        x='Year',
                        y='AverageTemperature',
                        title=f'🌍 Temperature Trend of {selected}',
                        color_discrete_sequence=["green"]
                    )
                    fig.update_layout(yaxis_title="Average Temperature (°C)")
                    fig.show()

            country_dd.observe(plot_country, names='value')
            display(country_dd, out2)

        # ---------------------------------------
        
        # 6️⃣ HISTOGRAM OF GLOBAL TEMPERATURES
        # ---------------------------------------
        elif choice == "Histogram of Global Temperatures":
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
            fig.show()

# Attach observer and display
dropdown.observe(show_graph, names='value')
display(dropdown, output)
