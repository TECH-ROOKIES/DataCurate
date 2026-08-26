import pandas as pd

from backend.services.profiler import profile_dataset


def make_df():
    return pd.DataFrame(
        {
            "name": ["Rahul", "Priya", "Amit", None],
            "age": ["21", "22", "twenty", "24"],
            "email": ["rahul@gmail.com", "priya@gmail", "amit@gmail.com", "john@gmail.com"],
        }
    )


def test_row_and_column_count():
    profile = profile_dataset(make_df())
    assert profile["rows"] == 4
    assert profile["columns"] == 3


def test_missing_values_detected():
    profile = profile_dataset(make_df())
    assert profile["missing_values"] == 1  # the single None in "name"


def test_duplicate_detection():
    df = pd.DataFrame({"a": ["1", "1", "2"], "b": ["x", "x", "y"]})
    profile = profile_dataset(df)
    assert profile["duplicates"] == 1


def test_numeric_column_inferred_and_stats():
    df = pd.DataFrame({"age": ["21", "22", "23", "24"]})
    profile = profile_dataset(df)
    column = profile["columns_profile"][0]
    assert column["inferred_type"] == "numeric"
    assert column["stats"]["min"] == 21
    assert column["stats"]["max"] == 24


def test_email_column_inferred_by_name():
    df = pd.DataFrame({"email": ["a@b.com", "c@d.com"]})
    profile = profile_dataset(df)
    assert profile["columns_profile"][0]["inferred_type"] == "email"
