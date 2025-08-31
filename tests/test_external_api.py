from unittest.mock import MagicMock, patch

import pytest

import src.external_api as external_api

# ---------- get_currency_rate ----------


def test_get_currency_rate_success():
    mock_json = {"Valute": {"USD": {"Value": 92.5}}}
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_json

    with patch("requests.get", return_value=mock_response):
        result = external_api.get_currency_rate("USD")
        assert result == {"currency_code": "USD", "rate": 92.5}


def test_get_currency_rate_invalid_code():
    mock_json = {"Valute": {"EUR": {"Value": 100.0}}}
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_json

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="No data for currency"):
            external_api.get_currency_rate("USD")


def test_get_currency_rate_http_error():
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.reason = "Server Error"
    mock_response.json.return_value = {}

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="Failed to get currency rate"):
            external_api.get_currency_rate("USD")


# ---------- get_stock_prices ----------


def test_get_stock_prices_success(monkeypatch):
    mock_json = {
        "data": [
            {"symbol": "AAPL", "close": 150.0},
            {"symbol": "MSFT", "close": 310.0},
        ]
    }
    monkeypatch.setenv("MARKETSTACK_API_KEY", "fake_api_key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_json

    with patch("requests.get", return_value=mock_response):
        result = external_api.get_stock_prices(["AAPL", "MSFT"])
        assert len(result) == 2
        assert result[0]["symbol"] == "AAPL"
        assert result[1]["close"] == 310.0


def test_get_stock_prices_http_error(monkeypatch):
    monkeypatch.setenv("MARKETSTACK_API_KEY", "fake_api_key")

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.reason = "Forbidden"
    mock_response.json.return_value = {}

    with patch("requests.get", return_value=mock_response):
        result = external_api.get_stock_prices(["AAPL"])
        assert result == []
