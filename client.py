import socket
import threading
from mss import mss
import datetime
import os
import time
import sys

# Создание сокета
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Подключение к серверу
server_address = ('localhost', 65029)
client_socket.connect(server_address)
print('подключились к серверу')

# Функция для создания и отправки скриншота


def send_screenshot():
    print('зашли в создание скрина!!!!')
    # Отправка команды "screenshot" серверу
    # client_socket.sendall(b'screenshot')

    # Создание объекта mss для создания скриншота
    with mss() as sct:
        # Формирование имени файла на основе текущей даты и времени
        current_time = datetime.datetime.now()
        filename = current_time.strftime("%Y-%m-%d_%H-%M-%S.png")

        print('взяли время')

        # Создание скриншота и сохранение его в файл
        sct.shot(output=filename)
        print('создали скриншот и сохранили его')

        # Чтение данных скриншота из файла в бинарном формате
        with open(filename, 'rb') as f:
            screenshot_data = f.read()
        print('прочитали скрин')
        # Отправка данных скриншота на сервер
        # Отправка данных скриншота на сервер
        client_socket.sendall(f'IMAGE:{filename}:{screenshot_data}'.encode())

        print('отправили скрин')

        # Удаление временного файла
        # os.remove(filename)
        sys.exit()

# Отправка скриншотов по требованию сервера


def handle_commands():

    print('зашли в цикл')
    # Ожидание команды от сервера
    print('читаем файл')
    with open('data.txt', 'r') as f:
        command = f.read()
    # command = client_socket.recv(1024).decode()
        print('сравниваем')
        print(command)
        if command == 'screenshot':
            print('идём делать скрин')
            # Если команда - "screenshot", создаем и отправляем скриншот
            send_screenshot()
        # Задержка перед следующей итерацией цикла
        time.sleep(0.5)

    # Закрытие соединения
    client_socket.close()


print('запуск потока для создания скрина')
# Запуск отдельного потока для обработки команд
command_thread = threading.Thread(target=handle_commands)
command_thread.start()
