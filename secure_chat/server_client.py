import threading
import time
from crypto_utils import CryptoManager, generate_handshake_message, process_handshake_message
from network_utils import NetworkManager

class SecureChatServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.network = NetworkManager(host, port)
        self.crypto = CryptoManager()
        self.username = "Сервер"
        self.running = False
    
    def perform_handshake(self):
        """Выполнение криптографического рукопожатия"""
        print("Начало криптографического рукопожатия...")
        
        # Генерация ключей
        self.crypto.generate_keypair()
        print("✓ RSA ключи сгенерированы")
        
        # Сервер отправляет свой публичный ключ первым
        key_message = generate_handshake_message(self.crypto, "key_exchange")
        self.network.send_message(key_message)
        print("✓ Публичный ключ отправлен клиенту")
        
        # Ожидание ключа от клиента
        print("Ожидание публичного ключа от клиента...")
        while True:
            message = self.network.receive_message()
            if message:
                result = process_handshake_message(self.crypto, message)
                if result == "key_received":
                    print("✓ Публичный ключ клиента получен")
                    break
            time.sleep(0.1)
        
        # Отправка сессионного ключа
        session_message = generate_handshake_message(self.crypto, "session_key")
        self.network.send_message(session_message)
        print("✓ Сессионный ключ отправлен и установлен")
        
        print("✓ Криптографическое рукопожатие завершено!")
        print("Можете начинать безопасное общение!\n")
    
    def receive_messages(self):
        """Поток для приема сообщений"""
        while self.running:
            try:
                encrypted_message = self.network.receive_message()
                if encrypted_message:
                    decrypted_message = self.crypto.decrypt_message(encrypted_message)
                    print(f"\nКлиент: {decrypted_message}")
                    print("Вы: ", end="", flush=True)
            except Exception as e:
                if self.running:
                    print(f"\nОшибка приема: {e}")
                break
    
    def send_messages(self):
        """Поток для отправки сообщений"""
        while self.running:
            try:
                message = input("Вы: ")
                if message.lower() == '/exit':
                    self.running = False
                    break
                
                encrypted_message = self.crypto.encrypt_message(message)
                self.network.send_message(encrypted_message)
            except Exception as e:
                print(f"Ошибка отправки: {e}")
                break
    
    def start(self):
        """Запуск сервера"""
        print("=== Защищенный P2P Чат (Сервер) ===")
        
        try:
            # Запуск сервера
            self.network.start_server()
            self.running = True
            
            # Криптографическое рукопожатие
            self.perform_handshake()
            
            # Запуск потоков для приема и отправки
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            send_thread = threading.Thread(target=self.send_messages)
            
            receive_thread.start()
            send_thread.start()
            
            send_thread.join()
            
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            self.running = False
            self.network.close()
            print("\nЧат завершен.")

if __name__ == "__main__":
    # Для работы через интернет замените '0.0.0.0' на ваш внешний IP
    server = SecureChatServer('0.0.0.0', 8888)
    server.start()