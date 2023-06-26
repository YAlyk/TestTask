import socket
import tkinter as tk
from tkinter import ttk
import datetime
import subprocess
import threading
import time

# Создание сокета
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Привязка сервера к адресу и порту
server_socket.bind(('localhost', 65029))
server_socket.listen(5)  # Ожидание до 5 подключений

# Переменная для хранения состояния сервера
is_server_running = False

# Словарь для хранения ссылок на элементы таблицы активности
user_activity = {}

# Блокировка для обеспечения безопасности работы с общими данными
lock = threading.Lock()


def handle_client_data(client_socket, client_address, data):
    username, hostname, computer, timestamp = data.split(",")
    # Вывод полученных данных на сервере
    print("Имя пользователя:", username)
    print("IP-адрес клиента:", client_address[0])
    print("Доменное имя клиента:", hostname)
    print("Имя компьютера:", computer)
    print("Последняя активность:", datetime.datetime.fromtimestamp(
        float(timestamp)).strftime("%Y-%m-%d %H:%M:%S"))

    # Обновление данных таблицы пользователей
    with lock:
        # Поиск существующей строки с именем пользователя
        existing_items = user_table.get_children()
        for item in existing_items:
            if user_table.item(item, "values")[0] == username:
                # Обновление данных в существующей строке
                user_table.set(item, "ip", client_address[0])
                user_table.set(item, "domain", hostname)
                user_table.set(item, "computer", computer)
                break
        else:
            # Добавление новой строки, если пользователь не найден
            item = user_table.insert("", "end", values=(
                username, client_address[0], hostname, computer))
            # Создание ссылки на элемент таблицы активности
            user_activity[username] = item

        # Обновление данных в таблице активности
        if username in user_activity:
            activity_item = user_activity[username]
            if activity_table.exists(activity_item):
                activity_table.set(activity_item, "activity", datetime.datetime.fromtimestamp(
                    float(timestamp)).strftime("%Y-%m-%d %H:%M:%S"))
            else:
                item = activity_table.insert("", "end", values=(username, datetime.datetime.fromtimestamp(
                    float(timestamp)).strftime("%Y-%m-%d %H:%M:%S")))
                user_activity[username] = item
        else:
            item = activity_table.insert("", "end", values=(username, datetime.datetime.fromtimestamp(
                float(timestamp)).strftime("%Y-%m-%d %H:%M:%S")))
            user_activity[username] = item

        # Обновление таблиц
        user_table.update()
        activity_table.update()


def handle_client(client_socket, client_address):
    while is_server_running:
        # Получение данных от клиента
        data = client_socket.recv(1024).decode()
        if not data:
            break  # Прерывание цикла при отсутствии данных от клиента

        print("Полученные данные:", data)

        # Обработка полученных данных
        handle_client_data(client_socket, client_address, data)

    # Закрытие соединения
    client_socket.close()


def start_server():
    global is_server_running

    if is_server_running:
        return

    is_server_running = True
    print("Сервер запущен. Ожидание подключения клиентов...")

    while is_server_running:
        # Принятие подключения от клиента
        client_socket, client_address = server_socket.accept()
        print("Подключение от клиента:", client_address)

        # Создание отдельного потока для обработки клиента
        client_thread = threading.Thread(
            target=handle_client, args=(client_socket, client_address))
        client_thread.start()


def stop_server():
    global is_server_running
    is_server_running = False
    # Закрытие сокета
    server_socket.close()
    print("Сервер остановлен.")


def create_screenshot(client_address):
    subprocess.Popen(["./client.exe", client_address])
    time.sleep(1)  # Подождать некоторое время перед отправкой текста "Exit"
    subprocess.Popen(["./client.exe", "Exit"])


# Создание графического интерфейса с помощью tkinter
root = tk.Tk()
root.title("Сервер")

# Создание таблицы для отображения пользователей
user_table_frame = ttk.Frame(root)
user_table_frame.pack(pady=10)

user_table = ttk.Treeview(user_table_frame, columns=(
    "username", "ip", "domain", "computer"))
user_table.heading("username", text="Имя пользователя")
user_table.heading("ip", text="IP-адрес")
user_table.heading("domain", text="Доменное имя")
user_table.heading("computer", text="Имя компьютера")
user_table.pack()

# Создание таблицы для отображения активности
activity_table_frame = ttk.Frame(root)
activity_table_frame.pack(pady=10)

activity_table = ttk.Treeview(
    activity_table_frame, columns=("username", "activity"))
activity_table.heading("username", text="Имя пользователя")
activity_table.heading("activity", text="Последняя активность")
activity_table.pack()

# Кнопки для управления сервером
buttons_frame = ttk.Frame(root)
buttons_frame.pack(pady=10)

start_button = ttk.Button(
    buttons_frame, text="Запустить сервер", command=lambda: threading.Thread(target=start_server).start())
start_button.pack(side=tk.LEFT, padx=5)

stop_button = ttk.Button(
    buttons_frame, text="Остановить сервер", command=stop_server)
stop_button.pack(side=tk.LEFT, padx=5)

# Кнопки для скриншота
screenshot_button_frame = ttk.Frame(root)
screenshot_button_frame.pack(pady=10)

screenshot_button_1 = ttk.Button(screenshot_button_frame, text="Сделать скриншот (127.0.0.1)",
                                 command=lambda: create_screenshot("127.0.0.1"))
screenshot_button_1.pack()

screenshot_button_2 = ttk.Button(screenshot_button_frame, text="Сделать скриншот (192.168.0.1)",
                                 command=lambda: create_screenshot("192.168.0.1"))
screenshot_button_2.pack()

root.mainloop()
