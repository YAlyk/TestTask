#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <Windows.h>
#include <lmcons.h>
#include <chrono>
#include <string>
#include <thread>
#pragma comment(lib, "ws2_32.lib")

int main() {
    system("chcp 1251");
    // Инициализация Winsock
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "Не удалось инициализировать Winsock\n";
        return -1;
    }

    // Создание сокета
    SOCKET clientSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (clientSocket == INVALID_SOCKET) {
        std::cerr << "Не удалось создать сокет\n";
        WSACleanup();
        return -1;
    }

    // Установка адреса сервера и порта
    sockaddr_in serverAddress{};
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(65029);  // Порт сервера

    if (inet_pton(AF_INET, "127.0.0.1", &(serverAddress.sin_addr)) <= 0) {
        std::cerr << "Ошибка при преобразовании IP-адреса\n";
        closesocket(clientSocket);
        WSACleanup();
        return -1;
    }

    // Установка соединения с сервером
    if (connect(clientSocket, (struct sockaddr*)&serverAddress, sizeof(serverAddress)) == SOCKET_ERROR) {
        std::cerr << "Не удалось установить соединение\n";
        closesocket(clientSocket);
        WSACleanup();
        return -1;
    }

    // Основной цикл клиента
    while (true) {
        // Получение информации о клиенте
        char username[UNLEN + 1];
        DWORD usernameLength = UNLEN + 1;
        GetUserNameA(username, &usernameLength);

        char computerName[MAX_COMPUTERNAME_LENGTH + 1];
        DWORD computerNameLength = MAX_COMPUTERNAME_LENGTH + 1;
        GetComputerNameA(computerName, &computerNameLength);

        char hostname[NI_MAXHOST];
        gethostname(hostname, NI_MAXHOST);

        // Получение текущего времени
        auto current_time = std::chrono::system_clock::now();
        std::time_t timestamp = std::chrono::system_clock::to_time_t(current_time);

        // Формирование сообщения для отправки
        std::string message = std::string(username) + "," + std::string(hostname) + "," + std::string(computerName) +
            "," + std::to_string(timestamp);
        std::cout << "Отправляемая информация: " << message << std::endl;

        // Отправка данных на сервер
        if (send(clientSocket, message.c_str(), message.length(), 0) == SOCKET_ERROR) {
            std::cerr << "Ошибка при отправке данных\n";
            closesocket(clientSocket);
            WSACleanup();
            return -1;
        }

        // Задержка перед следующей отправкой данных
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }

    // Закрытие сокета и завершение
    closesocket(clientSocket);
    WSACleanup();
    return 0;
}
