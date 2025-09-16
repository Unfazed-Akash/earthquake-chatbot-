# modules/chatbot.py
from typing import Tuple
import pandas as pd
from . import nlp, analytics, plots

HELP_TEXT = """
Try queries like:
  • show summary
  • largest earthquake in Japan after 2015
  • count earthquakes in 2020
  • plot trend in Japan between 2010 and 2015 with mag >= 6
  • histogram of magnitude in Chile
  • earthquakes per year in India
  • earthquakes per month with mag between 5 and 6
  • sample
Type 'exit' to quit.
"""

def _format_event(row: pd.Series) -> str:
    if row is None or row.empty:
        return "No event found."
    t = row.get("time", "?")
    m = row.get("mag", "?")
    d = row.get("depth", "?")
    p = row.get("place", "?")
    return f"Time: {t} | Mag: {m} | Depth(km): {d} | Place: {p}"

def handle_query(df: pd.DataFrame, text: str) -> str:
    parsed = nlp.parse_query(text)
    f = parsed.filters
    filtered = analytics.apply_filters(df, f.place, f.year_range, f.mag_op, f.mag_values)

    intent = parsed.intent

    if intent == "summary":
        base = "Dataset summary:\n" + analytics.basic_summary(df)
        if len(filtered) != len(df):
            base += "\n\nFiltered view:\n" + analytics.basic_summary(filtered)
        return base + ("\n\n" + HELP_TEXT)

    if intent == "sample":
        return str(filtered.head(10))

    if intent == "max":
        row = analytics.max_event(filtered)
        return "Largest earthquake:\n" + _format_event(row)

    if intent == "min":
        row = analytics.min_event(filtered)
        return "Smallest earthquake:\n" + _format_event(row)

    if intent == "avg":
        val = analytics.avg_mag(filtered)
        return "Average magnitude: " + (f"{val:.3f}" if val is not None else "N/A")

    if intent == "count":
        c = analytics.count_events(filtered)
        return f"Count: {c}"

    if intent == "plot_trend":
        plots.plot_trend(filtered, title="Magnitude Over Time (filtered)")
        return "📈 Shown: trend of magnitude over time."

    if intent == "hist":
        plots.plot_hist_mag(filtered, bins=30, title="Magnitude Distribution (filtered)")
        return "📊 Shown: histogram of magnitudes."

    if intent == "counts_year":
        s = analytics.counts_by_year(filtered)
        plots.plot_counts(s, title="Earthquakes per Year")
        return "📊 Shown: earthquakes per year."

    if intent == "counts_month":
        s = analytics.counts_by_month(filtered)
        plots.plot_counts(s, title="Earthquakes per Month (year,month)")
        return "📊 Shown: earthquakes per month."

    # fallback
    return "I didn't fully get that. " + HELP_TEXT
