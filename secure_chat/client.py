import threading
import time
from crypto_utils import CryptoManager, generate_handshake_message, process_handshake_message
from network_utils import NetworkManager

class SecureChatClient:
    def __init__(self, host='localhost', port=8888):
        self.network = NetworkManager(host, port)
        self.crypto = CryptoManager()
        self.username = "Клиент"
        self.running = False
    
    def perform_handshake(self):

        print("Криптографическое рукопожатие...")
        




        # Генерация ключей
        self.crypto.generate_keypair()
        print("✓ RSA ключи сгенерированы")
        



        # Клиент сначала получает ключ сервера
        print("Ожидание публичного ключа от сервера...")


        while True:
            message = self.network.receive_message()
            if message:
                result = process_handshake_message(self.crypto, message)
                if result == "key_received":
                    print("✓ Публичный ключ сервера получен")
                    break
            time.sleep(0.1)
        


        # Отправка своего публичного ключа
        key_message = generate_handshake_message(self.crypto, "key_exchange")
        self.network.send_message(key_message)

        print(" Публичный ключ отправлен серверу")
        



        # Ожидание сессионного ключа
        print("Ожидание сессионного ключа...")


        while True:
            message = self.network.receive_message()
            if message:
                result = process_handshake_message(self.crypto, message)
                if result == "session_established":
                    print(" Сессионный ключ получен и установлен")
                    break
            time.sleep(0.1)
        
        print(" Криптографическое рукопожатие завершено!")
        print("Можете начинать безопасное общение!\n")






    def receive_messages(self):



        while self.running:
            try:
                encrypted_message = self.network.receive_message()
                if encrypted_message:
                    decrypted_message = self.crypto.decrypt_message(encrypted_message)
                    print(f"\nСервер: {decrypted_message}")
                    print("Вы: ", end="", flush=True)
            except Exception as e:
                if self.running:
                    print(f"\nОшибка приема: {e}")
                break






    def send_messages(self):

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

        print("=== Защищенный P2P Чат (Клиент) ===")
        
        try:
            # Подключение к серверу
            if not self.network.connect_to_server():
                return
            
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



    server_host = input("Введите IP-адрес сервера (localhost для локального теста): ").strip()
    
    if not server_host:
        server_host = 'localhost'
    
    client = SecureChatClient(server_host, 8888)
    client.start()