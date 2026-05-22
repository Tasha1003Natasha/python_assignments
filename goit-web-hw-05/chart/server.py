import asyncio
import json
import logging
from datetime import datetime, timedelta
import aiohttp
import names
import websockets
from aiofile import async_open
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from aiopath import AsyncPath
from aiofile import async_open


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

    days = []

    for i in range(count):

        date = (
            datetime.now() - timedelta(days=i)
        ).strftime("%d.%m.%Y")

        days.append(date)

    return days


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
                "sale": item.get("saleRate"),
                "purchase": item.get("purchaseRate")
            }

    return result


async def get_exchange(days, currencies):

    days_list = get_last_days(days)

    async with aiohttp.ClientSession() as session:

        tasks = []

        for date in days_list:

            url = f"{BASE_URL}/exchange_rates?json&date={date}"

            tasks.append(
                fetch_rate(session, url)
            )

        responses = await asyncio.gather(*tasks)

        rate_list = []

        for response in responses:

            parsed_data = parse_currency(response, currencies)

            if parsed_data:
                rate_list.append(parsed_data)

        return rate_list


async def log_exchange(command):

    log_file = AsyncPath("exchange.log")

    if not await log_file.exists():
        await log_file.touch()

    async with async_open(log_file, "a") as file:

        await file.write(
            f"{datetime.now()} | {command}\n"
        )


async def exchange_command(message):

    parts = message.split()

    days = 1

    currencies = ["USD", "EUR"]

    if len(parts) >= 2:

        try:

            days = int(parts[1])

            if days < 1 or days > 10:
                return "Days count must be between 1 and 10"

        except ValueError:
            return "Invalid days count"

    if len(parts) >= 3:

        currencies = [
            currency.upper()
            for currency in parts[2:]
        ]

    result = await get_exchange(days, currencies)

    return json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )


class Server:

    clients = set()

    async def register(self, ws: WebSocketServerProtocol):

        ws.name = names.get_full_name()

        self.clients.add(ws)

        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):

        self.clients.remove(ws)

        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):

        if self.clients:

            for client in self.clients:
                await client.send(message)

    async def ws_handler(self, ws: WebSocketServerProtocol):

        await self.register(ws)

        try:
            await self.distribute(ws)

        except ConnectionClosedOK:
            pass

        finally:

            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol):

        async for message in ws:

            if message.startswith("exchange"):

                await log_exchange(message)

                exchange = await exchange_command(message)

                await self.send_to_clients(exchange)

            elif message == 'Hello server':

                await self.send_to_clients(
                    "Привіт мої карапузи!"
                )

            else:

                await self.send_to_clients(
                    f"{ws.name}: {message}"
                )


async def main():

    server = Server()

    async with websockets.serve(
        server.ws_handler,
        'localhost',
        8080
    ):

        await asyncio.Future()


if __name__ == '__main__':

    asyncio.run(main())
