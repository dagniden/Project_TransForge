import json
import os
from datetime import datetime

import pandas as pd
from loguru import logger

from src.external_api import get_currency_rate, get_stock_prices
from src.utils import filter_last_stocks, filter_top_transactions, get_card_statistics, read_json

# Конфигурация логгера
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "views.log")
logger.add(sink=log_file, level="DEBUG")


def get_main_page(data: list[dict], datetime_str: str) -> str:
    """Возвращает json для главной страницы"""
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    settings = read_json(os.path.join(current_dir, "..", "user_settings.json"))
    user_stocks = settings["user_stocks"]
    user_currencies = settings["user_currencies"]
    logger.debug(f"Start calculating response for main page with args: {user_stocks=}, {user_currencies=}, {dt=}")

    filtered_data = filter_data_by_month(data, dt)

    greeting_str = get_greetings(dt)
    cards_data = get_card_statistics(filtered_data)
    top_transactions = filter_top_transactions(filtered_data)

    stocks_data = []
    try:
        stocks_data = filter_last_stocks(get_stock_prices(user_stocks), user_stocks)
    except Exception as e:
        logger.error(f"Error getting stocks data: {e}")

    currency_rates = []
    for currency_code in user_currencies:
        try:
            currency_rate = get_currency_rate(currency_code)
            currency_rates.append(currency_rate)
        except Exception as e:
            logger.error(f"Error getting currency rate {currency_code}: {e}")

    result = {
        "greeting": greeting_str,
        "cards": cards_data,
        "top_transaction": top_transactions,
        "stock_prices": stocks_data,
        "currency_rates": currency_rates,
    }

    logger.debug(f"Response for main page calculated: {result=}")
    result_json = json.dumps(result, ensure_ascii=False, indent=4, default=json_serializer)
    return result_json


def filter_data_by_month(data: list[dict], dt: datetime) -> list[dict]:
    """
    Оставляет записи только в диапазоне с начала месяца до указанной даты включительно.
    Предполагается, что в данных есть ключ 'Дата операции' в формате '%d.%m.%Y %H:%M:%S'.
    """
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    start_of_month = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    mask = (df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= dt)

    return df.loc[mask].to_dict("records")


def json_serializer(obj):
    """Конвертер для datetime и pandas.Timestamp в строку"""
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    raise TypeError(f"Type {type(obj)} not serializable")


def get_greetings(dt: datetime) -> str:
    """Возвращает приветствие пользователя"""
    logger.debug(f"Calculating user greeting for hour: {dt.hour}")
    if dt.hour < 12:
        return "Доброе утро"
    elif dt.hour < 18:
        return "Добрый день"
    elif dt.hour < 21:
        return "Добрый вечер"
    else:
        return "Доброй ночи"
