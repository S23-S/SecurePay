import json
import hashlib
import uuid
import time
from datetime import datetime
import sys
import os

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
        
        # Track failed CVV attempts for rate limiting
        self.failed_attempts = {}
        self.max_attempts = 3
        self.lock_duration = 300  # 5 minutes in seconds
        
        self.load_tokens()
    
    def load_tokens(self):
        """Load tokens from file"""
        try:
            with open("vendor/data/tokens.json", "r") as f:
                self.tokens = json.load(f)
        except:
            self.tokens = {}
    
    def save_tokens(self):
        """Save tokens to file"""
        with open("vendor/data/tokens.json", "w") as f:
            json.dump(self.tokens, f, indent=2)
    
    def validate_card_data(self, card_data: dict) -> bool:
        # Check if card number is masked (contains asterisks)
        # If masked, we're using a token - skip Luhn check for masked number
        if card_data['number'].startswith('****'):
            # This is a masked number from token
            # Only validate expiry and CVV
            return (self.validator.validate_expiry(card_data['expiry']) and
                    self.validator.validate_cvv(card_data['cvv']))
        else:
            # Regular validation for manual entry
            return (self.validator.validate_card_format(card_data['number']) and
                    self.validator.validate_expiry(card_data['expiry']) and
                    self.validator.validate_cvv(card_data['cvv']))
    
    def generate_token(self, card_data: dict) -> str:
        """Generate token for card (stores only number and expiry)"""
        # Create a safe copy without CVV
        safe_card_data = {
            'number': card_data['number'],
            'expiry': card_data['expiry']
            # CVV is intentionally omitted for security!
        }
        return self.token_manager.generate_token(safe_card_data)
    
    def mask_card_number(self, card_number: str) -> str:
        return f"**** **** **** {card_number[-4:]}"
    
    def validate_cvv_with_rate_limit(self, card_number: str, cvv: str, token: str = None) -> tuple:
        """
        Validate CVV with rate limiting
        Returns: (is_valid, error_message)
        """
        # Use token as key if provided, otherwise use card number
        key = token if token else card_number
        
        # Check if locked
        if key in self.failed_attempts:
            attempts, lock_until = self.failed_attempts[key]
            
            if lock_until and time.time() < lock_until:
                remaining = int(lock_until - time.time())
                return False, f"Card locked. Try again in {remaining} seconds."
            
            if attempts >= self.max_attempts:
                # Lock the card
                self.failed_attempts[key] = (attempts, time.time() + self.lock_duration)
                return False, f"Too many attempts. Card locked for {self.lock_duration//60} minutes."
        
        # In a real system, you would validate against a secure vault
        # For demo purposes, we'll simulate validation
        # (In production, NEVER store or compare CVV like this!)
        
        # Simulate CVV validation - in reality, this would come from a secure source
        # For demo, we'll say any 3-digit number ending with '3' is valid
        is_valid = len(cvv) == 3 and cvv.isdigit() and cvv[-1] == '3'
        
        if is_valid:
            # Reset on success
            if key in self.failed_attempts:
                del self.failed_attempts[key]
            return True, "CVV validated"
        else:
            # Track failed attempt
            attempts = self.failed_attempts.get(key, (0, None))[0] + 1
            self.failed_attempts[key] = (attempts, None)
            
            remaining_attempts = self.max_attempts - attempts
            if remaining_attempts > 0:
                return False, f"Invalid CVV. {remaining_attempts} attempts remaining."
            else:
                return False, "Invalid CVV. Card will be locked on next failed attempt."
    
    def process_payment(self, card_data: dict, token: str = None) -> str:
        """Process payment, optionally using a token"""
        
        # Validate card data
        if not self.validate_card_data(card_data):
            raise ValueError("Invalid card data")
        
        # If using token, get card number and expiry from token
        actual_card_data = card_data.copy()
        if token:
            try:
                token_data = self.get_card_from_token(token)
                actual_card_data['number'] = token_data['number']
                actual_card_data['expiry'] = token_data['expiry']
            except Exception as e:
                return f"❌ Token error: {str(e)}"
        
        # Validate CVV with rate limiting
        key = token if token else actual_card_data['number']
        is_valid, message = self.validate_cvv_with_rate_limit(
            actual_card_data['number'], 
            actual_card_data['cvv'], 
            token
        )
        
        if not is_valid:
            return f"❌ CVV validation failed: {message}"
        
        # Generate new token if requested
        new_token = None
        if card_data.get('save_token', False) and not token:
            # Don't regenerate if already using a token
            new_token = self.generate_token(actual_card_data)
        
        # Prepare payment message
        payment_message = {
            'transaction_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'card_data': actual_card_data,
            'token': token or new_token,
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
                # Decrypt the bank's response
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
        """Get card data from token (NO CVV - user must enter fresh!)"""
        card_data = self.token_manager.get_card_data(token)
        if not card_data:
            raise ValueError("Token not found")
        
        return {
            'number': card_data['card_number'],
            'expiry': card_data['expiry'],
            'masked': card_data['masked']
            # CVV is NOT included - user must enter it fresh each time!
        }
    
    def get_all_tokens(self) -> dict:
        return self.token_manager.get_all_tokens()
    
    def delete_token(self, token: str):
        self.token_manager.delete_token(token)
    
    def get_system_status(self) -> str:
        token_count = self.token_manager.token_count()
        blocked_count = len([k for k, v in self.failed_attempts.items() 
                           if v[1] and time.time() < v[1]])
        return f"Tokens: {token_count} | Blocked: {blocked_count} | Last: {datetime.now().strftime('%H:%M:%S')}"