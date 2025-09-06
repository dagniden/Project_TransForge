import json
import pytest
from datetime import datetime
from unittest.mock import patch

import pandas as pd

import src.views as views


def test_get_greetings_morning() -> None:
    dt = datetime(2025, 1, 1, 8, 0, 0)
    assert views.get_greetings(dt) == "Доброе утро"


def test_get_greetings_day() -> None:
    dt = datetime(2025, 1, 1, 15, 0, 0)
    assert views.get_greetings(dt) == "Добрый день"


def test_get_greetings_evening() -> None:
    dt = datetime(2025, 1, 1, 19, 0, 0)
    assert views.get_greetings(dt) == "Добрый вечер"


def test_get_greetings_night() -> None:
    dt = datetime(2025, 1, 1, 23, 0, 0)
    assert views.get_greetings(dt) == "Доброй ночи"


def test_filter_data_by_month_filters_correctly() -> None:
    dt = datetime(2025, 5, 15, 12, 0, 0)
    data = [
        {"Дата операции": "01.05.2025 10:00:00", "amount": 100},
        {"Дата операции": "20.05.2025 12:00:00", "amount": 200},
        {"Дата операции": "30.04.2025 23:59:59", "amount": 300},
    ]
    result = views.filter_data_by_month(data, dt)
    assert len(result) == 1
    assert all(isinstance(r, dict) for r in result)


def test_filter_data_by_month_empty_result() -> None:
    dt = datetime(2025, 5, 1, 12, 0, 0)
    data = [
        {"Дата операции": "30.04.2025 10:00:00", "amount": 100},
    ]
    result = views.filter_data_by_month(data, dt)
    assert result == []


def test_json_serializer_datetime() -> None:
    dt = datetime(2025, 1, 1, 12, 0, 0)
    assert views.json_serializer(dt) == "2025-01-01 12:00:00"


def test_json_serializer_pandas_timestamp() -> None:
    ts = pd.Timestamp("2025-01-01 12:00:00")
    assert views.json_serializer(ts) == "2025-01-01 12:00:00"


def test_json_serializer_raises_type_error():
    with pytest.raises(TypeError):
        views.json_serializer(123)


@patch("src.views.read_json")
@patch("src.views.filter_top_transactions")
@patch("src.views.get_card_statistics")
@patch("src.views.filter_last_stocks")
@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rate")
def test_get_main_page_success(
        mock_currency, mock_stock_prices, mock_filter_stocks,
        mock_cards, mock_top, mock_read_json
) -> None:
    mock_read_json.return_value = {
        "user_stocks": ["AAPL"],
        "user_currencies": ["USD"],
    }
    mock_cards.return_value = [{"last_digits": "1234", "total_spent": 1000}]
    mock_top.return_value = [{"id": 1, "amount": 500}]
    mock_stock_prices.return_value = [{"ticker": "AAPL", "price": 200}]
    mock_filter_stocks.return_value = [{"ticker": "AAPL", "price": 200}]
    mock_currency.return_value = {"code": "USD", "rate": 90}

    data = [{"Дата операции": "01.09.2025 10:00:00", "amount": 100}]
    result_json = views.get_main_page(data, "2025-09-01 12:00:00")
    result = json.loads(result_json)

    assert "greeting" in result
    assert "cards" in result
    assert "top_transaction" in result
    assert "stock_prices" in result
    assert "currency_rates" in result
    assert result["cards"][0]["total_spent"] == 1000
