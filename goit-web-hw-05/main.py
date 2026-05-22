import platform
import aiohttp
import asyncio
from datetime import datetime, timedelta
from colorama import Fore
import sys

BASE_URL = "https://api.privatbank.ua/p24api"


async def fetch_rate(session, url):

    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            data = await response.json()
            return data

    except aiohttp.ClientError as error:
        print(Fore.RED + f"Network error: {error}")

    except asyncio.TimeoutError:
        print(Fore.RED + "Request timeout")

    except Exception as error:
        print(Fore.RED + f"Unexpected error: {error}")

    return {}


def get_days_count():

    try:

        days = int(sys.argv[1])

        if days < 1 or days > 10:
            raise ValueError

        return days

    except (IndexError, ValueError):

        print(
            Fore.RED +
            "Error: enter number from 1 to 10"
        )

        return None


def get_last_days(count):
    days = []
    for i in range(count):
        date = (
            datetime.now() - timedelta(days=i)
        ).strftime("%d.%m.%Y")
        days.append(date)

    return days


def parse_currency(data):

    if not data or "error" in data:
        return data

    result = {}

    date = data.get("date")

    result[date] = {}

    for item in data.get("exchangeRate", []):

        currency = item.get("currency")

        if currency in ["EUR", "USD"]:

            result[date][currency] = {
                "sale": item.get("saleRate"),
                "purchase": item.get("purchaseRate")
            }

    return result


def print_rates(rate_list):

    print(Fore.WHITE + "[")

    for index, day_data in enumerate(rate_list):

        print(Fore.WHITE + "  {")

        for date, currencies in day_data.items():

            print(
                Fore.LIGHTBLUE_EX +
                f"    '{date}': " +
                Fore.WHITE +
                "{"
            )

            currency_items = list(currencies.items())

            for currency_index, (currency, values) in enumerate(currency_items):

                print(
                    Fore.LIGHTBLUE_EX +
                    f"      '{currency}': " +
                    Fore.WHITE +
                    "{"
                )

                print(
                    Fore.LIGHTBLUE_EX +
                    "        'sale': " +
                    Fore.LIGHTYELLOW_EX +
                    str(values["sale"]) +
                    Fore.WHITE +
                    ","
                )

                print(
                    Fore.LIGHTBLUE_EX +
                    "        'purchase': " +
                    Fore.LIGHTYELLOW_EX +
                    str(values["purchase"])
                )

                if currency_index < len(currency_items) - 1:
                    print(Fore.WHITE + "      },")
                else:
                    print(Fore.WHITE + "      }")

            print(Fore.WHITE + "    }")

        if index < len(rate_list) - 1:
            print(Fore.WHITE + "  },")
        else:
            print(Fore.WHITE + "  }")

    print(Fore.WHITE + "]")


async def main():

    count = get_days_count()

    if count is None:
        return

    days = get_last_days(count)

    async with aiohttp.ClientSession() as session:
        rate_list = []

        for date in days:

            url = f"{BASE_URL}/exchange_rates?json&date={date}"

            data = await fetch_rate(session, url)

            parsed_data = parse_currency(data)

            if parsed_data:
                rate_list.append(parsed_data)

        print_rates(rate_list)

if __name__ == "__main__":
    asyncio.run(main())
