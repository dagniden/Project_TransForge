# tests/test_views.py

import json
from datetime import datetime
from unittest.mock import patch

import pytest

from src.views import get_greetings, get_main_page

# ----------------------
# Тесты для get_greetings
# ----------------------


@pytest.mark.parametrize(
    "hour,expected",
    [
        (6, "Доброе утро"),
        (13, "Добрый день"),
        (19, "Добрый вечер"),
        (22, "Доброй ночи"),
    ],
)
def test_get_greetings(hour: int, expected: str) -> None:
    dt = datetime(2025, 8, 31, hour, 0, 0)
    assert get_greetings(dt) == expected


# ----------------------
# Тесты для get_main_page
# ----------------------


@patch("src.views.read_json")
@patch("src.views.get_card_statistics")
@patch("src.views.filter_top_transactions")
@patch("src.views.get_stock_prices")
@patch("src.views.filter_last_stocks")
@patch("src.views.get_currency_rate")
def test_get_main_page_success(
    mock_get_currency_rate,
    mock_filter_last_stocks,
    mock_get_stock_prices,
    mock_filter_top_transactions,
    mock_get_card_statistics,
    mock_read_json,
):
    # Настройка моков
    mock_read_json.return_value = {"user_stocks": ["AAPL", "GOOG"], "user_currencies": ["USD", "EUR"]}
    mock_get_card_statistics.return_value = [{"card": "1234", "sum": -100}]
    mock_filter_top_transactions.return_value = [{"id": 1, "amount": -50}]
    mock_get_stock_prices.return_value = [{"symbol": "AAPL", "price": 150}]
    mock_filter_last_stocks.return_value = [{"symbol": "AAPL", "price": 150}]
    mock_get_currency_rate.side_effect = [75.0, 85.0]

    data = [{"Сумма платежа": -100, "Сумма операции": -100, "Кэшбэк": 0}]
    dt_str = "2025-08-31 10:00:00"

    result_json = get_main_page(data, dt_str)
    result = json.loads(result_json)

    # Проверка содержимого
    assert result["greeting"] == "Доброе утро"
    assert result["cards"] == [{"card": "1234", "sum": -100}]
    assert result["top_transaction"] == [{"id": 1, "amount": -50}]
    assert result["stock_prices"] == [{"symbol": "AAPL", "price": 150}]
    assert result["currency_rates"] == [75.0, 85.0]


def test_get_main_page_handles_stock_error() -> None:
    with patch("src.views.read_json", return_value={"user_stocks": ["AAPL"], "user_currencies": []}), patch(
        "src.views.get_card_statistics", return_value=[]
    ), patch("src.views.filter_top_transactions", return_value=[]), patch(
        "src.views.get_stock_prices", side_effect=Exception("API Error")
    ):
        data = []
        dt_str = "2025-08-31 10:00:00"
        result_json = get_main_page(data, dt_str)
        result = json.loads(result_json)
        # Проверка, что при ошибке получения акций функция возвращает пустой список
        assert result["stock_prices"] == []


def test_get_main_page_handles_currency_error() -> None:
    with patch("src.views.read_json", return_value={"user_stocks": [], "user_currencies": ["USD"]}), patch(
        "src.views.get_card_statistics", return_value=[]
    ), patch("src.views.filter_top_transactions", return_value=[]), patch(
        "src.views.get_stock_prices", return_value=[]
    ), patch(
        "src.views.get_currency_rate", side_effect=Exception("API Error")
    ):
        data = []
        dt_str = "2025-08-31 10:00:00"
        result_json = get_main_page(data, dt_str)
        result = json.loads(result_json)
        # Проверка, что при ошибке получения валюты функция возвращает пустой список
        assert result["currency_rates"] == []
