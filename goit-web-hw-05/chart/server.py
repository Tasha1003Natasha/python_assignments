import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta

import aiohttp
import names
import websockets
from aiofile import async_open
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)

BASE_URL = "https://api.privatbank.ua/p24api"


async def fetch_rate(session, url):

    try:

        async with session.get(url, timeout=10) as response:

            response.raise_for_status()

            return await response.json()

    except aiohttp.ClientError as error:
        return {"error": f"Network error: {error}"}

    except asyncio.TimeoutError:
        return {"error": "Request timeout"}

    except Exception as error:
        return {"error": f"Unexpected error: {error}"}


def get_last_days(count):

    return [
        (
            datetime.now() - timedelta(days=i)
        ).strftime("%d.%m.%Y")
        for i in range(count)
    ]


def parse_currency(data, currencies):

    if not data or "error" in data:
        return data

    result = {}

    date = data.get("date")

    result[date] = {}

    for item in data.get("exchangeRate", []):

        currency = item.get("currency")

        if currency in currencies:

            result[date][currency] = {
                "sale": item.get("saleRate") or item.get("saleRateNB"),
                "purchase": item.get("purchaseRate") or item.get("purchaseRateNB")
            }

    return result


async def get_exchange(days, currencies):

    days_list = get_last_days(days)

    async with aiohttp.ClientSession() as session:

        tasks = []

        for date in days_list:

            url = (
                f"{BASE_URL}/exchange_rates"
                f"?json&date={date}"
            )

            tasks.append(
                fetch_rate(session, url)
            )

        responses = await asyncio.gather(*tasks)

        rate_list = []

        for response in responses:

            parsed_data = parse_currency(
                response,
                currencies
            )

            if parsed_data:
                rate_list.append(parsed_data)

        return rate_list


async def log_exchange(message):

    async with async_open(
        "exchange.log",
        "a"
    ) as file:

        await file.write(
            f"{datetime.now()} | "
            f"{message}\n"
        )


async def exchange_command(message):

    parts = message.split()

    days = 1

    currencies = ["USD", "EUR"]

    if len(parts) >= 2:

        try:

            days = int(parts[1])

            if days < 1 or days > 10:
                return (
                    "Days count must be "
                    "between 1 and 10"
                )

        except ValueError:

            return "Invalid days count"

    if len(parts) >= 3:

        currencies = [
            currency.upper()
            for currency in parts[2:]
        ]

    result = await get_exchange(
        days,
        currencies
    )

    return json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )


def get_cli_args():

    days = 1
    currencies = ["USD", "EUR"]

    if len(sys.argv) > 1:

        try:

            days = int(sys.argv[1])

            if days < 1 or days > 10:
                raise ValueError

        except ValueError:

            print(
                "Days count must be "
                "between 1 and 10"
            )

            sys.exit(1)

    if len(sys.argv) > 2:

        currencies = [
            currency.upper()
            for currency in sys.argv[2:]
        ]

    return days, currencies


class Server:

    clients = set()

    async def register(
        self,
        ws: WebSocketServerProtocol
    ):

        ws.name = names.get_full_name()

        self.clients.add(ws)

        logging.info(
            f"{ws.remote_address} connects"
        )

    async def unregister(
        self,
        ws: WebSocketServerProtocol
    ):

        self.clients.remove(ws)

        logging.info(
            f"{ws.remote_address} disconnects"
        )

    async def send_to_clients(
        self,
        message: str
    ):

        for client in self.clients:
            await client.send(message)

    async def ws_handler(
        self,
        ws: WebSocketServerProtocol
    ):

        await self.register(ws)

        try:

            await self.distribute(ws)

        except ConnectionClosedOK:
            pass

        finally:

            await self.unregister(ws)

    async def distribute(
        self,
        ws: WebSocketServerProtocol
    ):

        async for message in ws:

            await log_exchange(f"{ws.name}: {message}")

            if message.startswith(
                "exchange"
            ):

                exchange = (
                    await exchange_command(
                        message
                    )
                )

                await log_exchange(
                    f": {message}")

                await self.send_to_clients(
                    exchange
                )

            elif (
                message
                == "Hello server"
            ):

                await self.send_to_clients(
                    "Привіт мої карапузи!"
                )

            else:

                await self.send_to_clients(
                    f"{ws.name}: "
                    f"{message}"
                )


async def main():

    if len(sys.argv) > 1:

        days, currencies = get_cli_args()

        result = await get_exchange(
            days,
            currencies
        )

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False
            )
        )

        return

    server = Server()

    async with websockets.serve(
        server.ws_handler,
        "localhost",
        8080
    ):

        print(
            "WebSocket server started "
            "on ws://localhost:8080"
        )

        await asyncio.Future()


if __name__ == "__main__":

    asyncio.run(main())
