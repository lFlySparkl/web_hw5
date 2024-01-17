import socket
import json
from pathlib import Path

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 5000
JSON_FILE_PATH = "storage/data.json"


def save_data_to_json(data):
    with open(JSON_FILE_PATH, 'a') as json_file:
        json.dump(data, json_file)
        json_file.write('\n')


def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((UDP_SERVER_IP, UDP_SERVER_PORT))

    print(f"UDP server listening on {UDP_SERVER_IP}:{UDP_SERVER_PORT}")

    while True:
        message, client_address = server_socket.recvfrom(1024)
        data = json.loads(message.decode('utf-8'))
        for timestamp, entry in data.items():
            print(f"Received data from {client_address}: {entry}")
            save_data_to_json({timestamp: entry})


if __name__ == "__main__":
    Path("storage").mkdir(exist_ok=True)
    udp_server()