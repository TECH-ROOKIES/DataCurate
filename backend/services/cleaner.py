"""
Cleaning service.

Applies a small, explicit set of cleaning rules to a DataFrame and returns
both the cleaned DataFrame and a summary describing exactly what changed
(the summary feeds directly into the provenance/curation-history log).

Deliberately conservative: no rule here invents or guesses a corrected
value (e.g. "twenty" is never turned into 20) -- that is the validator's
job to flag, not the cleaner's job to fix.
"""
import pandas as pd
from pandas.api.types import is_string_dtype

from backend.utils.validators import is_missing_token

# Small, explicit standardization map rather than a generic "title case
# everything" rule, per the "do not silently guess" principle. Extend this
# per-field as your dataset's controlled vocabulary needs it.
STANDARDIZATION_RULES = {
    "gender": {
        "male": "Male",
        "female": "Female",
        "other": "Other",
    },
}


def _strip_whitespace(df: pd.DataFrame) -> int:
    fixed = 0

    def strip_value(value):
        nonlocal fixed
        if isinstance(value, str):
            stripped = value.strip()
            if stripped != value:
                fixed += 1
            return stripped
        return value

    for column in df.columns:
        # is_string_dtype() covers both legacy 'object' text columns and
        # pandas' newer dedicated string dtype -- checking dtype == object
        # alone silently skips every column on pandas >= 2.x/3.x, where
        # text columns no longer default to 'object'.
        if not is_string_dtype(df[column]):
            continue
        df[column] = df[column].apply(strip_value)
    return fixed


def _normalize_missing_tokens(df: pd.DataFrame) -> int:
    normalized = 0

    def replace(value):
        nonlocal normalized
        if isinstance(value, str) and is_missing_token(value):
            normalized += 1
            return None
        return value

    for column in df.columns:
        if not is_string_dtype(df[column]):
            continue
        df[column] = df[column].apply(replace)
    return normalized


def _remove_duplicates(df: pd.DataFrame) -> tuple:
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    after = len(df)
    return df, before - after


def _standardize_fields(df: pd.DataFrame) -> int:
    standardized = 0

    for column, mapping in STANDARDIZATION_RULES.items():
        if column not in df.columns:
            continue

        def apply_rule(value):
            nonlocal standardized
            if not isinstance(value, str):
                return value
            key = value.strip().lower()
            if key in mapping and value != mapping[key]:
                standardized += 1
                return mapping[key]
            return value

        df[column] = df[column].apply(apply_rule)

    return standardized


def clean_dataset(df: pd.DataFrame) -> tuple:
    """Apply cleaning rules in a fixed order and return (clean_df, summary).

    Order matters: whitespace is stripped and missing tokens normalized
    *before* duplicate detection, so that " Male " and "Male" are treated
    as the same row when they should be.
    """
    df = df.copy()

    whitespace_fixed = _strip_whitespace(df)
    missing_normalized = _normalize_missing_tokens(df)
    df, duplicates_removed = _remove_duplicates(df)
    standardized_fields = _standardize_fields(df)

    summary = {
        "duplicates_removed": duplicates_removed,
        "whitespace_fixed": whitespace_fixed,
        "missing_values_normalized": missing_normalized,
        "standardized_fields": standardized_fields,
    }
    return df, summary
