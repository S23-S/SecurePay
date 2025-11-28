from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from shared.config import Config

class EncryptionManager:
    def __init__(self):
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)
    
    def _load_or_create_key(self) -> bytes:
        """Load existing key or create new one"""
        key_file = Config.KEY_FILE
        
        # Create shared directory if it doesn't exist
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        
        if os.path.exists(key_file):
            try:
                with open(key_file, "rb") as f:
                    key = f.read()
                # Verify it's a valid Fernet key
                Fernet(key)
                return key
            except Exception:
                # Key file exists but is invalid, generate new one
                print("⚠️  Existing key invalid, generating new key...")
        
        # Generate new key
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        print("🔑 New encryption key generated")
        return key
    
    def encrypt_data(self, data: dict) -> str:
        """Encrypt dictionary data"""
        import json
        json_data = json.dumps(data).encode()
        encrypted = self.fernet.encrypt(json_data)
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> dict:
        """Decrypt data back to dictionary"""
        import json
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return json.loads(decrypted.decode())
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")