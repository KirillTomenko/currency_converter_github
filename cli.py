"""
cli.py — интерфейс командной строки: мини-CLI для конвертера валют
"""

from api_client import get_available_codes
from storage import get_cached_or_update

DISPLAY_CURRENCIES = ["RUB", "EUR", "GBP"]


# ─── вспомогательные функции ────────────────────────────────────────────────

def validate_currency(code: str, available: list[str]) -> bool:
    """Проверяет, есть ли код валюты в списке доступных."""
    if code.upper() not in available:
        print(
            f"❌ Валюта «{code.upper()}» не найдена.\n"
            f"   Доступных валют: {len(available)}. "
            "Введите корректный трёхбуквенный код (например: USD, EUR, RUB)."
        )
        return False
    return True


def ask_currency(prompt: str, available: list[str] | None = None) -> str | None:
    """
    Запрашивает код валюты у пользователя.
    Если передан список available — валидирует ввод.
    """
    raw = input(prompt).strip().upper()
    if not raw:
        print("❌ Вы ввели пустую строку.")
        return None
    if available and not validate_currency(raw, available):
        return None
    return raw


def ask_amount(prompt: str) -> float | None:
    """Запрашивает числовую сумму, возвращает float или None при ошибке."""
    raw = input(prompt).strip().replace(",", ".")
    try:
        value = float(raw)
        if value <= 0:
            print("❌ Сумма должна быть положительным числом.")
            return None
        return value
    except ValueError:
        print(f"❌ «{raw}» — не число. Введите, например: 100 или 49.90")
        return None


# ─── режимы работы ──────────────────────────────────────────────────────────

def show_rates(base: str) -> None:
    """
    Выводит курсы для DISPLAY_CURRENCIES относительно базовой валюты.
    Читает из кэша, если он свежий; иначе обновляет.
    """
    data = get_cached_or_update(base)
    if data is None:
        return

    rates: dict = data.get("conversion_rates", {})
    updated = data.get("time_last_update_utc", "—")
    next_upd = data.get("time_next_update_utc", "—")

    print(f"\n{'─'*42}")
    print(f"  Базовая валюта : {data.get('base_code', base.upper())}")
    print(f"  Обновлено      : {updated}")
    print(f"  Следующее обн. : {next_upd}")
    print(f"{'─'*42}")

    targets = [c for c in DISPLAY_CURRENCIES if c != base.upper()]
    for code in targets:
        rate = rates.get(code)
        if rate is not None:
            print(f"  1 {base.upper():>3}  =  {rate:>12.4f}  {code}")
        else:
            print(f"  {code}: данные недоступны")

    print(f"{'─'*42}\n")


def convert_amount(from_cur: str, to_cur: str, amount: float) -> None:
    """
    Конвертирует сумму из одной валюты в другую.
    Использует кэш базовой валюты.
    """
    data = get_cached_or_update(from_cur)
    if data is None:
        return

    rates: dict = data.get("conversion_rates", {})
    available = get_available_codes(data)

    if not validate_currency(to_cur, available):
        return

    rate = rates.get(to_cur.upper())
    if rate is None:
        print(f"❌ Курс для {to_cur.upper()} не найден в ответе API.")
        return

    result = amount * rate
    print(
        f"\n  {amount:,.4f} {from_cur.upper()}  =  "
        f"{result:,.4f} {to_cur.upper()}\n"
        f"  (курс: 1 {from_cur.upper()} = {rate:.4f} {to_cur.upper()})\n"
    )


# ─── главное меню ────────────────────────────────────────────────────────────

def main_menu() -> None:
    print("\n╔══════════════════════════════════╗")
    print("║     Конвертер валют  v1.0        ║")
    print("╚══════════════════════════════════╝")

    while True:
        print("\n  1  Курсы валют для базовой валюты")
        print("  2  Конвертировать сумму")
        print("  0  Выход")

        choice = input("\nВаш выбор: ").strip()

        if choice == "1":
            # Получаем базовую валюту без проверки (API сам вернёт ошибку)
            base = input("  Введите базовую валюту (например, USD): ").strip().upper()
            if not base:
                print("❌ Код валюты не может быть пустым.")
                continue
            show_rates(base)

        elif choice == "2":
            # Нужно сначала загрузить данные, чтобы знать доступные коды
            from_cur = input("  Из валюты (например, USD): ").strip().upper()
            if not from_cur:
                print("❌ Код валюты не может быть пустым.")
                continue

            data = get_cached_or_update(from_cur)
            if data is None:
                continue

            available = get_available_codes(data)

            to_cur = ask_currency("  В валюту   (например, RUB): ", available)
            if to_cur is None:
                continue

            amount = ask_amount("  Сумма                      : ")
            if amount is None:
                continue

            convert_amount(from_cur, to_cur, amount)

        elif choice == "0":
            print("\nДо свидания! 👋\n")
            break

        else:
            print("⚠️  Введите 0, 1 или 2.")


if __name__ == "__main__":
    main_menu()
