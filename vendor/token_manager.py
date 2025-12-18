import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Optional, Any

class TokenManager:
    def __init__(self, tokens_file: str = "vendor/data/tokens.json"):
        self.tokens_file = tokens_file
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> Dict[str, Dict[str, Any]]:
        """Load tokens from JSON file"""
        try:
            with open(self.tokens_file, 'r') as f:
                data = json.load(f)
                # Check if data is in new format
                if data and isinstance(next(iter(data.values())), dict):
                    return data
                else:
                    # Convert old format to new format
                    new_data = {}
                    for token, card_number in data.items():
                        new_data[token] = {
                            'card_number': card_number,
                            'masked': f"**** **** **** {card_number[-4:]}"
                        }
                    return new_data
        except (FileNotFoundError, json.JSONDecodeError, StopIteration):
            return {}
    
    def _save_tokens(self):
        """Save tokens to JSON file"""
        with open(self.tokens_file, 'w') as f:
            json.dump(self.tokens, f, indent=2)
    
    def generate_token(self, card_data: Dict[str, str]) -> str:
        """
        Generate a secure token for card data
        Store ONLY card number and expiry - NEVER CVV!
        """
        card_number = card_data['number']
        salt = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        token_data = f"{card_number}{salt}{timestamp}"
        
        # Generate token (first 16 chars of hash)
        token = hashlib.sha256(token_data.encode()).hexdigest()[:16]
        
        # Store ONLY safe data (never CVV!)
        self.tokens[token] = {
            'card_number': card_number,
            'expiry': card_data['expiry'],  # Only expiry, not CVV!
            'masked': f"**** **** **** {card_number[-4:]}",
            'created_at': timestamp
        }
        self._save_tokens()
        
        return token
    
    def get_card_data(self, token: str) -> Optional[Dict[str, Any]]:
        """Retrieve safe card data from token (NO CVV!)"""
        return self.tokens.get(token)
    
    def validate_token(self, token: str) -> bool:
        """Check if token exists and is valid"""
        return token in self.tokens
    
    def delete_token(self, token: str) -> bool:
        """Delete a token from storage"""
        if token in self.tokens:
            del self.tokens[token]
            self._save_tokens()
            return True
        return False
    
    def get_all_tokens(self) -> Dict[str, str]:
        """Get all tokens with masked card numbers"""
        masked_tokens = {}
        for token, card_data in self.tokens.items():
            masked_tokens[token] = card_data.get('masked', '**** **** **** ****')
        return masked_tokens
    
    def token_count(self) -> int:
        """Get total number of stored tokens"""
        return len(self.tokens)
    
    def clear_all_tokens(self):
        """Clear all tokens (for testing/reset)"""
        self.tokens = {}
        self._save_tokens()