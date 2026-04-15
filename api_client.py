"""
api_client.py — HTTP-слой: запросы к open.er-api.com
"""

import requests

BASE_URL = "https://open.er-api.com/v6/latest/{base}"


def get_currency_rates(base: str) -> dict | None:
    """
    Получает актуальные курсы валют относительно базовой.

    Ключевые поля ответа:
        base_code            — код базовой валюты (например "USD")
        time_last_update_utc — время последнего обновления (UTC, читаемый формат)
        time_next_update_utc — время следующего обновления (UTC)
        conversion_rates     — словарь курсов: {"RUB": 90.5, "EUR": 0.93, ...}
        result               — "success" при успехе

    Возвращает dict с данными или None при ошибке.
    """
    url = BASE_URL.format(base=base.upper())

    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка сети: не удалось подключиться к серверу.")
        return None
    except requests.exceptions.Timeout:
        print("❌ Ошибка сети: превышено время ожидания ответа.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Непредвиденная ошибка сети: {e}")
        return None

    if response.status_code == 404:
        print(f"❌ Валюта «{base.upper()}» не найдена на сервере (HTTP 404).")
        return None
    if response.status_code != 200:
        print(
            f"❌ Сервер вернул ошибку {response.status_code}. "
            "Попробуйте позже или проверьте код валюты."
        )
        return None

    data = response.json()

    if data.get("result") != "success":
        error_type = data.get("error-type", "неизвестная ошибка")
        print(f"❌ API вернул ошибку: {error_type}")
        return None

    return data


def get_available_codes(data: dict) -> list[str]:
    """Возвращает список всех доступных кодов валют из ответа API."""
    return list(data.get("conversion_rates", {}).keys())
