import json
import os
import re

import pandas as pd
from loguru import logger

# Конфигурация логгера
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "services.log")
logger.add(sink=log_file, level="DEBUG")


def analyze_cashback(data: list[dict], year: int, month: int) -> str:
    """Функция возвращает JSON с суммами по категориям кэшбэка в указанном месяце года"""
    logger.debug(f"start analyzing cashback data for {year}/{month}. Input data len: {len(data)}")
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    df_filtered = df[(df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)]

    result = df_filtered.groupby("Категория")["Бонусы (включая кэшбэк)"].sum().sort_values(ascending=False).to_dict()
    logger.debug(f"Analyzed cashback len: {len(result)}")
    result_json = json.dumps(result, indent=4, ensure_ascii=False)
    return result_json


def search_transactions(data: list[dict], search: str, scope: tuple = ("Описание", "Категория")) -> str:
    """Функция возвращает JSON со всеми транзакциями, найденными по паттерну в полях описание или категория"""
    logger.debug(f"Start searching transactions for with pattern: '{search}'. Input data len: {len(data)}")
    pattern = re.compile(search)
    result = []

    for transaction in data:
        for transaction_key in transaction.keys():
            if transaction_key in scope:
                value = transaction[transaction_key]

                if isinstance(value, (int, bool, float)):
                    value = str(value)

                if isinstance(value, str) and pattern.search(value):
                    result.append(transaction)
                    break
    logger.debug(f"Search result len: {len(result)}")
    return json.dumps(result, ensure_ascii=False, indent=4)


def search_transactions_p2p(data: list[dict]) -> str:
    """Функция возвращает JSON со всеми транзакциями, которые относятся к переводам физ.лицам"""
    return search_transactions(data, r"[А-Я]{1}[а-я]+\s[А-Я]{1}\.", scope=("Описание",))


def search_transactions_by_phone(data: list[dict]) -> str:
    """Функция возвращает JSON со всеми транзакциями, содержащими в описании мобильные номера"""
    return search_transactions(data, r"\+7\s\d{3}\s\d{2,3}-\d{2}-\d{2}", scope=("Описание",))
