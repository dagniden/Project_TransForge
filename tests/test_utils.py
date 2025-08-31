from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.utils import filter_last_stocks, filter_top_transactions, get_card_statistics, read_excel, read_json

# -------------------- read_excel --------------------


@patch("pandas.read_excel")
def test_read_excel_success(mock_read_excel):
    mock_df = pd.DataFrame({"col_num": [1, None, 3], "col_str": ["a", None, "c"]})
    mock_read_excel.return_value = mock_df

    result = read_excel("fake.xlsx")
    assert result == [
        {"col_num": 1.0, "col_str": "a"},
        {"col_num": 0.0, "col_str": ""},
        {"col_num": 3.0, "col_str": "c"},
    ]


@patch("pandas.read_excel", side_effect=FileNotFoundError("file not found"))
def test_read_excel_file_not_found(mock_read_excel):
    with pytest.raises(FileNotFoundError):
        read_excel("not_exists.xlsx")


# -------------------- read_json --------------------


@patch("builtins.open", new_callable=MagicMock)
@patch("json.load")
def test_read_json_success(mock_json_load, mock_open):
    mock_json_load.return_value = {"key": "value"}

    result = read_json("fake.json")
    assert result == {"key": "value"}
    mock_open.assert_called_once_with("fake.json", "r", encoding="utf-8")


@patch("builtins.open", side_effect=FileNotFoundError("no file"))
def test_read_json_file_not_found(mock_open):
    with pytest.raises(FileNotFoundError):
        read_json("missing.json")


# -------------------- get_card_statistics --------------------


def test_get_card_statistics_success():
    data = [
        {"Номер карты": "*1111", "Сумма платежа": -100, "Сумма операции": -100, "Кэшбэк": 5},
        {"Номер карты": "*1111", "Сумма платежа": -200, "Сумма операции": -200, "Кэшбэк": 10},
        {"Номер карты": "*2222", "Сумма платежа": 300, "Сумма операции": 300, "Кэшбэк": 0},  # не учитывается
    ]
    result = get_card_statistics(data)
    assert {"last_digits": "1111", "total_spent": 300, "cashback": 15} in result
    assert all("last_digits" in r for r in result)


def test_get_card_statistics_empty():
    result = get_card_statistics([])
    assert result == []


# -------------------- filter_top_transactions --------------------


def test_filter_top_transactions_success():
    data = [
        {"Дата операции": "2024-01-01", "Сумма платежа": -10, "Категория": "Food", "Описание": "Shop"},
        {"Дата операции": "2024-01-02", "Сумма платежа": -50, "Категория": "Tech", "Описание": "Store"},
        {"Дата операции": "2024-01-03", "Сумма платежа": -30, "Категория": "Fun", "Описание": "Game"},
    ]
    result = filter_top_transactions(data)
    assert result[0]["amount"] == -50  # наибольшая по модулю сумма
    assert all("date" in r for r in result)


def test_filter_top_transactions_empty():
    result = filter_top_transactions([])
    assert result == []


# -------------------- filter_last_stocks --------------------


def test_filter_last_stocks_success():
    data = [
        {"symbol": "AAPL", "price_currency": "USD", "high": 150},
        {"symbol": "AAPL", "price_currency": "EUR", "high": 999},  # игнорируется
        {"symbol": "MSFT", "price_currency": "USD", "high": 300},
        {"symbol": "AAPL", "price_currency": "USD", "high": 200},  # дубликат символа
    ]
    result = filter_last_stocks(data, ["AAPL", "MSFT"])
    assert {"stock": "AAPL", "price": 150} in result
    assert {"stock": "MSFT", "price": 300} in result
    assert len(result) == 2  # дубликаты не должны добавляться


def test_filter_last_stocks_not_found():
    data = [{"symbol": "TSLA", "price_currency": "USD", "high": 1000}]
    result = filter_last_stocks(data, ["AAPL"])
    assert result == []
