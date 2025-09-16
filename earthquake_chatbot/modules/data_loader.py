# modules/data_loader.py
import pandas as pd

STANDARD_COLS = {
    "time": ["time", "Time", "date_time", "datetime", "Date", "DateTime"],
    "place": ["place", "Place", "Location", "location", "Region", "region"],
    "latitude": ["latitude", "lat", "Latitude", "Lat"],
    "longitude": ["longitude", "lon", "Longitude", "Long", "Lng"],
    "depth": ["depth", "Depth"],
    "mag": ["mag", "magnitude", "Mag", "Magnitude"],
}

def _map_columns(df: pd.DataFrame) -> pd.DataFrame:
    colmap = {}
    for std, candidates in STANDARD_COLS.items():
        for c in candidates:
            if c in df.columns:
                colmap[c] = std
                break
    # apply map
    df = df.rename(columns=colmap)
    return df

def load_dataframe(path="data/earthquakes.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df = _map_columns(df)

    # parse time
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
    else:
        raise ValueError("No time column found. Please ensure your CSV has a Time column.")

    # cast numeric cols when present
    for col in ["mag", "depth", "latitude", "longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # drop obvious empties
    df = df.dropna(subset=["time"])
    # helpful derived cols
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    df = df.sort_values("time").reset_index(drop=True)
    return df

def dataset_summary(df: pd.DataFrame) -> str:
    start = df["time"].min()
    end = df["time"].max()
    n = len(df)
    cols = ", ".join(df.columns.astype(str).tolist())
    return f"Rows: {n}\nTime range: {start} → {end}\nColumns: {cols}"
