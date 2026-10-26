
from pathlib import Path
import pandas as pd

path = Path("data/raw/weather/open-meteo-40.74N74.04W32m.csv")

# Read the CSV using its actual header row.
df = pd.read_csv(path, skiprows=2, header=0)

# Remove completely empty columns, including the trailing empty column.
df = df.dropna(axis=1, how="all")

df.columns = [str(c).strip() for c in df.columns]

print("\n=== WEATHER DATA OVERVIEW ===")
print("Rows:", len(df))
print("Columns:", df.columns.tolist())

# Parse timestamp
df["time"] = pd.to_datetime(df["time"], errors="coerce")

weather_columns = [
    "temperature_2m (°C)",
    "relative_humidity_2m (%)",
    "precipitation (mm)",
    "wind_speed_10m (km/h)",
]

for column in weather_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

print("\n=== DATE RANGE ===")
print("First:", df["time"].min())
print("Last:", df["time"].max())

print("\n=== MISSING VALUES ===")
print(df.isna().sum().to_string())

print("\n=== DUPLICATE TIMESTAMPS ===")
print(df["time"].duplicated().sum())

print("\n=== FIRST FIVE OBSERVATIONS ===")
print(df.head().to_string(index=False))

print("\n=== WEATHER SUMMARY ===")
print(df[weather_columns].describe().round(2).to_string())
