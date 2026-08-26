"""
Validation service.

Runs a configurable set of rule-based checks against a dataset and reports
structured pass/warning/error results (POST /dataset/{id}/validate). This
module also powers the "validity" dimension of the quality engine.

A validation config looks like:
{
    "required": ["name", "email"],
    "numeric": ["age"],
    "range": {"age": [0, 120]},
    "email": ["email"]
}

If no config is supplied, columns are auto-classified with
infer_column_kind() so the MVP still produces a sane result on an
unfamiliar dataset. Per the project's "do not silently guess" principle,
these checks only ever *report* problems -- they never rewrite values.
"""
import pandas as pd

from backend.services.profiler import infer_column_kind
from backend.utils.validators import is_valid_email, is_numeric_value


def auto_detect_config(df: pd.DataFrame) -> dict:
    config = {"required": [], "numeric": [], "range": {}, "email": []}
    for column in df.columns:
        kind = infer_column_kind(df[column])
        if kind == "numeric":
            config["numeric"].append(column)
        elif kind == "email":
            config["email"].append(column)
    return config


def _check_required(df: pd.DataFrame, column: str) -> dict:
    missing = int(df[column].isna().sum())
    if missing == 0:
        return {"name": f"Required field: {column}", "status": "PASS", "message": "No missing values."}
    return {
        "name": f"Required field: {column}",
        "status": "ERROR",
        "message": f"{missing} missing value(s) found.",
    }


def _check_numeric(df: pd.DataFrame, column: str):
    non_null = df[column].dropna()
    invalid = [v for v in non_null if not is_numeric_value(v)]
    if not invalid:
        result = {"name": f"Numeric format: {column}", "status": "PASS", "message": "All values are numeric."}
    else:
        result = {
            "name": f"Numeric format: {column}",
            "status": "ERROR",
            "message": f"{len(invalid)} non-numeric value(s) found (e.g. '{invalid[0]}').",
        }
    return result, len(invalid), len(non_null)


def _check_email(df: pd.DataFrame, column: str):
    non_null = df[column].dropna()
    invalid = [v for v in non_null if not is_valid_email(v)]
    if not invalid:
        result = {
            "name": f"Email format: {column}",
            "status": "PASS",
            "message": "All values look like valid email addresses.",
        }
    else:
        result = {
            "name": f"Email format: {column}",
            "status": "ERROR",
            "message": f"{len(invalid)} invalid email value(s) found (e.g. '{invalid[0]}').",
        }
    return result, len(invalid), len(non_null)


def _check_range(df: pd.DataFrame, column: str, low: float, high: float):
    non_null = df[column].dropna()
    out_of_range = 0
    checked = 0
    for value in non_null:
        if not is_numeric_value(value):
            continue
        checked += 1
        if float(value) < low or float(value) > high:
            out_of_range += 1

    if checked == 0:
        result = {
            "name": f"Range check: {column}",
            "status": "WARNING",
            "message": "No numeric values available to check.",
        }
    elif out_of_range == 0:
        result = {
            "name": f"Range check: {column}",
            "status": "PASS",
            "message": f"All values fall within [{low}, {high}].",
        }
    else:
        result = {
            "name": f"Range check: {column}",
            "status": "WARNING",
            "message": f"{out_of_range} value(s) fall outside [{low}, {high}].",
        }
    return result, out_of_range, checked


def run_validation(df: pd.DataFrame, config: dict = None) -> dict:
    """Run every configured check and return a structured summary."""
    if not config:
        config = auto_detect_config(df)

    checks = []

    for column in config.get("required") or []:
        if column in df.columns:
            checks.append(_check_required(df, column))

    for column in config.get("numeric") or []:
        if column in df.columns:
            result, _, _ = _check_numeric(df, column)
            checks.append(result)

    for column in config.get("email") or []:
        if column in df.columns:
            result, _, _ = _check_email(df, column)
            checks.append(result)

    for column, bounds in (config.get("range") or {}).items():
        if column in df.columns and len(bounds) == 2:
            result, _, _ = _check_range(df, column, bounds[0], bounds[1])
            checks.append(result)

    passed = sum(1 for c in checks if c["status"] == "PASS")
    warnings = sum(1 for c in checks if c["status"] == "WARNING")
    errors = sum(1 for c in checks if c["status"] == "ERROR")

    return {"passed": passed, "warnings": warnings, "errors": errors, "checks": checks}


def get_invalid_cell_counts(df: pd.DataFrame, config: dict = None) -> tuple:
    """Used by the quality engine to score the 'validity' dimension.
    Returns (invalid_cells, checked_cells) across numeric, email, and range
    rules. Required-field checks are intentionally excluded here because
    missing values are already scored by the 'completeness' dimension."""
    if not config:
        config = auto_detect_config(df)

    invalid_total = 0
    checked_total = 0

    for column in config.get("numeric") or []:
        if column in df.columns:
            _, invalid, checked = _check_numeric(df, column)
            invalid_total += invalid
            checked_total += checked

    for column in config.get("email") or []:
        if column in df.columns:
            _, invalid, checked = _check_email(df, column)
            invalid_total += invalid
            checked_total += checked

    for column, bounds in (config.get("range") or {}).items():
        if column in df.columns and len(bounds) == 2:
            _, invalid, checked = _check_range(df, column, bounds[0], bounds[1])
            invalid_total += invalid
            checked_total += checked

    return invalid_total, checked_total
