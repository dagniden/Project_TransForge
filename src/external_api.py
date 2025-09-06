import os

import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Конфигурация логгера
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "external_api.log")
logger.add(sink=log_file, level="DEBUG")


def get_currency_rate(currency_code: str):
    """Возвращает текущий курс указанной валюты по коду ISO с сайта ЦБ РФ."""
    url = "https://www.cbr-xml-daily.ru//daily_json.js"

    logger.debug(f"Sending GET request: {url=}")
    response = requests.get(url)

    if response.status_code != 200:
        raise ValueError("Failed to get currency rate")

    data = response.json()
    currency_data = data["Valute"].get(currency_code)

    if not currency_data:
        logger.debug(f"Error getting currency rate: {currency_code}")
        raise ValueError(f"No data for currency {currency_code}")

    result = {
        "currency_code": currency_code,
        "rate": currency_data["Value"],
    }

    logger.debug(f"Getting currency rate: {result=}")
    return result


def get_stock_prices(stock_names: list) -> list:
    api_key = os.getenv("MARKETSTACK_API_KEY")
    """Получает котировки акций (цены закрытия) для списка тикеров через API Marketstack."""
    stock_name_str = ",".join(stock_names)
    url = f"http://api.marketstack.com/v2/eod?access_key={api_key}&symbols={stock_name_str}"

    logger.debug(f"Sending GET request: {url=}")
    response = requests.get(url)

    if response.status_code != 200:
        logger.error(f"Error getting stock prices: {response.status_code} {response.reason}")
        return []

    json_data = response.json().get("data", [])
    logger.debug(f"JSON data len: {url=}")
    return json_data
