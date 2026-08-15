# SkyPro Модуль Django Магазин. Учебный проект: Bootstrap + http.server

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)


Учебный проект, реализующий простой веб-сервер на встроенном модуле `http.server` с поддержкой статических файлов, обработкой GET/POST-запросов и страницами ошибок.


## 🚀 Возможности программы

Проект представляет собой минималистичный веб-сервер, написанный на чистом Python без использования сторонних фреймворков. Он умеет:

- 📄 Отдавать HTML-страницы
- 🎨 Раздавать статические файлы (CSS, JS, шрифты)
- 📨 Обрабатывать POST-запросы (форма обратной связи)
- 🛡️ Защищать от directory traversal атак
- 🔄 Нормализовать URL-пути
- 🎯 Возвращать страницы 404 и 500

Проект создан в образовательных целях для понимания того, как работают веб-серверы "под капотом".

## 📋 Содержание

- [Технологии](#технологии)
- [Установка](#установка)
- [Конфигурация](#конфигурация)
- [Использование](#использование)
- [Структура таблиц БД](#структура-таблиц-бд)
- [Методы DBManager](#методы-dbmanager)
- [Разработка](#разработка)
- [Тестирование](#тестирование)
- [To do](#to-do)
- [Команда проекта](#команда-проекта)

<div id="технологии"></div>

## Технологии

| Компонент | Технология |
|-----------|------------|
| **HTTP-сервер** | `http.server.BaseHTTPRequestHandler` |
| **Верстка** | Bootstrap 5 |
| **Иконки** | Bootstrap Icons |


<div id="установка"></div>

## Установка

```bash
git clone https://github.com/matt-motik/sp-django.git
cd sp-django
poetry install --with dev,lint
poetry shell
```

<div id="конфигурация"></div>

## ⚙️ Конфигурация


<div id="использование"></div>

## 💻 Использование

### Запуск программы

```bash
poetry run python main.py
```
Открыть в браузере
http://127.0.0.1:8000/
```
HTTP-запрос
    │
    ▼
┌─────────────────────────────────────────┐
│ Handler.do_GET() / do_POST()            │
├─────────────────────────────────────────┤
│ 1. Нормализация пути (posixpath.normpath)│
│ 2. Редирект (если путь изменился)       │
│ 3. Статика (/static/*)                  │
│ 4. Страницы ошибок (/404, /500)         │
│ 5. Основная логика (read_page)          │
└─────────────────────────────────────────┘
```
<div id="разработка"></div>

## Разработка

<!-- СЕКЦИЯ_AUTO_API: СТАРТ -->
<details>
<summary>📚 Документация API (развёрнуть)</summary>

*Этот раздел генерируется автоматически из docstring.*

| Модуль | Функция/Класс | Краткое описание |
|--------|---------------|------------------|
| [**`main.py`**](docs/api/main.md) | | |
| | [🔧 main](docs/api/main.md#main) | Основная функция запуска. |
| [**`path.py`**](docs/api/path.md) | | |
| | [🔧 get_log_path](docs/api/path.md#get_log_path) | Функция для получения пути к папке с логами. |
| | [🔧 get_root_dir](docs/api/path.md#get_root_dir) | Функция для получения пути к корневой папке проекта. |
| | [🔧 get_data_dir](docs/api/path.md#get_data_dir) | Функция для получения пути к папке с данными. |
| [**`server.py`**](docs/api/server.md) | | |
| | [🔧 path_guard](docs/api/server.md#path_guard) | Декоратор для защиты путей к страницам. |
| | [🔧 read_page](docs/api/server.md#read_page) | Читает HTML-файл из директории pages. |
| | [📦 Handler](docs/api/server.md#Handler) | Обработчик HTTP-запросов для простого веб-сервера. |
| | [⚙️ Handler.do_GET](docs/api/server.md#Handler.do_GET) | Обрабатывает входящие GET-запросы. |
| | [⚙️ Handler.do_POST](docs/api/server.md#Handler.do_POST) | Обрабатывает входящие POST-запросы. |
| | [🔧 do_GET](docs/api/server.md#do_GET) | Обрабатывает входящие GET-запросы. |
| | [🔧 do_POST](docs/api/server.md#do_POST) | Обрабатывает входящие POST-запросы. |

> 📘 **Полная документация** с примерами и описанием параметров доступна в папке [`docs/api`](docs/api).
</details>
<!-- СЕКЦИЯ_AUTO_API: КОНЕЦ -->

<div id="тестирование"></div>

## 🧪 Тестирование

> `main.py` не тестируется

<!-- СЕКЦИЯ_AUTO_TEST: СТАРТ -->
<details>
<summary>📊 Результаты тестов и покрытие (развёрнуть)</summary>
### 📊 Результаты тестов SRC

```
📈 Покрытие кода:
src/__init__.py       0      0   100%
src/path.py          10     10     0%   3-22
src/server.py        99     99     0%   2-264
TOTAL               109    109     0%
Coverage HTML written to dir htmlcov/src
/home/matt/.cache/pypoetry/virtualenvs/sp-django-dGoNMyjz-py3.14/lib/python3.14/site-packages/coverage/control.py:963: CoverageWarning: No data was collected. (no-data-collected); see https://coverage.readthedocs.io/en/7.15.4/messages.html#warning-no-data-collected

🎯 Результаты тестов src:
============================= test session starts ==============================
=============================== warnings summary ===============================
================================ tests coverage ================================
-----------------------------------------------
-----------------------------------------------
============================== 1 warning in 0.04s ==============================
```

> 📊 **HTML отчёт покрытия**: [`htmlcov/index.html`](htmlcov/src/index.html)


</details>
<!-- СЕКЦИЯ_AUTO_TEST: КОНЕЦ -->

<div id="to-do"></div>

## To do

- [x] Структура проекта, `pyproject.toml`, `README.md`, `.gitignore`, Poetry, линтеры
- [x] Виртуальное окружение, установка зависимостей через Poetry
- [x] `readme_gen.py` — скрипт генерации README и покрытия тестами
- [x] `lint.ps1` — скрипт линтеров, форматеров, типизаторов и др
- [x] [main.py](main.py) — Точка входа в приложение
- [x] server.py — основной модуль веб-сервера на BaseHTTPRequestHandler
- [x] [path.py](src/path.py) — Модуль реализующий работу с путями
- [x]  Реализована обработка GET-запросов:
- [x] Отдача HTML-страниц из pages/
- [x] Раздача статических файлов из static/
- [x] Нормализация URL-путей через posixpath.normpath
- [x] Защита от directory traversal (..)
- [x] Защита от URL-кодирования (%2E%2E)
- [x] Редирект (301) при изменении пути
- [x] Страницы ошибок 404 и 500
- [x] Реализована обработка POST-запросов:
- [x] Чтение тела запроса
- [x] Парсинг данных формы (application/x-www-form-urlencoded)
- [x] Вывод данных в консоль для отладки
- [x] Возврат страницы contacts.html после отправки
- [x] Сверстаны 4 страницы по прототипам:
- [x] index.html — Главная
- [x] category.html — Категории
- [x] catalog.html — Каталог/Заказы
- [x] contacts.html — Контакты (с формой обратной связи)
- [x] Страницы ошибок:
- [x] 404.html
- [x] 500.html
- [x] Подключен Bootstrap 5 (локально через /static/)
- [x] Подключены Bootstrap Icons
- [x] Создан navigation.js — скрипт подсветки активного пункта меню
- [x] Декоратор path_guard для защиты путей к страницам
- [x] Защита от directory traversal (..)
- [x] Защита от URL-кодирования (unquote)
- [x] Нормализация пути через posixpath.normpath
- [x] Проверка, что файл статики находится внутри STATIC_DIR
- [x] Проверить линтеры (`flake8`, `mypy`, `pydocstyle`, `black`, `isort`)
- [x] Финальная вычитка документации и обновление README
- [x] Обновить документацию

## Команда проекта

- Matvey Bakirov — [mabakirov@gmail.com](mailto:mabakirov@gmail.com) — Back-End Engineer
