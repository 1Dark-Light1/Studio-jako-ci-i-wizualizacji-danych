import tempfile
from pathlib import Path

import pandas as pd

from src.data_session import DataSession
from src.visualization import bar_figure, box_figure, histogram_figure, scatter_figure


def make_session() -> DataSession:
    return DataSession(pd.DataFrame({
        "id": [1, 2, 2, 3, 4],
        "value": [10.0, None, None, 30.0, 1000.0],
        "group": ["A", "B", "B", "A", "C"],
    }))


def test_from_csv_accepts_comma_and_semicolon(tmp_path):
    comma = tmp_path / "comma.csv"
    comma.write_text("id,value\n1,10\n2,20\n", encoding="utf-8")
    semicolon = tmp_path / "semicolon.csv"
    semicolon.write_text("id;value\n1;10\n2;20\n", encoding="utf-8")

    assert DataSession.from_csv(comma).shape() == (2, 2)
    assert DataSession.from_csv(semicolon).shape() == (2, 2)


def test_profile_missing_duplicate_and_unique():
    session = make_session()
    profile = session.profile()

    assert int(profile.loc["value", "braki"]) == 2
    assert session.count_duplicates() == 1
    assert int(profile.loc["id", "unikalne"]) == 4


def test_missing_median_duplicate_reset_and_export():
    session = make_session()
    changed = session.impute_missing("value", "median")
    assert changed == 2
    assert session.current["value"].isna().sum() == 0

    removed = session.drop_duplicates()
    assert removed == 1
    session.reset()
    assert len(session.current) == 5
    assert session.current["value"].isna().sum() == 2

    with tempfile.TemporaryDirectory() as directory:
        csv_path = Path(directory) / "clean.csv"
        report_path = Path(directory) / "report.csv"
        session.export_csv(csv_path)
        session.export_report(report_path)
        assert pd.read_csv(csv_path).shape == (5, 3)
        assert pd.read_csv(report_path).shape[0] >= 1


def test_range_outlier_mark_remove_and_clamp():
    session = DataSession(pd.DataFrame({
        "value": [1.0, 2.0, 3.0, 4.0, 100.0],
    }))
    assert session.range_report("value", 0.0, 10.0) == 1
    assert "value_poza_zakresem" not in session.current
    assert session.apply_range("value", 0.0, 10.0, "mark") == 1
    assert "value_poza_zakresem" in session.current

    session.reset()
    assert session.apply_range("value", 0.0, 10.0, "clamp") == 1
    assert session.current["value"].max() == 10.0

    session.reset()
    assert session.apply_outliers("value", 1.5, "remove") == 1
    assert len(session.current) == 4


def test_invalid_numeric_conversion_and_missing_imputation():
    session = DataSession(pd.DataFrame({
        "value": ["10", "abc", None, "30"],
        "group": ["A", None, "A", "B"],
    }))
    assert session.convert_numeric("value") == 1
    assert session.impute_missing("group", "mode") == 1
    assert session.current["group"].isna().sum() == 0


def test_all_four_visualizations():
    session = make_session()
    assert histogram_figure(session, "value").axes
    assert scatter_figure(session, "id", "value").axes
    assert box_figure(session, "value").axes
    assert bar_figure(session, "group").axes
