import json

from datetime import datetime
from src.utils import read_excel

def analyze_cashback(data: list[dict], year: str, month: str) -> dict:
    pass


if __name__ == '__main__':
    data = read_excel("operations_test.xlsx")
    expected = {
        "Категория 1": 1000,
        "Категория 2": 2000,
        "Категория 3": 500
    }

    for item in data[:5]:
        print(item)
    # res = analyze_cashback()
