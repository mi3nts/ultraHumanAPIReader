import requests
import yaml
from pprint import pprint
import pandas as pd
from datetime import datetime, timedelta
import  os 
import matplotlib.pyplot as plt
import time 
import json
import traceback
import matplotlib.font_manager as fm
import matplotlib as mpl
from matplotlib import font_manager
import matplotlib.font_manager as fm
from cycler import cycler

#Define plotting style
montserrat_path = "Montserrat,Sankofa_Display/Montserrat/static"
font_files = font_manager.findSystemFonts(fontpaths=montserrat_path)
for font_file in font_files:
    font_manager.fontManager.addfont(font_file)


mpl.rcParams.update({
    'font.family': 'Montserrat',
    'font.size': 20,
    'axes.labelsize': 18,
    'xtick.labelsize': 15,
    'ytick.labelsize': 15,
    'xtick.major.size': 3,
    'ytick.major.size': 3,
    'xtick.minor.visible': True,
    'ytick.minor.visible': True,
    'xtick.minor.size': 1,
    'ytick.minor.size': 1,
    'grid.alpha': 0.5,
    'axes.grid': True,
    'grid.linewidth': 2,
    'axes.grid.which': 'both',
    'axes.titleweight': 'bold',
    'axes.titlesize': 18,
    'axes.prop_cycle': cycler('color', ['#3cd184', '#f97171', '#1e81b0', '#66beb2', '#f99192', '#8ad6cc', '#3d6647', '#000080']),
    'image.cmap': 'viridis',
})


metric_types  = ["hr", "temp", "hrv", "steps"]
all_daily_dfs = []

# Helper function to extract each time-series metric
def extract_metric_type_df(metric,metric_type):
        df = pd.DataFrame(metric["object"]["values"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df.set_index("timestamp", inplace=True)
        df.rename(columns={"value": metric_type}, inplace=True)
        df = df.reset_index().rename(columns={"timestamp": "dateTime"})
        df.set_index('dateTime', inplace=True) 
        # print(df.head())
        return df


def extract_metric_df(data):
    metrics   = []
    metricIDS = []
    
    try:
        metricData = data["data"]["metric_data"]
        for metric in metricData:
            metric_type = metric["type"]
            print(f"Checking metric type: {metric_type}")
            # print(metric_type in metric_types)
            if (metric_type in metric_types) and (isinstance(metric.get("object", {}).get("values"), list) and metric["object"]["values"]):
                print(f"Extracting data for metric: {metric_type}")
                metricIDS.append(metric_type)
                metrics.append(extract_metric_type_df(metric,metric_type))
        return metrics,metricIDS
    
    except Exception as e:
        print(f"🚨 An error occurred: {e}")
        traceback.print_exc()

# Load configuration from YAML
config_file = "config.yaml"
with open(config_file, "r") as file:
    config = yaml.safe_load(file)

downloads_folder = config.get("downloadsFolder")
start_date       = config.get("Dates", {}).get("startDate")
end_date         = config.get("Dates", {}).get("endDate")
email            = config.get("UltraHuman", {}).get("email")
token            = config.get("UltraHuman", {}).get("api")

url = "https://partner.ultrahuman.com/api/v1/metrics"
headers = {"Authorization": token}

# Generate date range
start_dt   = datetime.strptime(start_date, "%Y-%m-%d")
end_dt     = datetime.strptime(end_date, "%Y-%m-%d")
date_range = [start_dt + timedelta(days=i) for i in range((end_dt - start_dt).days + 1)]

# Collect all daily dataframes
all_daily_dfs = []

for dt in date_range:
    date_str = dt.strftime("%Y-%m-%d")
    params = {"email": email, "date": date_str}
    print(f"Fetching data for: {date_str}")
    
    response = requests.get(url, headers=headers, params=params)
    # time.sleep(1)  # To avoid hitting rate limits
    if response.status_code != 200:
        print(f"❌ Failed to fetch data for {date_str}: {response.status_code}")
        continue
    print("-------------------")
    
    data = response.json()

    dfMetrics, metricIDS = extract_metric_df(data)

    if metricIDS == metric_types :
        combined = pd.concat(dfMetrics, axis=1, join='outer')
        all_daily_dfs.append(combined)

print("-------------------------")
print("Combined Daily DataFrame:")
combinedDaily = pd.concat(all_daily_dfs)
combinedDaily.head()
combinedDaily.info()
print(combinedDaily)
# Save the DataFrame as CSV
os.makedirs(downloads_folder, exist_ok=True)
print("f{downloads_folder}/time_series_metrics.csv")


combinedDaily.to_csv(downloads_folder +"/time_series_metrics.csv")
combinedDaily.to_pickle(downloads_folder +"/time_series_metrics.pkl")

for column in combinedDaily.columns:
    if combinedDaily[column].notna().sum() > 0:
        
        plt.figure(figsize=(16, 9))
        plotData = combinedDaily[column].dropna()
        plt.plot(plotData.index, plotData.values, label=column)
        plt.title(f"Time Series of {column}",fontsize=25, pad=20)
        plt.xlabel("DateTime", fontsize=25)
        plt.ylabel(column, fontsize=25)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        # Rotate x-axis labels
        plt.xticks(rotation=45)        
        plt.grid(True)
        plt.legend()
        plt.autoscale(enable=True, axis='both', tight=True)
        plt.tight_layout()
        plt.savefig(f"{downloads_folder}/{column}_time_series_plot.png", dpi=300)
        plt.close()