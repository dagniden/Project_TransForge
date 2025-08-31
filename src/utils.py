import json
import os

import pandas as pd
import requests
from loguru import logger

# Конфигурация логгера
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "utils.log")
logger.add(sink=log_file, level="DEBUG")


def read_excel(filename: str) -> list[dict]:
    """Функция возвращает DataFrame с содержимым эксель файла"""
    data = pd.read_excel(filename)
    return data.to_dict("records")


def read_json(filename: str) -> dict | list[dict]:
    """Функция возвращает словарь с конфигурацией приложения"""
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_stock_prices(stock_names: list) -> list:
    stock_name_str = ",".join(stock_names)
    api_key = "869901c4c2db759fdfe5c7f7fc0b4a9f"
    url = f"http://api.marketstack.com/v2/eod?access_key={api_key}&symbols={stock_name_str}"
    logger.debug(f"Sending GET request: {url=}")

    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"Error getting stock prices: {response.status_code} {response.reason}")
        return []

    json_data = response.json().get("data", [])
    logger.debug(f"JSON data len: {url=}")
    return json_data


def filter_last_stocks(data: list[dict], stock_names: list) -> list:
    """Функция возвращает список последних цен акций"""
    logger.debug(f"Start filtering last stocks: input data len={len(data)}, {stock_names=}")
    result = []
    found_stocks = []
    for item in data:
        if item["symbol"] in stock_names and item["symbol"] not in found_stocks and item["price_currency"] == "USD":
            result.append({"stock": item["symbol"], "price": item["high"]})
            found_stocks.append(item["symbol"])
    logger.debug(f"End filtering last stocks: output data len={len(found_stocks)}")
    return result
