import json
import hashlib
import uuid
from datetime import datetime
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.encryption import EncryptionManager
from shared.config import CardValidator
from communication.message_bus import MessageBus
from vendor.token_manager import TokenManager

class PaymentProcessor:
    def __init__(self):
        self.encryption = EncryptionManager()
        self.validator = CardValidator()
        self.message_bus = MessageBus()
        self.token_manager = TokenManager()
        self.load_tokens()
    
    def load_tokens(self):
        try:
            with open("vendor/data/tokens.json", "r") as f:
                self.tokens = json.load(f)
        except:
            self.tokens = {}
    
    def save_tokens(self):
        with open("vendor/data/tokens.json", "w") as f:
            json.dump(self.tokens, f, indent=2)
    
    def validate_card_data(self, card_data: dict) -> bool:
        return (self.validator.validate_card_format(card_data['number']) and
                self.validator.validate_expiry(card_data['expiry']) and
                self.validator.validate_cvv(card_data['cvv']))
    
    def generate_token(self, card_number: str) -> str:
        salt = str(uuid.uuid4())
        token_data = f"{card_number}{salt}{datetime.now().isoformat()}"
        return hashlib.sha256(token_data.encode()).hexdigest()[:16]
    
    def mask_card_number(self, card_number: str) -> str:
        return f"**** **** **** {card_number[-4:]}"
    
    def process_payment(self, card_data: dict) -> str:
        # Validate card data
        if not self.validate_card_data(card_data):
            raise ValueError("Invalid card data")
        
        # Generate token if requested
        token = None
        if card_data.get('save_token', False):
            token = self.generate_token(card_data['number'])
            self.tokens[token] = card_data['number']
            self.save_tokens()
        
        # Prepare payment message
        payment_message = {
            'transaction_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'card_data': card_data,
            'token': token,
            'amount': card_data['amount']
        }
        
        # Encrypt and send to bank
        encrypted_message = self.encryption.encrypt_data(payment_message)
        self.message_bus.send_to_bank(encrypted_message)
        
        print("⏳ Waiting for bank response...")
        
        # Wait for response
        response = self.message_bus.receive_from_bank(timeout=30)
        if response:
            try:
                # DECRYPT the bank's response
                decrypted_response = self.encryption.decrypt_data(response)
                status = decrypted_response.get('status', 'UNKNOWN')
                reason = decrypted_response.get('reason', 'No reason provided')
                
                if status == 'APPROVED':
                    return f"✅ Payment APPROVED: {reason}"
                elif status == 'DECLINED':
                    return f"❌ Payment DECLINED: {reason}"
                else:
                    return f"⚠️ Payment {status}: {reason}"
                    
            except Exception as e:
                return f"⚠️ Payment processed but response error: {str(e)}"
        else:
            raise TimeoutError("Bank response timeout - Bank system may not be running")
    
    def get_card_from_token(self, token: str) -> dict:
        if token not in self.tokens:
            raise ValueError("Token not found")
        
        return {
            'number': self.tokens[token],
            'masked': self.mask_card_number(self.tokens[token])
        }
    
    def get_all_tokens(self) -> dict:
        return {token: self.mask_card_number(card_num) 
                for token, card_num in self.tokens.items()}
    
    def delete_token(self, token: str):
        if token in self.tokens:
            del self.tokens[token]
            self.save_tokens()
    
    def get_system_status(self) -> str:
        return f"Tokens: {len(self.tokens)} | Last update: {datetime.now().strftime('%H:%M:%S')}"