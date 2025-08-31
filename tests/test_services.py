import json
from unittest.mock import patch

import pytest

from src.services import analyze_cashback, search_transactions, search_transactions_by_phone, search_transactions_p2p

# ----------------------
# Тесты analyze_cashback
# ----------------------


def test_analyze_cashback_success():
    data = [
        {"Дата операции": "01.08.2025 12:00:00", "Категория": "Еда", "Бонусы (включая кэшбэк)": 50},
        {"Дата операции": "02.08.2025 13:00:00", "Категория": "Транспорт", "Бонусы (включая кэшбэк)": 30},
        {"Дата операции": "03.08.2025 14:00:00", "Категория": "Еда", "Бонусы (включая кэшбэк)": 20},
    ]
    result_json = analyze_cashback(data, 2025, 8)
    result = json.loads(result_json)
    assert result == {"Еда": 70, "Транспорт": 30}


def test_analyze_cashback_no_data_for_month():
    data = [{"Дата операции": "01.07.2025 12:00:00", "Категория": "Еда", "Бонусы (включая кэшбэк)": 50}]
    result_json = analyze_cashback(data, 2025, 8)
    result = json.loads(result_json)
    assert result == {}


def test_analyze_cashback_invalid_date_format():
    data = [{"Дата операции": "invalid_date", "Категория": "Еда", "Бонусы (включая кэшбэк)": 50}]
    with pytest.raises(Exception):
        analyze_cashback(data, 2025, 8)


# ----------------------
# Тесты search_transactions
# ----------------------


def test_search_transactions_success():
    data = [
        {"Описание": "Оплата кафе", "Категория": "Еда"},
        {"Описание": "Такси", "Категория": "Транспорт"},
        {"Описание": "Покупка книги", "Категория": "Развлечения"},
    ]
    result_json = search_transactions(data, "кафе")
    result = json.loads(result_json)
    assert len(result) == 1
    assert result[0]["Описание"] == "Оплата кафе"


def test_search_transactions_no_matches():
    data = [{"Описание": "Оплата кафе", "Категория": "Еда"}]
    result_json = search_transactions(data, "магазин")
    result = json.loads(result_json)
    assert result == []


def test_search_transactions_invalid_data():
    data = "not_a_list"
    with pytest.raises(Exception):
        search_transactions(data, "кафе")


# ----------------------
# Тесты search_transactions_p2p
# ----------------------


@patch("src.services.search_transactions")
def test_search_transactions_p2p_success(mock_search):
    # Подменяем два вызова search_transactions
    # Первый вызов (фильтр по категории "Переводы")
    mock_search.side_effect = [
        json.dumps(
            [{"Описание": "Иван П.", "Категория": "Переводы"}, {"Описание": "Мария С.", "Категория": "Переводы"}]
        ),
        json.dumps([{"Описание": "Иван П.", "Категория": "Переводы"}]),
    ]
    data = [{"Описание": "dummy", "Категория": "dummy"}]
    result_json = search_transactions_p2p(data)
    result = json.loads(result_json)
    assert len(result) == 1
    assert result[0]["Описание"] == "Иван П."
    assert mock_search.call_count == 2


@patch("src.services.search_transactions")
def test_search_transactions_p2p_no_matches(mock_search):
    mock_search.side_effect = [json.dumps([]), json.dumps([])]
    data = [{"Описание": "dummy", "Категория": "dummy"}]
    result_json = search_transactions_p2p(data)
    result = json.loads(result_json)
    assert result == []


# ----------------------
# Тесты search_transactions_by_phone
# ----------------------


@patch("src.services.search_transactions")
def test_search_transactions_by_phone_success(mock_search):
    mock_search.return_value = json.dumps([{"Описание": "+7 912 345-67-89", "Категория": "Связь"}])
    data = [{"Описание": "dummy", "Категория": "dummy"}]
    result_json = search_transactions_by_phone(data)
    result = json.loads(result_json)
    assert len(result) == 1
    assert "+7" in result[0]["Описание"]
    mock_search.assert_called_once()


@patch("src.services.search_transactions")
def test_search_transactions_by_phone_no_matches(mock_search):
    mock_search.return_value = json.dumps([])
    data = [{"Описание": "dummy", "Категория": "dummy"}]
    result_json = search_transactions_by_phone(data)
    result = json.loads(result_json)
    assert result == []
