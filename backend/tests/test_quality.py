import pandas as pd

from backend.services.quality_engine import (
    calculate_completeness,
    calculate_consistency,
    calculate_overall,
    calculate_uniqueness,
    calculate_validity,
)


def test_completeness_perfect():
    df = pd.DataFrame({"a": ["1", "2"], "b": ["3", "4"]})
    assert calculate_completeness(df) == 100.0


def test_completeness_with_missing():
    df = pd.DataFrame({"a": ["1", None], "b": ["3", "4"]})
    assert calculate_completeness(df) == 75.0  # 1 missing of 4 cells


def test_uniqueness_with_duplicates():
    df = pd.DataFrame({"a": ["1", "1", "2"], "b": ["x", "x", "y"]})
    assert calculate_uniqueness(df) == round((2 / 3) * 100, 2)


def test_validity_flags_bad_numeric():
    df = pd.DataFrame({"age": ["21", "22", "twenty"]})
    config = {"numeric": ["age"], "email": [], "range": {}}
    assert calculate_validity(df, config) == round((2 / 3) * 100, 2)


def test_validity_flags_bad_email():
    df = pd.DataFrame({"email": ["a@b.com", "not-an-email"]})
    config = {"numeric": [], "email": ["email"], "range": {}}
    assert calculate_validity(df, config) == 50.0


def test_validity_defaults_to_100_with_no_checkable_columns():
    df = pd.DataFrame({"city": ["Imphal", "Delhi"]})
    config = {"numeric": [], "email": [], "range": {}}
    assert calculate_validity(df, config) == 100.0


def test_consistency_flags_case_variants():
    df = pd.DataFrame({"gender": ["Male", "male", "MALE", "Female"] * 3})
    assert calculate_consistency(df) < 100.0


def test_consistency_perfect_when_uniform():
    df = pd.DataFrame({"gender": ["Male", "Female", "Male", "Female"] * 3})
    assert calculate_consistency(df) == 100.0


def test_overall_weighted_average():
    assert calculate_overall(100, 100, 100, 100) == 100.0
    assert calculate_overall(0, 0, 0, 0) == 0.0
