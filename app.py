from flask import Flask, render_template, request
from datetime import datetime
import socket
import json
import aiohttp
import asyncio
from datetime import datetime, timedelta

app = Flask(__name__)

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 5000
JSON_FILE_PATH = "storage/data.json"


class ExchangeRateFetcher:
    def __init__(self):
        self.base_url = "https://api.privatbank.ua/p24api/exchange_rates"

    async def fetch_exchange_rate(self, session, date):
        url = f"{self.base_url}?json&date={date}"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data["exchangeRate"]
            else:
                return []

    async def get_exchange_rates(self, start_date, end_date):
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            date_range = [
                start_date + timedelta(days=i)
                for i in range((end_date - start_date).days + 1)
            ]
            date_strings = [date.strftime("%d.%m.%Y") for date in date_range]

            tasks = [self.fetch_exchange_rate(session, date) for date in date_strings]
            results = await asyncio.gather(*tasks)
            return results


def send_data_to_udp_server(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = json.dumps(data).encode("utf-8")
    client_socket.sendto(message, (UDP_SERVER_IP, UDP_SERVER_PORT))
    client_socket.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/message", methods=["GET", "POST"])
def message():
    if request.method == "POST":
        username = request.form["username"]
        message_text = request.form["message"]
        timestamp = str(datetime.now())

        data = {timestamp: {"username": username, "message": message_text}}

        send_data_to_udp_server(data)

    return render_template("message.html")


@app.route("/get_exchange_rates", methods=["GET"])
def getting_exchange_rates():
    return render_template("getting_exchange_rates.html")


@app.route('/get_exchange_rates', methods=['POST'])
def get_exchange_rates():
    fetcher = ExchangeRateFetcher()
    days = int(request.form["days"])
    # print(days)
    
    # Разделение строки с запятыми на список валют
    currencies = request.form["currencies"].split(',')
    # print(currencies)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    exchange_rates = loop.run_until_complete(fetcher.get_exchange_rates(start_date, end_date))

    formatted_rates = []
    # print(exchange_rates)
    for date, rates in zip((start_date + timedelta(days=i) for i in range(days)), exchange_rates):
        formatted_entry = {"date": date.strftime("%d.%m.%Y")}
        for currency in currencies:
            rate_value = next((rate["purchaseRateNB"] for rate in rates if rate["currency"].upper() == currency.upper()), None)
            formatted_entry[currency] = rate_value
        formatted_rates.append(formatted_entry)
    # print(formatted_rates)
    # print(currencies)
    return render_template("result.html", result=formatted_rates, currencies=currencies)

@app.route("/<variable>")
def error(variable):
    if variable != "message":
        print(variable)
        return render_template("error.html"), 404


if __name__ == "__main__":
    app.run(port=3000, debug=True)
