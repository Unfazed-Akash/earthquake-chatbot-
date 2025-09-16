# modules/analytics.py
from typing import Optional, Tuple
import pandas as pd

def apply_filters(df: pd.DataFrame,
                  place: Optional[str] = None,
                  year_range: Optional[Tuple[int,int]] = None,
                  mag_op: Optional[str] = None,
                  mag_values: Optional[Tuple[float,float]] = None) -> pd.DataFrame:
    out = df.copy()

    # place filter (substring in 'place')
    if place and "place" in out.columns:
        mask = out["place"].astype(str).str.contains(place, case=False, na=False)
        out = out.loc[mask]

    # year filter
    if year_range:
        y0, y1 = year_range
        if "year" in out.columns:
            out = out[(out["year"] >= y0) & (out["year"] <= y1)]

    # magnitude filter
    if mag_op and "mag" in out.columns:
        if mag_op == "between" and mag_values:
            lo, hi = mag_values
            out = out[(out["mag"] >= lo) & (out["mag"] <= hi)]
        elif mag_values:
            v = mag_values[0]
            if mag_op == ">":
                out = out[out["mag"] > v]
            elif mag_op == ">=":
                out = out[out["mag"] >= v]
            elif mag_op == "<":
                out = out[out["mag"] < v]
            elif mag_op == "<=":
                out = out[out["mag"] <= v]
    return out

def basic_summary(df: pd.DataFrame) -> str:
    parts = []
    parts.append(f"Rows: {len(df)}")
    if "mag" in df.columns and len(df) > 0:
        parts.append(f"Avg Mag: {df['mag'].mean():.2f}")
        parts.append(f"Max Mag: {df['mag'].max():.2f}")
        parts.append(f"Min Mag: {df['mag'].min():.2f}")
    if "depth" in df.columns and df["depth"].notna().any():
        parts.append(f"Avg Depth(km): {df['depth'].mean():.1f}")
    if "place" in df.columns:
        top_place = df["place"].dropna().astype(str).str.split(",").str[-1].str.strip()
        if not top_place.empty:
            parts.append(f"Top region (rough): {top_place.mode().iloc[0]}")
    return " | ".join(parts)

def max_event(df: pd.DataFrame) -> Optional[pd.Series]:
    if "mag" not in df.columns or df["mag"].isna().all():
        return None
    return df.loc[df["mag"].idxmax()]

def min_event(df: pd.DataFrame) -> Optional[pd.Series]:
    if "mag" not in df.columns or df["mag"].isna().all():
        return None
    return df.loc[df["mag"].idxmin()]

def avg_mag(df: pd.DataFrame) -> Optional[float]:
    if "mag" not in df.columns or df["mag"].isna().all():
        return None
    return float(df["mag"].mean())

def count_events(df: pd.DataFrame) -> int:
    return int(len(df))

def counts_by_year(df: pd.DataFrame) -> pd.Series:
    return df.groupby("year").size().sort_index()

def counts_by_month(df: pd.DataFrame) -> pd.Series:
    return df.groupby(["year","month"]).size()
