# SkyPro Модуль ООП Трекер Самолётов

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791.svg)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/Tests-pytest-green.svg)](https://pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)]()

Курсовой проект для получения данных о самолётах, находящихся в воздухе, через открытые API [OpenSky Network](https://opensky-network.org/) и [Nominatim](https://nominatim.openstreetmap.org/), с сохранением в PostgreSQL.

## 🚀 Возможности программы

- Получение bounding box страны через **Nominatim API**
- Получение списка самолётов в воздушном пространстве через **OpenSky Network API**
- Сохранение данных в JSON-файл с возможностью добавления, обновления и удаления записей
- Сохранение данных в **PostgreSQL** с поддержкой upsert (обновление существующих записей)
- Фильтрация самолётов по: стране регистрации, позывному, диапазону высот, диапазону скоростей, нахождению на земле / в воздухе, географическим координатам (bounding box)
- Аналитические запросы: средняя скорость, самые быстрые самолёты
- Сортировка по высоте (и скорости при равной высоте), вывод топ-N
- Работа в офлайн-режиме (использование кэшированных данных при недоступности API)

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
| Язык | [Python 3.12+](https://www.python.org/) |
| База данных | [PostgreSQL 14+](https://www.postgresql.org/) |
| Драйвер БД | [psycopg2](https://www.psycopg.org/) |
| HTTP-клиент | [requests](https://requests.readthedocs.io/) |
| Тестирование | [pytest](https://docs.pytest.org/), [pytest-cov](https://pytest-cov.readthedocs.io/) |
| Управление зависимостями | [Poetry](https://python-poetry.org/) |
| Линтеры | [flake8](https://flake8.pycqa.org/), [mypy](https://mypy.readthedocs.io/), [black](https://black.readthedocs.io/), [isort](https://pycqa.github.io/isort/) |
| Внешние API | [OpenSky Network](https://opensky-network.org/), [Nominatim](https://nominatim.org/) (OpenStreetMap) |

<div id="установка"></div>

## Установка

```bash
git clone https://github.com/matt-motik/spcw-aircraft-api.git
cd spcw-aircraft-api
poetry install --with dev,lint
poetry shell
```

<div id="конфигурация"></div>

## ⚙️ Конфигурация

Создайте файл `database.ini` в корне проекта:

```ini
[postgresql]
host=localhost
database=sky_db
user=sky_user
password=your_password
port=5432
```

Для первоначальной инициализации (создание БД и пользователя) создайте `admin.ini`:

```ini
[postgresql]
host=localhost
database=postgres
user=postgres
password=admin_password
port=5432
```

> ⚠️ **Важно:** Не коммитьте файлы с паролями! Добавьте `*.ini` в `.gitignore`.

<div id="использование"></div>

## 💻 Использование

### Запуск программы

```bash
poetry run python main.py
```

1. Выберите хранилище: PostgreSQL или JSON-файл
2. Дождитесь загрузки данных по 10+ странам
3. Введите название страны для поиска самолётов
4. Применяйте фильтры (высота, скорость, координаты, статус)
5. Получите топ-N самолётов, отсортированных по высоте

### Пример программного использования

```python
from src.db_manager import DBManager
from src.aeroplanes_api import AeroplanesAPI
from src.aeroplane import Aeroplane

db = DBManager()
db.initialize()
api = AeroplanesAPI()

bbox = api.get_country_bbox("Germany")
country_id = db.add_country("Germany", bbox)

raw_planes = api.get_aeroplanes("Germany")
planes = Aeroplane.cast_to_object_list(raw_planes, country_id=country_id)
db.add_multiple_aeroplanes(planes)

print(db.get_countries_and_aeroplanes_count())
print(f"Средняя скорость: {db.get_avg_speed():.1f} м/с")
fast_planes = db.get_aeroplanes_with_higher_speed(limit=5)
aca_planes = db.get_aeroplanes_with_keyword("ACA")

db.close()
```

<div id="структура-таблиц-бд"></div>

## 🗄️ Структура таблиц БД

### `countries`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `SERIAL PRIMARY KEY` | Уникальный идентификатор |
| `name` | `VARCHAR(100) UNIQUE NOT NULL` | Название страны |
| `lat_min` | `FLOAT` | Минимальная широта (юг) |
| `lat_max` | `FLOAT` | Максимальная широта (север) |
| `lon_min` | `FLOAT` | Минимальная долгота (запад) |
| `lon_max` | `FLOAT` | Максимальная долгота (восток) |

### `aeroplanes`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `SERIAL PRIMARY KEY` | Уникальный идентификатор |
| `icao24` | `VARCHAR(6) UNIQUE NOT NULL` | Идентификатор транспондера (hex) |
| `callsign` | `VARCHAR(8)` | Позывной рейса |
| `origin_country` | `VARCHAR(100)` | Страна регистрации |
| `longitude` | `FLOAT` | Долгота |
| `latitude` | `FLOAT` | Широта |
| `altitude` | `FLOAT` | Барометрическая высота, м |
| `velocity` | `FLOAT` | Скорость относительно земли, м/с |
| `on_ground` | `BOOLEAN` | Флаг нахождения на земле |
| `country_id` | `INTEGER REFERENCES countries(id)` | Страна над которой летит |

<div id="методы-dbmanager"></div>

## 🔧 Методы DBManager

| Метод | Описание |
|-------|----------|
| `get_countries_and_aeroplanes_count()` | Список стран + количество самолётов в их воздушном пространстве (JOIN) |
| `get_all_aeroplanes()` | Все воздушные суда |
| `get_avg_speed()` | Средняя скорость по всем самолётам |
| `get_aeroplanes_with_higher_speed(limit=5)` | Топ-N самолётов со скоростью выше средней |
| `get_aeroplanes_with_keyword(keyword)` | Поиск по подстроке в позывном (`ILIKE`) |
| `add_aeroplane(aeroplane)` | Добавление / обновление одного самолёта (upsert) |
| `add_multiple_aeroplanes(aeroplanes)` | Пакетное добавление (1 commit) |
| `get_aeroplanes(**filters)` | Фильтрация по 11 параметрам |
| `insert_country(...)` / `add_country(...)` | Добавление страны |
| `delete_aeroplane(aeroplane)` | Удаление по `icao24` |
| `close()` | Закрытие соединения |

<div id="разработка"></div>

## Разработка

<!-- СЕКЦИЯ_AUTO_API: СТАРТ -->
<details>
<summary>📚 Документация API (развёрнуть)</summary>

*Этот раздел генерируется автоматически из docstring.*

| Модуль | Функция/Класс | Краткое описание |
|--------|---------------|------------------|
| [**`aeroplane.py`**](docs/api/aeroplane.md) | | |
| | [📦 Aeroplane](docs/api/aeroplane.md#Aeroplane) | Класс, представляющий данные о самолёте. |
| | [⚙️ Aeroplane.icao24](docs/api/aeroplane.md#Aeroplane.icao24) | Геттер. Уникальный идентификатор борта (транспондера). |
| | [⚙️ Aeroplane.icao24](docs/api/aeroplane.md#Aeroplane.icao24) | Сеттер. Уникальный идентификатор борта (транспондера). |
| | [⚙️ Aeroplane.callsign](docs/api/aeroplane.md#Aeroplane.callsign) | Позывной рейса. |
| | [⚙️ Aeroplane.callsign](docs/api/aeroplane.md#Aeroplane.callsign) | Сеттер. Позывной рейса. |
| | [⚙️ Aeroplane.origin_country](docs/api/aeroplane.md#Aeroplane.origin_country) | Страна регистрации. |
| | [⚙️ Aeroplane.origin_country](docs/api/aeroplane.md#Aeroplane.origin_country) | Сеттер. Страна регистрации. |
| | [⚙️ Aeroplane.longitude](docs/api/aeroplane.md#Aeroplane.longitude) | Долгота (°). |
| | [⚙️ Aeroplane.longitude](docs/api/aeroplane.md#Aeroplane.longitude) | Сеттер. Долгота (°). |
| | [⚙️ Aeroplane.latitude](docs/api/aeroplane.md#Aeroplane.latitude) | Широта (°). |
| | [⚙️ Aeroplane.latitude](docs/api/aeroplane.md#Aeroplane.latitude) | Сеттер. Широта (°). |
| | [⚙️ Aeroplane.altitude](docs/api/aeroplane.md#Aeroplane.altitude) | Барометрическая высота, м. |
| | [⚙️ Aeroplane.altitude](docs/api/aeroplane.md#Aeroplane.altitude) | Сеттер. Барометрическая высота, м. |
| | [⚙️ Aeroplane.velocity](docs/api/aeroplane.md#Aeroplane.velocity) | Скорость относительно земли, м/с. |
| | [⚙️ Aeroplane.velocity](docs/api/aeroplane.md#Aeroplane.velocity) | Сеттер. Скорость относительно земли, м/с. |
| | [⚙️ Aeroplane.on_ground](docs/api/aeroplane.md#Aeroplane.on_ground) | Флаг нахождения на земле. |
| | [⚙️ Aeroplane.on_ground](docs/api/aeroplane.md#Aeroplane.on_ground) | Сеттер. Флаг нахождения на земле. |
| | [⚙️ Aeroplane.country_id](docs/api/aeroplane.md#Aeroplane.country_id) | Страна над которой летит. |
| | [⚙️ Aeroplane.country_id](docs/api/aeroplane.md#Aeroplane.country_id) | Сеттер. Страна над которой летит. |
| | [⚙️ Aeroplane.cast_to_object_list](docs/api/aeroplane.md#Aeroplane.cast_to_object_list) | Преобразует сырой список состояний от OpenSky API в список объектов Aeroplane. |
| | [⚙️ Aeroplane.to_dict](docs/api/aeroplane.md#Aeroplane.to_dict) | Сериализация в словарь. |
| | [⚙️ Aeroplane.from_dict](docs/api/aeroplane.md#Aeroplane.from_dict) | Десериализация из словаря. |
| | [🔧 icao24](docs/api/aeroplane.md#icao24) | Геттер. Уникальный идентификатор борта (транспондера). |
| | [🔧 icao24](docs/api/aeroplane.md#icao24) | Сеттер. Уникальный идентификатор борта (транспондера). |
| | [🔧 callsign](docs/api/aeroplane.md#callsign) | Позывной рейса. |
| | [🔧 callsign](docs/api/aeroplane.md#callsign) | Сеттер. Позывной рейса. |
| | [🔧 origin_country](docs/api/aeroplane.md#origin_country) | Страна регистрации. |
| | [🔧 origin_country](docs/api/aeroplane.md#origin_country) | Сеттер. Страна регистрации. |
| | [🔧 longitude](docs/api/aeroplane.md#longitude) | Долгота (°). |
| | [🔧 longitude](docs/api/aeroplane.md#longitude) | Сеттер. Долгота (°). |
| | [🔧 latitude](docs/api/aeroplane.md#latitude) | Широта (°). |
| | [🔧 latitude](docs/api/aeroplane.md#latitude) | Сеттер. Широта (°). |
| | [🔧 altitude](docs/api/aeroplane.md#altitude) | Барометрическая высота, м. |
| | [🔧 altitude](docs/api/aeroplane.md#altitude) | Сеттер. Барометрическая высота, м. |
| | [🔧 velocity](docs/api/aeroplane.md#velocity) | Скорость относительно земли, м/с. |
| | [🔧 velocity](docs/api/aeroplane.md#velocity) | Сеттер. Скорость относительно земли, м/с. |
| | [🔧 on_ground](docs/api/aeroplane.md#on_ground) | Флаг нахождения на земле. |
| | [🔧 on_ground](docs/api/aeroplane.md#on_ground) | Сеттер. Флаг нахождения на земле. |
| | [🔧 country_id](docs/api/aeroplane.md#country_id) | Страна над которой летит. |
| | [🔧 country_id](docs/api/aeroplane.md#country_id) | Сеттер. Страна над которой летит. |
| | [🔧 cast_to_object_list](docs/api/aeroplane.md#cast_to_object_list) | Преобразует сырой список состояний от OpenSky API в список объектов Aeroplane. |
| | [🔧 to_dict](docs/api/aeroplane.md#to_dict) | Сериализация в словарь. |
| | [🔧 from_dict](docs/api/aeroplane.md#from_dict) | Десериализация из словаря. |
| [**`aeroplanes_api.py`**](docs/api/aeroplanes_api.md) | | |
| | [📦 AeroplanesAPI](docs/api/aeroplanes_api.md#AeroplanesAPI) | Класс для работы с API nominatim.openstreetmap.org и opensky-network.org. |
| | [⚙️ AeroplanesAPI.get_country_bbox](docs/api/aeroplanes_api.md#AeroplanesAPI.get_country_bbox) | Получает bounding box страны через Nominatim API. |
| | [⚙️ AeroplanesAPI.get_aeroplanes](docs/api/aeroplanes_api.md#AeroplanesAPI.get_aeroplanes) | Получает список самолётов в воздушном пространстве указанной страны. |
| | [🔧 get_country_bbox](docs/api/aeroplanes_api.md#get_country_bbox) | Получает bounding box страны через Nominatim API. |
| | [🔧 get_aeroplanes](docs/api/aeroplanes_api.md#get_aeroplanes) | Получает список самолётов в воздушном пространстве указанной страны. |
| [**`base_api.py`**](docs/api/base_api.md) | | |
| | [📦 BaseAPI](docs/api/base_api.md#BaseAPI) | Абстрактный класс для работы с внешними API. |
| | [⚙️ BaseAPI.get_country_bbox](docs/api/base_api.md#BaseAPI.get_country_bbox) | Метод получения bounding box страны. |
| | [⚙️ BaseAPI.get_aeroplanes](docs/api/base_api.md#BaseAPI.get_aeroplanes) | Метод получения списка самолётов. |
| | [🔧 get_country_bbox](docs/api/base_api.md#get_country_bbox) | Метод получения bounding box страны. |
| | [🔧 get_aeroplanes](docs/api/base_api.md#get_aeroplanes) | Метод получения списка самолётов. |
| [**`base_storage.py`**](docs/api/base_storage.md) | | |
| | [📦 BaseStorage](docs/api/base_storage.md#BaseStorage) | Абстрактный базовый класс для хранилища данных о самолётах. |
| | [⚙️ BaseStorage.add_aeroplane](docs/api/base_storage.md#BaseStorage.add_aeroplane) | Добавляет запись о самолёте в хранилище. |
| | [⚙️ BaseStorage.add_multiple_aeroplanes](docs/api/base_storage.md#BaseStorage.add_multiple_aeroplanes) | Пакетное добавление/обновление списка самолётов с однократным сохранением. |
| | [⚙️ BaseStorage.get_aeroplanes](docs/api/base_storage.md#BaseStorage.get_aeroplanes) | Возвращает список самолётов, удовлетворяющих заданным фильтрам. |
| | [⚙️ BaseStorage.delete_aeroplane](docs/api/base_storage.md#BaseStorage.delete_aeroplane) | Удаляет запись о самолёте из хранилища. |
| | [⚙️ BaseStorage.add_country](docs/api/base_storage.md#BaseStorage.add_country) | Добавляет страну в хранилище. |
| | [⚙️ BaseStorage.get_country](docs/api/base_storage.md#BaseStorage.get_country) | Получает данные о стране из хранилища. |
| | [⚙️ BaseStorage.initialize](docs/api/base_storage.md#BaseStorage.initialize) | Подготовка хранилища (создание таблиц, файлов и т.д.). |
| | [⚙️ BaseStorage.close](docs/api/base_storage.md#BaseStorage.close) | Закрывает хранилище если поддерживает. |
| | [⚙️ BaseStorage.get_aeroplanes_with_keyword](docs/api/base_storage.md#BaseStorage.get_aeroplanes_with_keyword) | Получает самолёты, в позывном которых содержится keyword. |
| | [🔧 add_aeroplane](docs/api/base_storage.md#add_aeroplane) | Добавляет запись о самолёте в хранилище. |
| | [🔧 add_multiple_aeroplanes](docs/api/base_storage.md#add_multiple_aeroplanes) | Пакетное добавление/обновление списка самолётов с однократным сохранением. |
| | [🔧 get_aeroplanes](docs/api/base_storage.md#get_aeroplanes) | Возвращает список самолётов, удовлетворяющих заданным фильтрам. |
| | [🔧 delete_aeroplane](docs/api/base_storage.md#delete_aeroplane) | Удаляет запись о самолёте из хранилища. |
| | [🔧 add_country](docs/api/base_storage.md#add_country) | Добавляет страну в хранилище. |
| | [🔧 get_country](docs/api/base_storage.md#get_country) | Получает данные о стране из хранилища. |
| | [🔧 initialize](docs/api/base_storage.md#initialize) | Подготовка хранилища (создание таблиц, файлов и т.д.). |
| | [🔧 close](docs/api/base_storage.md#close) | Закрывает хранилище если поддерживает. |
| | [🔧 get_aeroplanes_with_keyword](docs/api/base_storage.md#get_aeroplanes_with_keyword) | Получает самолёты, в позывном которых содержится keyword. |
| [**`config_reader.py`**](docs/api/config_reader.md) | | |
| | [📦 ConfigError](docs/api/config_reader.md#ConfigError) | Исключение при ошибках чтения конфигурации. |
| | [🔧 get_db_config](docs/api/config_reader.md#get_db_config) | Читает параметры подключения к БД из INI-файла. |
| [**`db_initializer.py`**](docs/api/db_initializer.md) | | |
| | [🔧 initialize_database](docs/api/db_initializer.md#initialize_database) | Создаёт БД и пользователя для приложения. |
| [**`db_manager.py`**](docs/api/db_manager.md) | | |
| | [📦 DBManager](docs/api/db_manager.md#DBManager) | Класс для работы с данными в PostgreSQL. |
| | [⚙️ DBManager.connection](docs/api/db_manager.md#DBManager.connection) | Ленивое создание соединения. |
| | [⚙️ DBManager.initialize](docs/api/db_manager.md#DBManager.initialize) | Подготовка хранилища — создание таблиц. |
| | [⚙️ DBManager.create_tables](docs/api/db_manager.md#DBManager.create_tables) | Создаёт таблицы countries и aeroplanes. |
| | [⚙️ DBManager.insert_country](docs/api/db_manager.md#DBManager.insert_country) | Добавляет страну в таблицу. |
| | [⚙️ DBManager.add_country](docs/api/db_manager.md#DBManager.add_country) | Добавляет страну в хранилище. |
| | [⚙️ DBManager.insert_aeroplane](docs/api/db_manager.md#DBManager.insert_aeroplane) | Добавляет самолёт в таблицу. |
| | [⚙️ DBManager.add_aeroplane](docs/api/db_manager.md#DBManager.add_aeroplane) | Добавляет один самолёт в БД. |
| | [⚙️ DBManager.add_multiple_aeroplanes](docs/api/db_manager.md#DBManager.add_multiple_aeroplanes) | Пакетное добавление/обновление списка самолётов с однократным сохранением. |
| | [⚙️ DBManager.delete_aeroplane](docs/api/db_manager.md#DBManager.delete_aeroplane) | Удаляет самолёт из БД по icao24. |
| | [⚙️ DBManager.get_aeroplanes](docs/api/db_manager.md#DBManager.get_aeroplanes) | Возвращает список самолётов, удовлетворяющих заданным фильтрам. |
| | [⚙️ DBManager.get_countries_and_aeroplanes_count](docs/api/db_manager.md#DBManager.get_countries_and_aeroplanes_count) | Получает список всех стран и количество самолётов в их воздушных пространствах. |
| | [⚙️ DBManager.get_all_aeroplanes](docs/api/db_manager.md#DBManager.get_all_aeroplanes) | Получает список всех воздушных судов. |
| | [⚙️ DBManager.get_avg_speed](docs/api/db_manager.md#DBManager.get_avg_speed) | Получает среднюю скорость по самолётам. |
| | [⚙️ DBManager.get_aeroplanes_with_higher_speed](docs/api/db_manager.md#DBManager.get_aeroplanes_with_higher_speed) | Получает топ-N самолётов со скоростью выше средней. |
| | [⚙️ DBManager.get_aeroplanes_with_keyword](docs/api/db_manager.md#DBManager.get_aeroplanes_with_keyword) | Получает самолёты, в позывном которых содержится keyword. |
| | [⚙️ DBManager.close](docs/api/db_manager.md#DBManager.close) | Закрывает соединение с БД. |
| | [⚙️ DBManager.get_country](docs/api/db_manager.md#DBManager.get_country) | Получает данные о стране из хранилища. |
| | [🔧 connection](docs/api/db_manager.md#connection) | Ленивое создание соединения. |
| | [🔧 initialize](docs/api/db_manager.md#initialize) | Подготовка хранилища — создание таблиц. |
| | [🔧 create_tables](docs/api/db_manager.md#create_tables) | Создаёт таблицы countries и aeroplanes. |
| | [🔧 insert_country](docs/api/db_manager.md#insert_country) | Добавляет страну в таблицу. |
| | [🔧 add_country](docs/api/db_manager.md#add_country) | Добавляет страну в хранилище. |
| | [🔧 insert_aeroplane](docs/api/db_manager.md#insert_aeroplane) | Добавляет самолёт в таблицу. |
| | [🔧 add_aeroplane](docs/api/db_manager.md#add_aeroplane) | Добавляет один самолёт в БД. |
| | [🔧 add_multiple_aeroplanes](docs/api/db_manager.md#add_multiple_aeroplanes) | Пакетное добавление/обновление списка самолётов с однократным сохранением. |
| | [🔧 delete_aeroplane](docs/api/db_manager.md#delete_aeroplane) | Удаляет самолёт из БД по icao24. |
| | [🔧 get_aeroplanes](docs/api/db_manager.md#get_aeroplanes) | Возвращает список самолётов, удовлетворяющих заданным фильтрам. |
| | [🔧 get_countries_and_aeroplanes_count](docs/api/db_manager.md#get_countries_and_aeroplanes_count) | Получает список всех стран и количество самолётов в их воздушных пространствах. |
| | [🔧 get_all_aeroplanes](docs/api/db_manager.md#get_all_aeroplanes) | Получает список всех воздушных судов. |
| | [🔧 get_avg_speed](docs/api/db_manager.md#get_avg_speed) | Получает среднюю скорость по самолётам. |
| | [🔧 get_aeroplanes_with_higher_speed](docs/api/db_manager.md#get_aeroplanes_with_higher_speed) | Получает топ-N самолётов со скоростью выше средней. |
| | [🔧 get_aeroplanes_with_keyword](docs/api/db_manager.md#get_aeroplanes_with_keyword) | Получает самолёты, в позывном которых содержится keyword. |
| | [🔧 close](docs/api/db_manager.md#close) | Закрывает соединение с БД. |
| | [🔧 get_country](docs/api/db_manager.md#get_country) | Получает данные о стране из хранилища. |
| [**`json_storage.py`**](docs/api/json_storage.md) | | |
| | [📦 JsonStorage](docs/api/json_storage.md#JsonStorage) | Класс для хранилища данных о самолётах. |
| | [⚙️ JsonStorage.initialize](docs/api/json_storage.md#JsonStorage.initialize) | JSON-файл создаётся при первом сохранении. |
| | [⚙️ JsonStorage.add_aeroplane](docs/api/json_storage.md#JsonStorage.add_aeroplane) | Добавляет запись о самолёте в хранилище. |
| | [⚙️ JsonStorage.add_multiple_aeroplanes](docs/api/json_storage.md#JsonStorage.add_multiple_aeroplanes) | Пакетное добавление/обновление списка самолётов с однократным сохранением. |
| | [⚙️ JsonStorage.get_aeroplanes](docs/api/json_storage.md#JsonStorage.get_aeroplanes) | Возвращает список самолётов, удовлетворяющих заданным фильтрам. |
| | [⚙️ JsonStorage.delete_aeroplane](docs/api/json_storage.md#JsonStorage.delete_aeroplane) | Удаляет запись о самолёте из хранилища. |
| | [⚙️ JsonStorage.add_country](docs/api/json_storage.md#JsonStorage.add_country) | Добавляет страну в хранилище. |
| | [⚙️ JsonStorage.get_country](docs/api/json_storage.md#JsonStorage.get_country) | Получает данные о стране из хранилища. |
| | [⚙️ JsonStorage.close](docs/api/json_storage.md#JsonStorage.close) | Закрывает хранилище. Для JSON — ничего не делает. |
| | [⚙️ JsonStorage.get_aeroplanes_with_keyword](docs/api/json_storage.md#JsonStorage.get_aeroplanes_with_keyword) | Получает самолёты, в позывном которых содержится keyword. |
| | [🔧 initialize](docs/api/json_storage.md#initialize) | JSON-файл создаётся при первом сохранении. |
| | [🔧 add_aeroplane](docs/api/json_storage.md#add_aeroplane) | Добавляет запись о самолёте в хранилище. |
| | [🔧 add_multiple_aeroplanes](docs/api/json_storage.md#add_multiple_aeroplanes) | Пакетное добавление/обновление списка самолётов с однократным сохранением. |
| | [🔧 get_aeroplanes](docs/api/json_storage.md#get_aeroplanes) | Возвращает список самолётов, удовлетворяющих заданным фильтрам. |
| | [🔧 delete_aeroplane](docs/api/json_storage.md#delete_aeroplane) | Удаляет запись о самолёте из хранилища. |
| | [🔧 add_country](docs/api/json_storage.md#add_country) | Добавляет страну в хранилище. |
| | [🔧 get_country](docs/api/json_storage.md#get_country) | Получает данные о стране из хранилища. |
| | [🔧 close](docs/api/json_storage.md#close) | Закрывает хранилище. Для JSON — ничего не делает. |
| | [🔧 get_aeroplanes_with_keyword](docs/api/json_storage.md#get_aeroplanes_with_keyword) | Получает самолёты, в позывном которых содержится keyword. |
| [**`logger_creator.py`**](docs/api/logger_creator.md) | | |
| | [🔧 create_logger](docs/api/logger_creator.md#create_logger) | Функция для создания логгера. |
| [**`main.py`**](docs/api/main.md) | | |
| | [🔧 input_float](docs/api/main.md#input_float) | Запрашивает у пользователя ввод дробного числа через консоль. |
| | [🔧 input_int](docs/api/main.md#input_int) | Запрашивает у пользователя ввод целого числа через консоль. |
| | [🔧 input_bool](docs/api/main.md#input_bool) | Запрашивает у пользователя подтверждение действия через консоль. |
| | [🔧 sort_aeroplanes](docs/api/main.md#sort_aeroplanes) | Сортирует самолёты по убыванию высоты (и скорости при равной высоте). |
| | [🔧 get_top_aeroplanes](docs/api/main.md#get_top_aeroplanes) | Получает первые top_n самолёта. |
| | [🔧 print_aeroplanes](docs/api/main.md#print_aeroplanes) | Печатает список самолётов. |
| | [🔧 load_initial_countries](docs/api/main.md#load_initial_countries) | Загружает начальные данные по 4+ странам. |
| | [🔧 user_interaction](docs/api/main.md#user_interaction) | Функция для взаимодействия с пользователем. |
| | [🔧 show_statistics](docs/api/main.md#show_statistics) | Показывает статистику по самолетам. |
| | [🔧 choose_storage](docs/api/main.md#choose_storage) | Выбор хранилища пользователем. |
| | [🔧 main](docs/api/main.md#main) | Основная функция запуска. |
| [**`path.py`**](docs/api/path.md) | | |
| | [🔧 get_log_path](docs/api/path.md#get_log_path) | Функция для получения пути к папке с логами. |
| | [🔧 get_root_dir](docs/api/path.md#get_root_dir) | Функция для получения пути к корневой папке проекта. |
| | [🔧 get_data_dir](docs/api/path.md#get_data_dir) | Функция для получения пути к папке с данными. |

> 📘 **Полная документация** с примерами и описанием параметров доступна в папке [`docs/api`](docs/api).
</details>
<!-- СЕКЦИЯ_AUTO_API: КОНЕЦ -->

## 🌐 Внешние API Endpoints

| API | URL | Назначение |
|-----|-----|------------|
| Nominatim | `https://nominatim.openstreetmap.org/search` | Bounding box страны |
| OpenSky | `https://opensky-network.org/api/states/all` | Состояния самолётов |

<div id="тестирование"></div>

## 🧪 Тестирование

> `main.py` не тестируется

<!-- СЕКЦИЯ_AUTO_TEST: СТАРТ -->
<details>
<summary>📊 Результаты тестов и покрытие (развёрнуть)</summary>
### 📊 Результаты тестов SRC

```
📈 Покрытие кода:
tests/test_aeroplane.py .............................                    [ 27%]
tests/test_aeroplanes_api.py ..........                                  [ 37%]
tests/test_config_reader.py ....                                         [ 41%]
tests/test_db_initializer.py ....                                        [ 45%]
tests/test_db_manager.py .................................               [ 76%]
tests/test_json_storage.py ...................                           [ 95%]
tests/test_logger_creator.py ..                                          [ 97%]
tests/test_path.py ...                                                   [100%]
src/__init__.py             0      0   100%
src/aeroplane.py          180      0   100%
src/aeroplanes_api.py      49      0   100%
src/base_api.py             7      0   100%
src/base_storage.py        23      0   100%
src/config_reader.py       14      0   100%
src/db_initializer.py      29      0   100%
src/db_manager.py         144      0   100%
src/json_storage.py       130      0   100%
src/logger_creator.py      15      0   100%
src/path.py                10      0   100%
TOTAL                     601      0   100%
Coverage HTML written to dir htmlcov/src

🎯 Результаты тестов src:
tests/test_aeroplane.py .............................                    [ 27%]
tests/test_aeroplanes_api.py ..........                                  [ 37%]
tests/test_config_reader.py ....                                         [ 41%]
tests/test_db_initializer.py ....                                        [ 45%]
tests/test_db_manager.py .................................               [ 76%]
tests/test_json_storage.py ...................                           [ 95%]
tests/test_logger_creator.py ..                                          [ 97%]
tests/test_path.py ...                                                   [100%]
================================ tests coverage ================================
-----------------------------------------------------
-----------------------------------------------------
============================= 104 passed in 0.25s ==============================
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
- [x] [main.py](main.py) — Точка входа в приложение, интерактивный режим, выбор хранилища (БД/JSON)
- [x] [aeroplane.py](src/aeroplane.py) — Модель с валидацией, сериализацией, сравнением
- [x] [aeroplanes_api.py](src/aeroplanes_api.py) — Модуль для работы с Nominatim + OpenSky API
- [x] [base_api.py](src/base_api.py) — Модуль базового класса для работы с внешними API
- [x] [base_storage.py](src/base_storage.py) — Модуль базового класса для работы с хранилищем самолётов
- [x] [json_storage.py](src/json_storage.py) — Модуль класса для работы с JSON-хранилищем самолётов
- [x] [db_manager.py](src/db_manager.py) — Модуль класса для работы с PostgreSQL-хранилищем самолётов: 5 методов задания + upsert + пакетная вставка
- [x] [logger_creator.py](src/logger_creator.py) — Модуль реализующий создание логгера
- [x] [path.py](src/path.py) — Модуль реализующий работу с путями
- [x] [db_initializer.py](src/db_initializer.py), [config_reader.py](src/config_reader.py) — Инициализация БД
- [x] Логирование важных функций
- [x] Написать тесты для всей новой функциональности
- [x] Проверить линтеры (`flake8`, `mypy`, `pydocstyle`, `black`, `isort`)
- [x] Финальная вычитка документации и обновление README
- [x] Обновить документацию

## Команда проекта

- Matvey Bakirov — [mabakirov@gmail.com](mailto:mabakirov@gmail.com) — Back-End Engineer
