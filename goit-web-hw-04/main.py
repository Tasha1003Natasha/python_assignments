from flask import Flask, render_template, request
import socket
import threading
import json
from pathlib import Path
from datetime import datetime


HOST = '127.0.0.1'
HTTP_PORT = 3000
UDP_PORT = 5000

STORAGE = Path("storage")
STORAGE.mkdir(exist_ok=True)
FILE = STORAGE / "data.json"


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        name = request.form.get('username')
        message = request.form.get('message')
        timestamp = str(datetime.now())
        data = {
            timestamp: {
                "username": name,
                "message": message
            }
        }
        send_to_socket(data)
        return render_template('result.html', name=name, message=message)

    return render_template('message.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


def send_to_socket(data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        server = (HOST, UDP_PORT)

        data = json.dumps(data).encode()
        sock.sendto(data, server)


def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))

    try:
        while True:
            data, address = sock.recvfrom(1024)

            decoded = data.decode()
            data_dict = json.loads(decoded)

            print(f"Received: {data_dict} from {address}")

            if FILE.exists():
                with open(FILE, "r", encoding="utf-8") as f:
                    storage = json.load(f)
            else:
                storage = {}

            storage.update(data_dict)

            with open(FILE, "w", encoding="utf-8") as f:
                json.dump(storage, f, ensure_ascii=False, indent=2)

            print("Saved to file")

    except KeyboardInterrupt:
        print("Server stopped")

    finally:
        sock.close()


def run_http_server():
    app.run(host=HOST, port=HTTP_PORT, debug=True, use_reloader=False)


if __name__ == '__main__':
    server = threading.Thread(target=run_http_server)
    socket_server = threading.Thread(target=run_server, args=(HOST, UDP_PORT))

    server.start()
    socket_server.start()

    server.join()
    socket_server.join()
