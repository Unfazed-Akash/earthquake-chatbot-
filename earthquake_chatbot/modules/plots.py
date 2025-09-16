# modules/plots.py
from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd

def _finalize_and_show():
    plt.tight_layout()
    plt.show()

def plot_trend(df: pd.DataFrame, title: str = "Magnitude Over Time"):
    if "time" not in df.columns or "mag" not in df.columns or df.empty:
        print("No data to plot.")
        return
    plt.figure(figsize=(8,4))
    plt.plot(df["time"], df["mag"], marker=".", linewidth=0.8)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Magnitude")
    _finalize_and_show()

def plot_hist_mag(df: pd.DataFrame, bins: int = 30, title: str = "Magnitude Distribution"):
    if "mag" not in df.columns or df.empty:
        print("No data to plot.")
        return
    plt.figure(figsize=(6,4))
    plt.hist(df["mag"].dropna(), bins=bins)
    plt.title(title)
    plt.xlabel("Magnitude")
    plt.ylabel("Frequency")
    _finalize_and_show()

def plot_counts(series: pd.Series, title: str):
    if series.empty:
        print("No data to plot.")
        return
    plt.figure(figsize=(7,4))
    series.plot(kind="bar")
    plt.title(title)
    plt.xlabel(series.index.name if series.index.name else "")
    plt.ylabel("Count")
    _finalize_and_show()
