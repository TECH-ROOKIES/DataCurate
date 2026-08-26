import pandas as pd

from backend.services.cleaner import clean_dataset


def test_whitespace_is_stripped():
    df = pd.DataFrame({"name": [" Rahul ", "Priya"]})
    cleaned, summary = clean_dataset(df)
    assert cleaned["name"].tolist() == ["Rahul", "Priya"]
    assert summary["whitespace_fixed"] == 1


def test_missing_tokens_normalized():
    # A distinguishing "id" column keeps these rows from being collapsed
    # by duplicate-removal once their "city" values all become missing.
    df = pd.DataFrame(
        {
            "id": ["1", "2", "3", "4"],
            "city": ["Imphal", "N/A", "na", " "],
        }
    )
    cleaned, summary = clean_dataset(df)
    assert summary["missing_values_normalized"] == 3  # "N/A", "na", and " " (post-strip: "")
    assert cleaned["city"].isna().sum() == 3
    assert cleaned["city"].iloc[0] == "Imphal"


def test_duplicates_removed():
    df = pd.DataFrame({"name": ["Rahul", "Rahul", "Priya"], "age": ["21", "21", "22"]})
    cleaned, summary = clean_dataset(df)
    assert summary["duplicates_removed"] == 1
    assert len(cleaned) == 2


def test_gender_standardized():
    df = pd.DataFrame({"gender": ["male", "MALE", "Male"]})
    cleaned, summary = clean_dataset(df)
    assert cleaned["gender"].tolist() == ["Male", "Male", "Male"]
    assert summary["standardized_fields"] == 2


def test_does_not_invent_values_for_invalid_numeric():
    # Cleaning should never silently "fix" a bad numeric value -- that's
    # the validator's job to flag, not the cleaner's job to guess.
    df = pd.DataFrame({"age": ["21", "twenty"]})
    cleaned, _ = clean_dataset(df)
    assert cleaned["age"].tolist() == ["21", "twenty"]
