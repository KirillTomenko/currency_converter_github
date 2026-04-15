"""
storage.py — I/O-слой: кэширование данных в JSON-файл
"""

import json
import os
from datetime import datetime, timezone

DEFAULT_PATH = "currency_rate.json"
CACHE_TTL_HOURS = 24


def save_to_file(data: dict, path: str = DEFAULT_PATH) -> None:
    """Сохраняет словарь data в JSON-файл с отступами и поддержкой UTF-8."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"✅ Данные сохранены в «{path}».")


def read_from_file(path: str = DEFAULT_PATH) -> dict | None:
    """
    Читает JSON-файл и возвращает словарь.
    Возвращает None, если файл не существует или повреждён.
    """
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠️  Не удалось прочитать кэш ({e}). Данные будут обновлены.")
        return None


def is_cache_fresh(path: str = DEFAULT_PATH, ttl_hours: int = CACHE_TTL_HOURS) -> bool:
    """
    Проверяет, моложе ли файл-кэш заданного числа часов (по умолчанию 24).
    Возвращает True, если кэш актуален.
    """
    if not os.path.exists(path):
        return False
    mtime = os.path.getmtime(path)
    age_hours = (datetime.now(timezone.utc).timestamp() - mtime) / 3600
    return age_hours < ttl_hours


def get_cached_or_update(base: str, path: str = DEFAULT_PATH) -> dict | None:
    """
    Если кэш существует и свежее 24 ч — читает из файла.
    Иначе запрашивает API, сохраняет и возвращает результат.
    """
    # Импорт здесь, чтобы избежать циклических зависимостей
    from api_client import get_currency_rates

    cached = read_from_file(path)

    if is_cache_fresh(path) and cached and base.upper() in cached:
        print(f"📂 Данные взяты из кэша «{path}» (свежее 24 ч).")
        return cached[base.upper()]

    print(f"🌐 Запрашиваю свежие данные для {base.upper()}...")
    data = get_currency_rates(base)
    if data is None:
        return None

    # Обновляем только нужный ключ, остальные оставляем
    if cached is None:
        cached = {}
    cached[base.upper()] = data
    save_to_file(cached, path)
    return data
