# Project TRANSFORGE

Набор утилит для анализа, поиска и отчётности по данным банковских транзакций.
Проект умеет собирать сводку для «главной» страницы, искать операции по шаблонам, считать статистику по картам и
формировать Excel-отчёты.

# Структура проекта

```
.
├── src
│ ├── __init__.py
│ ├── utils.py          # Чтение Excel, JSON; статистика по картам; топ-операции; фильтр котировок
│ ├── main.py           # Примеры запуска основных сценариев
│ ├── views.py          # Формирование JSON для главной страницы и приветствия
│ ├── reports.py        # Отчёты и декоратор авто-сохранения в Excel
│ ├── external_api.py   # Курсы валют (ЦБ РФ) и котировки акций (Marketstack)
│ └── services.py       # Поиск/фильтры по транзакциям, анализ кэшбэка
├── logs                # Папка для логов (создаётся автоматически)
├── data
│ ├── operations.xlsx   # Входные/выходные данные (operations.xlsx, отчёты *.xlsx)
├── tests
│ ├── __init__.py
│ ├── test_utils.py
│ ├── test_views.py
│ ├── test_reports.py
│ ├── test_external_api.py
│ └── test_services.py
├── user_settings.json  # Пользовательские настройки
├── .venv/
├── .env
├── .env_template
├── .git/
├── .idea/
├── .flake8
├── .gitignore
├── pyproject.toml
├── poetry.lock
└── README.md
```

# Описание данных

| Поле                              | Описание                                                             |
|-----------------------------------|----------------------------------------------------------------------|
| **Дата операции**                 | Дата, когда произошла транзакция                                     |
| **Дата платежа**                  | Дата, когда был произведен платеж                                    |
| **Номер карты**                   | Последние 4 цифры номера карты                                       |
| **Статус**                        | Статус операции (например, `OK`, `FAILED`)                           |
| **Сумма операции**                | Сумма транзакции в оригинальной валюте                               |
| **Валюта операции**               | Валюта, в которой была произведена транзакция                        |
| **Сумма платежа**                 | Сумма транзакции в валюте счета                                      |
| **Валюта платежа**                | Валюта счета                                                         |
| **Кешбэк**                        | Размер полученного кешбэка                                           |
| **Категория**                     | Категория транзакции                                                 |
| **MCC**                           | Код категории транзакции (соответствует международной классификации) |
| **Описание**                      | Описание транзакции                                                  |
| **Бонусы (включая кешбэк)**       | Количество полученных бонусов (включая кешбэк)                       |
| **Округление на «Инвесткопилку»** | Сумма, которая была округлена и переведена на «Инвесткопилку»        |
| **Сумма операции с округлением**  | Сумма транзакции, округленная до ближайшего целого числа             |

## Зависимости

* Python 3.11+
* `pandas`, `python-dateutil`, `requests`, `python-dotenv`, `loguru`
* Для чтения Excel: `openpyxl`


## Установка

```bash
git clone git@github.com:dagniden/project9.git
cd project9
poetry install
```

## Конфигурация

### Переменные окружения

Для получения котировок акций через API Marketstack требуется ключ:

Создайте `.env` в корне проекта (по образцу `.env.example`):

```ini
# Marketstack (https://marketstack.com/)
MARKETSTACK_API_KEY = ВашКлюч
```

> Курсы валют ЦБ РФ берутся с публичного эндпоинта и ключа не требуют.

### Настройки пользователя

`user_settings.json` в корне проекта (используется `views.py → get_main_page`):

```json
{
    "user_stocks": [
        "AAPL",
        "MSFT",
        "GOOGL"
    ],
    "user_currencies": [
        "USD",
        "EUR"
    ]
}
```

## Логирование

Используется `loguru`. Для каждого модуля создаётся собственный лог-файл в `logs/`:

* `external_api.log`, `reports.log`, `services.log`, `utils.log`, `views.log`
* Формат: метка времени, уровень, сообщение.
* Логи пишутся на уровень `DEBUG`.
* Директория `logs/` создаётся автоматически.

## Возможности

### Отчёты

* `reports.save_report(filename: str = "")` — декоратор. Автоматически сохраняет результат функции в `*.xlsx`.
  Если `filename` не указан, создастся имя вида `<func>_YYYY_MM_DD_HHMM_report.xlsx` в `data/`.
