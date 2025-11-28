import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Optional

class TokenManager:
    def __init__(self, tokens_file: str = "vendor/data/tokens.json"):
        self.tokens_file = tokens_file
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> Dict[str, str]:
        """Load tokens from JSON file"""
        try:
            with open(self.tokens_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_tokens(self):
        """Save tokens to JSON file"""
        with open(self.tokens_file, 'w') as f:
            json.dump(self.tokens, f, indent=2)
    
    def generate_token(self, card_number: str) -> str:
        """
        Generate a secure token for card number
        Uses SHA-256 with salt and timestamp for uniqueness
        """
        salt = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        token_data = f"{card_number}{salt}{timestamp}"
        
        # Generate token (first 16 chars of hash)
        token = hashlib.sha256(token_data.encode()).hexdigest()[:16]
        
        # Store the mapping
        self.tokens[token] = card_number
        self._save_tokens()
        
        return token
    
    def get_card_number(self, token: str) -> Optional[str]:
        """Retrieve card number from token"""
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
        for token, card_number in self.tokens.items():
            masked_card = f"**** **** **** {card_number[-4:]}" if len(card_number) >= 4 else "****"
            masked_tokens[token] = masked_card
        return masked_tokens
    
    def token_count(self) -> int:
        """Get total number of stored tokens"""
        return len(self.tokens)
    
    def clear_all_tokens(self):
        """Clear all tokens (for testing/reset)"""
        self.tokens = {}
        self._save_tokens()