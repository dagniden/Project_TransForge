import json
import os

import pandas as pd

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


def get_card_statistics(data: list[dict]) -> list:
    """Вычисляет статистику трат и кэшбэка по картам из списка транзакций."""
    logger.debug(f"Start calculating statistics for operation's amount: {len(data)}")
    df = pd.DataFrame(data)
    df_filtered = df[df["Сумма платежа"] < 0]

    df_grouped = (
        df_filtered
        .groupby("Номер карты")
        .agg({
            "Сумма операции": "sum",
            "Кэшбэк": "sum"
        })
        .reset_index()
        .to_dict("records")
    )

    result = []
    for item in df_grouped:
        result.append({"last_digits": item["Номер карты"].replace("*", ""),
                       "total_spent": abs(item["Сумма операции"]),
                       "cashback": item["Кэшбэк"]})

    logger.debug(f"Card statistics result len: {len(result)}\n"
                 f"Result: {result}")
    return result


def filter_top_transactions(data: list[dict]) -> list:
    logger.debug(f"Start filtering top transactions for operation's amount: {len(data)}")
    sorted_data = sorted(data, key=lambda x: abs(x.get("Сумма платежа")), reverse=True)
    top_transactions = sorted_data[:5]
    result = []
    for item in top_transactions:
        result.append({"date": item.get("Дата операции", ""),
                       "amount": item.get("Сумма платежа", ""),
                       "category": item.get("Категория", ""),
                       "description": item.get("Описание", "")

        })
    logger.debug(f"Top transactions result len: {len(result)}\n")
    return result


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


if __name__ == "__main__":
    excel_dict = read_excel("operations_test.xlsx")
    get_card_statistics(excel_dict)
