import json
import os
from unittest.mock import patch

import pandas as pd
import pytest

from src import reports

# ---------- write_report ----------


def test_write_report_success(tmp_path, test_dataframe):
    filename = tmp_path / "test.xlsx"
    reports.write_report(str(filename), test_dataframe)
    assert os.path.exists(filename)


# def test_write_report_failure(tmp_path, test_dataframe):
#     bad_filename = tmp_path / "nonexistent_dir" / "test.xlsx"
#
#     with pytest.raises(FileNotFoundError):
#         reports.write_report(str(bad_filename), test_dataframe)


# ---------- spending_by_category ----------


@patch("src.reports.search_transactions")
def test_spending_by_category_success(mock_search, test_dataframe):
    mock_search.return_value = json.dumps(
        [
            {"Дата операции": "2025-06-01 10:00:00", "Категория": "Еда", "Сумма платежа": -100},
            {"Дата операции": "2025-08-20 15:30:00", "Категория": "Еда", "Сумма платежа": -200},
        ]
    )

    result = reports.spending_by_category(test_dataframe, category="Еда", date="2025-08-30")

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert all(result["Категория"] == "Еда")
    assert len(result) == 2


@patch("src.reports.search_transactions")
def test_spending_by_category_empty(mock_search, test_dataframe):
    mock_search.return_value = json.dumps([])
    result = reports.spending_by_category(test_dataframe, category="Развлечения", date="2025-08-30")
    assert result.empty


@patch("src.reports.search_transactions")
def test_spending_by_category_invalid_date(test_dataframe):
    with pytest.raises(ValueError):
        reports.spending_by_category(test_dataframe, category="Еда", date="invalid-date")


@patch("src.reports.search_transactions")
def test_spending_by_category_search_raises(mock_search, test_dataframe):
    mock_search.side_effect = Exception("API error")
    with pytest.raises(Exception, match="API error"):
        reports.spending_by_category(test_dataframe, category="Еда", date="2025-08-30")


# ---------- save_report (декоратор) ----------


def test_save_report_decorator(tmp_path, test_dataframe):
    @reports.save_report(str(tmp_path / "decorator_test.xlsx"))
    def dummy_func():
        return test_dataframe

    result = dummy_func()
    assert isinstance(result, pd.DataFrame)

    # Проверяем, что файл реально создался
    files = list(tmp_path.iterdir())
    assert any(file.suffix == ".xlsx" for file in files)
