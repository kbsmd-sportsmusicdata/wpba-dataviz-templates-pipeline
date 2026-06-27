"""Explainable player role labels for WPBA social templates."""

from __future__ import annotations

import pandas as pd


SMALL_SAMPLE_MINUTES = 40


ROLE_FIELDS = [
    ("Volume Scorer", "percentile_scoring"),
    ("Efficiency Finisher", "percentile_efficiency"),
    ("Rim Pressure Creator", "percentile_rim_pressure"),
    ("Floor Spacer", "percentile_spacing"),
    ("Connector", "percentile_playmaking"),
    ("Defensive Disruptor", "percentile_defense"),
    ("Glass Cleaner", "percentile_rebounding"),
]


def assign_role_label(row: pd.Series, small_sample_minutes: float = SMALL_SAMPLE_MINUTES) -> str:
    total_minutes = pd.to_numeric(row.get("total_minutes"), errors="coerce")
    if pd.isna(total_minutes) or total_minutes < small_sample_minutes:
        return "Small Sample Contributor"

    usage = pd.to_numeric(row.get("usage_pct"), errors="coerce")
    ppsa = pd.to_numeric(row.get("ppsa"), errors="coerce")
    ast_tov = pd.to_numeric(row.get("ast_tov_ratio"), errors="coerce")

    adjusted = {}
    for label, field in ROLE_FIELDS:
        value = pd.to_numeric(row.get(field), errors="coerce")
        adjusted[label] = -1 if pd.isna(value) else float(value)

    if adjusted["Volume Scorer"] >= 70 and (pd.isna(usage) or usage >= 0.2):
        return "Volume Scorer"
    if adjusted["Efficiency Finisher"] >= 70 and (pd.isna(ppsa) or ppsa >= 1.0):
        return "Efficiency Finisher"
    if adjusted["Connector"] >= 70 and (pd.isna(ast_tov) or ast_tov >= 1.5):
        return "Connector"

    label = max(adjusted, key=adjusted.get)
    if adjusted[label] < 60:
        return "Balanced Contributor"
    return label


def add_role_labels(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["player_role_label"] = result.apply(assign_role_label, axis=1)
    return result
