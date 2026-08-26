"""
Low-level, reusable validation predicates.

These are plain helper functions with no knowledge of DataFrames, HTTP, or
the database. The business rules that decide *which* columns to check with
these live in services/validator.py and services/quality_engine.py.
"""
import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Extra missing-value representations to normalize during cleaning, beyond
# what pandas already recognizes as NA when it parses a CSV.
MISSING_TOKENS = {"", " ", "na", "n/a", "null", "none", "-", "--"}


def is_valid_email(value) -> bool:
    """Checks basic email *format* only -- this does not verify the address
    actually exists or is reachable."""
    if value is None:
        return False
    return bool(EMAIL_REGEX.match(str(value).strip()))


def is_numeric_value(value) -> bool:
    if value is None:
        return False
    try:
        float(str(value).strip())
        return True
    except ValueError:
        return False


def is_missing_token(value) -> bool:
    if value is None:
        return True
    return str(value).strip().lower() in MISSING_TOKENS
