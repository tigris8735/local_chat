import socket
import threading
import json

class NetworkManager:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connection = None
        self.is_connected = False
    
    def start_server(self):
        """Запуск сервера и ожидание подключения"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        
        print(f"Сервер запущен на {self.host}:{self.port}. Ожидание подключения...")
        self.connection, address = self.socket.accept()
        self.is_connected = True
        print(f"Клиент подключен: {address}")
        return self.connection
    
    def connect_to_server(self):
        """Подключение к серверу"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            self.connection = self.socket
            self.is_connected = True
            print(f"Успешно подключен к серверу {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            print(f"Не удалось подключиться к серверу {self.host}:{self.port}")
            return False
    
    def send_message(self, message):
        """Отправка сообщения"""
        if self.is_connected and self.connection:
            try:
                # Добавляем длину сообщения для надежной передачи
                message_data = json.dumps({"data": message})
                message_length = len(message_data).to_bytes(4, byteorder='big')
                self.connection.send(message_length + message_data.encode())
                return True
            except Exception as e:
                print(f"Ошибка отправки: {e}")
                return False
        return False
    
    def receive_message(self):
        """Получение сообщения"""
        if self.is_connected and self.connection:
            try:
                # Сначала читаем длину сообщения
                length_data = self.connection.recv(4)
                if not length_data:
                    return None
                
                message_length = int.from_bytes(length_data, byteorder='big')
                # Читаем само сообщение
                message_data = b""
                while len(message_data) < message_length:
                    chunk = self.connection.recv(message_length - len(message_data))
                    if not chunk:
                        return None
                    message_data += chunk
                
                message_json = json.loads(message_data.decode())
                return message_json["data"]
            except Exception as e:
                print(f"Ошибка получения: {e}")
                return None
        return None
    
    def close(self):
        """Закрытие соединения"""
        if self.connection:
            self.connection.close()
        if self.socket:
            self.socket.close()
        self.is_connected = False