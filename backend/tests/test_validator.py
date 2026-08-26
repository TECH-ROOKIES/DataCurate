import pandas as pd

from backend.services.validator import run_validation


def test_required_field_check():
    df = pd.DataFrame({"name": ["Rahul", None], "email": ["a@b.com", "c@d.com"]})
    result = run_validation(df, {"required": ["name"]})
    assert result["errors"] == 1
    assert result["checks"][0]["status"] == "ERROR"


def test_numeric_field_check():
    df = pd.DataFrame({"age": ["21", "twenty"]})
    result = run_validation(df, {"numeric": ["age"]})
    assert result["errors"] == 1


def test_email_field_check():
    df = pd.DataFrame({"email": ["a@b.com", "not-an-email"]})
    result = run_validation(df, {"email": ["email"]})
    assert result["errors"] == 1


def test_range_field_check():
    df = pd.DataFrame({"age": ["25", "200"]})
    result = run_validation(df, {"range": {"age": [0, 120]}})
    assert result["warnings"] == 1


def test_all_pass_when_clean():
    df = pd.DataFrame(
        {
            "name": ["Rahul", "Priya"],
            "age": ["21", "22"],
            "email": ["rahul@gmail.com", "priya@gmail.com"],
        }
    )
    config = {
        "required": ["name"],
        "numeric": ["age"],
        "email": ["email"],
        "range": {"age": [0, 120]},
    }
    result = run_validation(df, config)
    assert result["errors"] == 0
    assert result["passed"] == 4


def test_auto_detect_config_when_none_given():
    df = pd.DataFrame({"age": ["21", "22"], "email": ["a@b.com", "c@d.com"]})
    result = run_validation(df, None)
    # auto-detected numeric + email columns should each produce a PASS check
    assert result["passed"] == 2
    assert result["errors"] == 0
