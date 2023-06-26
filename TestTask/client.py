import socket
from mss import mss
import datetime
import os

# Создание сокета
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Подключение к серверу
server_address = ('localhost', 65029)
client_socket.connect(server_address)

# Функция для создания и отправки скриншота
def send_screenshot():
    # Создание объекта mss для создания скриншота
    with mss() as sct:
        # Формирование имени файла на основе текущей даты и времени
        current_time = datetime.datetime.now()
        filename = current_time.strftime("%Y-%m-%d_%H-%M-%S.png")

        # Создание скриншота и сохранение его в файл
        sct.shot(output=filename)

        # Чтение данных скриншота из файла в бинарном формате
        with open(filename, 'rb') as f:
            screenshot_data = f.read()

        # Отправка данных скриншота на сервер
        client_socket.sendall(screenshot_data)

        # Удаление временного файла
        os.remove(filename)

# Отправка скриншотов по требованию сервера
while True:
    # Ожидание команды от сервера
    command = client_socket.recv(1024).decode()

    if command == 'screenshot':
        # Если команда - "screenshot", создаем и отправляем скриншот
        send_screenshot()
    elif command == 'exit':
        # Если команда - "exit", выходим из цикла
        break

# Закрытие соединения
client_socket.close()