* `reports.spending_by_category(transactions: pd.DataFrame, category: str, date: str)`
  Возвращает `DataFrame` операций **за последние 3 месяца** от указанной даты и по указанной категории.
  Дата в формате `YYYY-MM-DD`.

### Интеграции/данные

* `external_api.get_currency_rate(code: str)` — курс валюты ЦБ РФ по коду ISO (например, `USD`).
* `external_api.get_stock_prices(tickers: list[str])` — котировки (EOD) через Marketstack.

### Сервисы

* `services.analyze_cashback(data, year, month)` — суммы кэшбэка по категориям за выбранный месяц (JSON).
* `services.search_transactions(data, pattern, scope=("Описание","Категория"))` — поиск транзакций по регулярному
  выражению.
* `services.search_transactions_p2p(data)` — поиск переводов физлицам.
* `services.search_transactions_by_phone(data)` — поиск операций с телефонными номерами в описании.

### Утилиты

* `utils.read_excel(path)` — чтение Excel в список словарей с заполнением `NaN` (числа → 0, строки → `""`).
* `utils.read_json(path)` — чтение JSON (словарь/список).
* `utils.get_card_statistics(data)` — агрегирование трат (отрицательные суммы) и кэшбэка по последним цифрам карт.
* `utils.filter_top_transactions(data)` — топ-5 операций по абсолютной величине платежа.
* `utils.filter_last_stocks(data, stock_names)` — последние цены акций (первое вхождение по тикеру, валюта USD).

### Представление (view)

* `views.get_main_page(data: list[dict], datetime_str: str)` — формирует итоговый JSON для главного экрана:

    * приветствие по времени,
    * статистика по картам,
    * топ-5 операций,
    * последние котировки акций пользователя,
    * актуальные курсы валют пользователя.
* `views.get_greetings(dt: datetime)` — «Доброе утро/день/вечер/ночи».

## Примеры использования

### Быстрый запуск демонстрации

```bash
# Poetry
poetry run python -m src.main
```

Скрипт:

* считывает `data/operations.xlsx`,
* печатает JSON для главной страницы,
* демонстрирует поиск по регулярным выражениям,
* формирует отчёт за 3 месяца по категории (Excel сохраняется в `data/` благодаря декоратору).

### Фрагменты кода

```python
import os
import pandas as pd
from src.utils import read_excel
from src.views import get_main_page
from src.reports import spending_by_category

# Входные данные
current_dir = os.path.dirname(os.path.abspath(__file__))
records = read_excel(os.path.join(current_dir, "..", "data", "operations.xlsx"))
df = pd.DataFrame(records)

# Главная страница
main_json = get_main_page(records, "2020-05-20 18:20:00")
print(main_json)

# Отчёт за 3 месяца по категории
report_df = spending_by_category(df, category="Переводы", date="2021-12-19")
# Результат автоматически сохранится в data/<имя_функции>_..._report.xlsx
```

Поиск транзакций:

```python
from src.services import search_transactions, search_transactions_p2p, search_transactions_by_phone

# Поиск по нескольким колонкам (Описание, Категория)
found = search_transactions(records, r"\s(через)+\s", ("Описание", "Категория"))

# Переводы физлицам
p2p = search_transactions_p2p(records)

# Операции с упоминанием телефонов
phones = search_transactions_by_phone(records)
```

Получение котировок и курсов:

```python
from src.external_api import get_stock_prices, get_currency_rate

tickers = ["AAPL", "MSFT"]
stocks = get_stock_prices(tickers)

usd = get_currency_rate("USD")
eur = get_currency_rate("EUR")
```

## Основной пользовательский сценарий

1. Загрузить операции из `data/operations.xlsx`.
2. Сформировать сводку для главной страницы (`get_main_page`), используя:

    * настройки из `user_settings.json` (тикеры и коды валют),
    * текущие курсы валют и котировки акций,
    * статистику по картам и топ-операции.
3. При необходимости — запустить отчёт `spending_by_category` для заданной категории и даты:
   результат будет сохранён в Excel автоматически.

## Тестирование

Тестирование есть.

```bash
pytest --cov
```

Для получения отчета о покрытии:

```bash
pytest --cov=src --cov-report=html
# Отчёт будет в htmlcov/index.html
```