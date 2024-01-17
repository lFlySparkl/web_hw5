import subprocess
import threading
from pathlib import Path
import time
import os

# Отримуємо шлях до поточного файлу
current_file_path = os.path.abspath(__file__)

def run_flask():
    subprocess.run(["python", 'app.py'], cwd=os.path.dirname(current_file_path))

def run_udp_server():
    subprocess.run(["python", "udp_server.py"], cwd=os.path.dirname(current_file_path))

if __name__ == "__main__":
    # Побудова повного шляху до папки "storage" у поточній директорії
    storage_path = os.path.join(os.path.dirname(current_file_path), 'storage')

    # Створюємо папку "storage", якщо вона ще не існує
    Path(storage_path).mkdir(exist_ok=True)

    # Запускаємо Flask у окремому потоці
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Даємо трошки часу для того, щоб Flask встиг заспрацювати
    time.sleep(2)

    # Запускаємо Socket сервер у окремому потоці
    udp_thread = threading.Thread(target=run_udp_server)
    udp_thread.daemon = True
    udp_thread.start()

    # Чекаємо завершення обох потоків
    flask_thread.join()
    udp_thread.join()