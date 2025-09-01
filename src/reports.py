import json
import os
from datetime import datetime
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta
from loguru import logger

from src.services import search_transactions

# Конфигурация логгера
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "reports.log")
logger.add(sink=log_file, level="DEBUG")


def save_report(filename: str = ""):
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal filename
            result = func(*args, **kwargs)
            logger.debug(f"Start saving report with decorator into: {filename}")
            if filename == "":
                name = f"{func.__name__}_{datetime.now().strftime("%Y_%m_%d_%H%M")}_report.xlsx"
                filename = os.path.join(current_dir, "..", "data", name)

            write_report(filename, result)
            return result

        return wrapper

    return my_decorator


@save_report()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает DataFrame транзакций за последние 3 месяца по заданной категории"""
    dt = datetime.strptime(date, "%Y-%m-%d")

    # Преобразуем столбец с датой в datetime
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    # Фильтруем за последние 3 месяца
    three_months_ago = dt - relativedelta(months=3)
    df_filtered = transactions[
        (transactions["Дата операции"] >= three_months_ago) & (transactions["Дата операции"] <= dt)
    ].copy()
    df_filtered["Дата операции"] = df_filtered["Дата операции"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Преобразуем в список словарей и в JSON
    result = df_filtered.to_dict("records")

    # Фильтруем по категории
    data_json = search_transactions(result, search=category, scope=("Категория",))
    data_dict = json.loads(data_json)
    return pd.DataFrame(data_dict)


def write_report(filename: str, df: pd.DataFrame):
    with pd.ExcelWriter(filename) as writer:
        df.to_excel(writer, sheet_name="Sheet1")
