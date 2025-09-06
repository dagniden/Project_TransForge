import os

import pandas as pd

from src.reports import spending_by_category
from src.services import search_transactions, search_transactions_by_phone, search_transactions_p2p
from src.utils import read_excel
from src.views import get_main_page

if __name__ == "__main__":
    # Основные параметры для работы приложения
    current_dir = os.path.dirname(os.path.abspath(__file__))
    excel_dict = read_excel(os.path.join(current_dir, "..", "data", "operations.xlsx"))
    excel_df = pd.DataFrame(excel_dict)
    current_time = "2020-05-20 18:20:00"

    # Получение json для главной страницы
    main_page_json = get_main_page(excel_dict, current_time)
    print(main_page_json)

    # Пример использования сервиса поиска транзакций - по нескольким колонкам с регулярным выражением
    found_transactions = search_transactions(excel_dict, r"\s(через)+\s", ("Описание", "Категория"))

    # Пример использования сервиса поиска транзакций с переводами физ.лицам
    p2p_transactions = search_transactions_p2p(excel_dict)

    # Пример использования сервиса поиска транзакций с переводами по номеру телефона
    mobile_transactions = search_transactions_by_phone(excel_dict)

    # Пример использования отчета по категориям
    report_df = spending_by_category(excel_df, category="Переводы", date="2021-12-19")
