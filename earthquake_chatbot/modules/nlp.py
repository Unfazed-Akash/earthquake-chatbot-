# modules/nlp.py
import re
from dataclasses import dataclass
from typing import Optional, Tuple, List

@dataclass
class QueryFilters:
    place: Optional[str] = None          # e.g., "Japan"
    year_range: Optional[Tuple[int,int]] = None  # (start_year, end_year)
    date_range: Optional[Tuple[str,str]] = None  # ISO strings if provided
    mag_op: Optional[str] = None         # one of: ">", ">=", "<", "<=", "between"
    mag_values: Optional[Tuple[float, float]] = None  # for between or single bound

@dataclass
class ParsedQuery:
    intent: str                          # "summary", "max", "min", "avg", "count", "plot_trend", "hist", "counts_year", "counts_month", "sample"
    filters: QueryFilters
    extras: dict

INTENT_KEYWORDS = [
    ("max", ["largest", "max", "strongest", "highest", "biggest", "most powerful", "most intense", "most severe", "most damaging", "most felt"]),
    ("min", ["smallest", "min", "weakest", "lowest", "least powerful", "least intense", "least severe", "least damaging", "least felt"]),
    ("avg", ["average", "mean", "avg", "mean magnitude", "mean mag", "average mag", "average magnitude",    "mean magnitude", "mean mag", "average magnitude", "average mag", "mean magnitude", "mean mag", "average magnitude", "average mag"]),
    ("count", ["count", "how many", "number of", "total", "sum", "quantity", "total count", "total number", "total sum", "total quantity", "total events", "total earthquakes", "total quakes", "total tremors", "total shocks", "total seismic events", "total seismic activity", "total seismic occurrences"]),
    ("plot_trend", ["plot", "trend", "line", "time series", "time-series", "graph", "chart", "visualization", "visualize", "show trend", "show time series", "show graph", "show chart", "show visualization", "show time-series", "show plot", "show line", "show trend line", "show time series line", "show graph line", "show chart line", "show visualization line", "show time-series line", "show plot line", "show line plot", "show time series plot", "show graph plot", "show chart plot", "show visualization plot", "show time-series plot", "show plot trend", "show time series trend", "show graph trend", "show chart trend", "show visualization trend", "show time-series trend"]),
    ("hist", ["histogram", "hist", "distribution", "bins", "frequency", "freq", "magnitude distribution", "magnitude histogram", "magnitude freq", "magnitude frequency", "magnitude bins", "magnitude distribution histogram", "magnitude distribution freq", "magnitude distribution frequency", "magnitude distribution bins",   "magnitude distribution histogram", "magnitude distribution freq", "magnitude distribution frequency", "magnitude distribution bins"]),
    ("counts_year", ["per year", "yearly", "by year", "counts year", "year counts", "yearly counts", "annual counts", "yearly events", "yearly earthquakes", "yearly quakes", "yearly tremors", "yearly shocks", "yearly seismic events", "yearly seismic activity", "yearly seismic occurrences",  "yearly seismic events", "yearly seismic activity", "yearly seismic occurrences", "yearly seismic events", "yearly seismic activity", "yearly seismic occurrences", "yearly seismic events", "yearly seismic activity", "yearly seismic occurrences"]),
    ("counts_month", ["per month", "monthly", "by month", "counts month", "month counts", "monthly counts", "monthly events", "monthly earthquakes", "monthly quakes", "monthly tremors", "monthly shocks", "monthly seismic events", "monthly seismic activity", "monthly seismic occurrences", "monthly seismic events", "monthly seismic activity", "monthly seismic occurrences", "monthly seismic events", "monthly seismic activity", "monthly seismic occurrences", "monthly seismic events", "monthly seismic activity", "monthly seismic occurrences"]),
    ("sample", ["sample", "head", "preview", "first few", "first rows", "top rows", "top events", "top earthquakes", "top quakes", "top tremors", "top shocks", "top seismic events", "top seismic activity", "top seismic occurrences", "top seismic events", "top seismic activity", "top seismic occurrences", "top seismic events", "top seismic activity", "top seismic occurrences", "top seismic events", "top seismic activity", "top seismic occurrences", "top seismic events", "top seismic activity", "top seismic occurrences", "top seismic events", "top seismic activity", "top seismic occurrences"]),
    ("summary", ["summary", "info", "describe", "dataset", "dataset summary", "data summary", "data info", "data describe", "data overview", "data details", "data statistics", "data stats", "data metrics", "data analysis", "data insights", "data trends", "data patterns", "data distributions", "data characteristics", "data features"]),
]

