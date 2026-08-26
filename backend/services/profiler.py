"""
Dataset profiling service.

Given a pandas DataFrame (loaded with dtype=str, so every cell is a string
or NaN), produces a structural profile: row/column counts, per-column
inferred type, missing-value counts, duplicate-row counts, and basic
numeric/categorical statistics.
"""
import math

import pandas as pd


def _safe_number(value):
    """Convert numpy/float values to plain, JSON-safe Python types."""
    if value is None:
        return None
    try:
        if isinstance(value, float) and math.isnan(value):
            return None
    except TypeError:
        pass
    if hasattr(value, "item"):
        value = value.item()
    return value


def infer_column_kind(series: pd.Series) -> str:
    """Best-effort classification of a column as 'numeric', 'email', or
    'categorical'. Values are strings (or NaN) because datasets are loaded
    with dtype=str, so we infer intent ourselves rather than trust pandas
    dtypes (which only reflect what pandas could parse, silently)."""
    non_null = series.dropna()
    if non_null.empty:
        return "categorical"

    if "email" in str(series.name).lower():
        return "email"

    numeric_count = 0
    for value in non_null:
        try:
            float(value)
            numeric_count += 1
        except (TypeError, ValueError):
            pass
    if numeric_count / len(non_null) >= 0.8:
        return "numeric"

    return "categorical"


def profile_numeric_column(series: pd.Series) -> dict:
    values = []
    for value in series.dropna():
        try:
            values.append(float(value))
        except (TypeError, ValueError):
            continue
    if not values:
        return {"min": None, "max": None, "mean": None}
    return {
        "min": _safe_number(min(values)),
        "max": _safe_number(max(values)),
        "mean": _safe_number(round(sum(values) / len(values), 4)),
    }


def profile_categorical_column(series: pd.Series, top_n: int = 10) -> dict:
    counts = series.value_counts(dropna=False).head(top_n)
    result = {}
    for key, count in counts.items():
        label = "Missing" if pd.isna(key) else str(key)
        result[label] = int(count)
    return result


def profile_dataset(df: pd.DataFrame) -> dict:
    rows, columns = df.shape

    dtypes = {}
    columns_profile = []
    total_missing = 0

    for column in df.columns:
        series = df[column]
        missing = int(series.isna().sum())
        total_missing += missing
        kind = infer_column_kind(series)
        dtypes[column] = kind

        column_info = {
            "name": column,
            "inferred_type": kind,
            "missing": missing,
            "missing_percent": round((missing / rows) * 100, 2) if rows else 0.0,
        }

        if kind == "numeric":
            column_info["stats"] = profile_numeric_column(series)
        else:
            column_info["top_values"] = profile_categorical_column(series)

        columns_profile.append(column_info)

    duplicates = int(df.duplicated().sum())

    return {
        "rows": rows,
        "columns": columns,
        "missing_values": total_missing,
        "duplicates": duplicates,
        "dtypes": dtypes,
        "columns_profile": columns_profile,
    }
