"""Модуль реализующий работу с путями."""

import os

ROOT_DIR = str(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
DATA_DIR = os.path.join(ROOT_DIR, "data")


def get_log_path() -> str:
    """Функция для получения пути к папке с логами."""
    return LOGS_DIR


def get_root_dir() -> str:
    """Функция для получения пути к корневой папке проекта."""
    return ROOT_DIR


def get_data_dir() -> str:
    """Функция для получения пути к папке с данными."""
    return DATA_DIR