MONTHS = ("jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december")

def _detect_intent(text: str) -> str:
    t = text.lower()
    for intent, kws in INTENT_KEYWORDS:
        if any(kw in t for kw in kws):
            return intent
    # default
    if "plot" in t or "graph" in t or "chart" in t:
        return "plot_trend"
    return "summary"

def _extract_place(text: str) -> Optional[str]:
    # very simple heuristic: look for 'in <place>' or 'at <place>'
    m = re.search(r"(in|at)\s+([a-zA-Z\s\-]+)", text, re.IGNORECASE)
    if m:
        place = m.group(2).strip()
        # stop words that usually end the place phrase
        place = re.split(r"\s+(after|before|between|with|where|when|and|or|from|to|on)\b", place, flags=re.I)[0].strip()
        return place if place else None
    # also accept plain proper noun if user types only the place, e.g., "Japan"
    tokens = text.strip().split()
    if len(tokens) == 1 and tokens[0].isalpha():
        return tokens[0]
    return None

def _extract_year_range(text: str) -> Optional[Tuple[int,int]]:
    t = text.lower()
    # between 2015 and 2020
    m = re.search(r"between\s+(\d{4})\s+and\s+(\d{4})", t)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return (min(a,b), max(a,b))
    # after 2018
    m = re.search(r"(after|since)\s+(\d{4})", t)
    if m:
        y = int(m.group(2))
        return (y, 9999)
    # before 2015
    m = re.search(r"(before|until)\s+(\d{4})", t)
    if m:
        y = int(m.group(2))
        return (0, y)
    # in 2020
    m = re.search(r"(in|for)\s+(\d{4})", t)
    if m:
        y = int(m.group(2))
        return (y, y)
    return None

def _extract_mag(text: str) -> Tuple[Optional[str], Optional[Tuple[float,float]]]:
    t = text.lower()
    # between 5 and 6
    m = re.search(r"(mag|magnitude)\s*(between|from)\s*(\d+(\.\d+)?)\s*(and|to)\s*(\d+(\.\d+)?)", t)
    if m:
        a = float(m.group(3)); b = float(m.group(6))
        return "between", (min(a,b), max(a,b))
    # >= 6 / > 6 / <= 4 / < 4
    m = re.search(r"(mag|magnitude)\s*(>=|>|<=|<)\s*(\d+(\.\d+)?)", t)
    if m:
        op = m.group(2); val = float(m.group(3))
        return op, (val, val)
    # words: above 6, below 4
    m = re.search(r"(above|over)\s*(\d+(\.\d+)?)", t)
    if m:
        return ">", (float(m.group(2)), float(m.group(2)))
    m = re.search(r"(below|under)\s*(\d+(\.\d+)?)", t)
    if m:
        return "<", (float(m.group(2)), float(m.group(2)))
    return None, None

def parse_query(user_text: str) -> ParsedQuery:
    intent = _detect_intent(user_text)
    place = _extract_place(user_text)
    year_range = _extract_year_range(user_text)
    mag_op, mag_values = _extract_mag(user_text)

    return ParsedQuery(
        intent=intent,
        filters=QueryFilters(
            place=place,
            year_range=year_range,
            mag_op=mag_op,
            mag_values=mag_values
        ),
        extras={}
    )
