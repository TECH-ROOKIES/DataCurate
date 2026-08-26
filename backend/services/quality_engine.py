"""
Quality engine.

Implements the four quality dimensions required by the project scope
(completeness, uniqueness, validity, consistency) plus a weighted overall
score. These formulas are this prototype's own scoring model -- not a
claim of any industry standard. That distinction is worth making clearly
in a viva.
"""
import pandas as pd

from backend.services.validator import auto_detect_config, get_invalid_cell_counts

WEIGHTS = {
    "completeness": 0.30,
    "uniqueness": 0.25,
    "validity": 0.25,
    "consistency": 0.20,
}


def calculate_completeness(df: pd.DataFrame) -> float:
    total_cells = df.shape[0] * df.shape[1]
    if total_cells == 0:
        return 0.0
    missing = int(df.isna().sum().sum())
    return round(((total_cells - missing) / total_cells) * 100, 2)


def calculate_uniqueness(df: pd.DataFrame) -> float:
    total_rows = df.shape[0]
    if total_rows == 0:
        return 0.0
    unique_rows = df.drop_duplicates().shape[0]
    return round((unique_rows / total_rows) * 100, 2)


def calculate_validity(df: pd.DataFrame, config: dict = None) -> float:
    invalid, checked = get_invalid_cell_counts(df, config)
    if checked == 0:
        # No numeric/email/range rules applied to anything -- treat as fully
        # valid rather than penalizing datasets with no rule-checkable columns.
        return 100.0
    return round(((checked - invalid) / checked) * 100, 2)


def calculate_consistency(df: pd.DataFrame) -> float:
    """Flags values that share a normalized (lowercased, trimmed) form but
    are represented inconsistently, e.g. 'Male' / 'MALE' / ' male'.
    Columns that look like free text or identifiers (mostly-unique values)
    are skipped, since case/whitespace variation there isn't meaningful."""
    inconsistent = 0
    total_text_values = 0

    for column in df.columns:
        series = df[column].dropna()
        if series.empty:
            continue
        if series.nunique() / len(series) > 0.5:
            continue

        total_text_values += len(series)

        variants_by_key = {}
        for value in series:
            key = str(value).strip().lower()
            variants_by_key.setdefault(key, set()).add(str(value))

        inconsistent_keys = {k for k, v in variants_by_key.items() if len(v) > 1}
        if not inconsistent_keys:
            continue

        for value in series:
            if str(value).strip().lower() in inconsistent_keys:
                inconsistent += 1

    if total_text_values == 0:
        return 100.0
    return round(((total_text_values - inconsistent) / total_text_values) * 100, 2)


def calculate_overall(completeness: float, uniqueness: float, validity: float, consistency: float) -> float:
    score = (
        WEIGHTS["completeness"] * completeness
        + WEIGHTS["uniqueness"] * uniqueness
        + WEIGHTS["validity"] * validity
        + WEIGHTS["consistency"] * consistency
    )
    return round(max(0.0, min(100.0, score)), 2)


def calculate_quality(df: pd.DataFrame, config: dict = None) -> dict:
    if config is None:
        config = auto_detect_config(df)

    completeness = calculate_completeness(df)
    uniqueness = calculate_uniqueness(df)
    validity = calculate_validity(df, config)
    consistency = calculate_consistency(df)
    overall = calculate_overall(completeness, uniqueness, validity, consistency)

    return {
        "completeness": completeness,
        "uniqueness": uniqueness,
        "validity": validity,
        "consistency": consistency,
        "overall": overall,
    }
