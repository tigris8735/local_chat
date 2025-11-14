import os
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import json

class CryptoManager:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.peer_public_key = None
        self.session_key = None
        
    def generate_keypair(self):
        """Генерация RSA ключевой пары"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
    
    def get_public_key_pem(self):
        """Получение публичного ключа в PEM формате"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def load_peer_public_key(self, pem_data):
        """Загрузка публичного ключа собеседника"""
        self.peer_public_key = serialization.load_pem_public_key(
            pem_data,
            backend=default_backend()
        )
    
    def encrypt_session_key(self):
        """Шифрование сессионного ключа публичным ключом собеседника"""
        if not self.peer_public_key:
            raise ValueError("Peer public key not loaded")
        
        # Генерация сессионного ключа AES
        self.session_key = AESGCM.generate_key(bit_length=256)
        
        # Шифрование сессионного ключа RSA публичным ключом
        encrypted_key = self.peer_public_key.encrypt(
            self.session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_key
    
    def decrypt_session_key(self, encrypted_key):
        """Расшифровка сессионного ключа своим приватным ключом"""
        self.session_key = self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    def encrypt_message(self, message):
        """Шифрование сообщения сессионным ключом AES-GCM"""
        if not self.session_key:
            raise ValueError("Session key not established")
        
        aesgcm = AESGCM(self.session_key)
        nonce = os.urandom(12)
        encrypted_data = aesgcm.encrypt(nonce, message.encode(), None)
        
        return base64.b64encode(nonce + encrypted_data).decode()
    
    def decrypt_message(self, encrypted_message):
        """Расшифровка сообщения сессионным ключом"""
        if not self.session_key:
            raise ValueError("Session key not established")
        
        data = base64.b64decode(encrypted_message)
        nonce = data[:12]
        ciphertext = data[12:]
        
        aesgcm = AESGCM(self.session_key)
        decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
        
        return decrypted_data.decode()

def generate_handshake_message(crypto_manager, message_type="key_exchange"):
    """Генерация сообщения для рукопожатия"""
    if message_type == "key_exchange":
        return json.dumps({
            "type": "key_exchange",
            "public_key": crypto_manager.get_public_key_pem().decode()
        })
    elif message_type == "session_key":
        encrypted_key = crypto_manager.encrypt_session_key()
        return json.dumps({
            "type": "session_key",
            "session_key": base64.b64encode(encrypted_key).decode()
        })
    return None

def process_handshake_message(crypto_manager, message):
    """Обработка сообщения рукопожатия"""
    data = json.loads(message)
    
    if data["type"] == "key_exchange":
        crypto_manager.load_peer_public_key(data["public_key"].encode())
        return "key_received"
    elif data["type"] == "session_key":
        encrypted_key = base64.b64decode(data["session_key"])
        crypto_manager.decrypt_session_key(encrypted_key)
        return "session_established"
    
    return "unknown"