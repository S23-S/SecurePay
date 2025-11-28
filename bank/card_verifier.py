import re
import random
from typing import Dict, Tuple
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import CardValidator

class CardVerifier:
    def __init__(self, valid_cards: Dict):
        self.valid_cards = valid_cards
        self.validator = CardValidator()
        self.fraud_patterns = self._initialize_fraud_patterns()
    
    def _initialize_fraud_patterns(self) -> Dict:
        """Initialize known fraud detection patterns"""
        return {
            'velocity_limits': 5,  # Max transactions per hour
            'high_amount_threshold': 1000.0,
            'suspicious_bins': ['6060', '5110']  # Known risky BINs
        }
    
    def verify_card(self, card_data: Dict, transaction_amount: float = 0.0) -> Tuple[bool, str]:
        """
        Comprehensive card verification
        Returns (is_valid, reason)
        """
        card_number = card_data['number']
        
        # 1. Basic format validation
        if not self.validator.validate_card_format(card_number):
            return False, "Invalid card format"
        
        # 2. Expiry validation
        if not self.validator.validate_expiry(card_data['expiry']):
            return False, "Card expired or invalid expiry date"
        
        # 3. CVV validation
        if not self.validator.validate_cvv(card_data['cvv']):
            return False, "Invalid CVV"
        
        # 4. Check if card exists in bank database
        if card_number not in self.valid_cards:
            return False, "Card not found in bank system"
        
        card_info = self.valid_cards[card_number]
        
        # 5. Expiry match check
        if card_info['expiry'] != card_data['expiry']:
            return False, "Card expiry mismatch"
        
        # 6. Sufficient funds check
        if card_info['balance'] < transaction_amount:
            return False, "Insufficient funds"
        
        # 7. Fraud detection checks
        fraud_check, fraud_reason = self._fraud_detection(card_number, transaction_amount)
        if not fraud_check:
            return False, fraud_reason
        
        return True, "Card verification successful"
    
    def _fraud_detection(self, card_number: str, amount: float) -> Tuple[bool, str]:
        """Advanced fraud detection checks"""
        
        # Check for suspicious BIN
        bin_number = card_number[:4]
        if bin_number in self.fraud_patterns['suspicious_bins']:
            return False, "Suspicious card issuer"
        
        # High amount threshold
        if amount > self.fraud_patterns['high_amount_threshold']:
            # 30% chance of flagging high amount as suspicious
            if random.random() < 0.3:
                return False, "High amount requires manual verification"
        
        # Simulate various fraud scenarios (15% chance total)
        fraud_risk = random.random()
        
        if fraud_risk < 0.05:  # 5% chance
            return False, "Suspicious transaction pattern"
        elif fraud_risk < 0.10:  # 5% chance
            return False, "Velocity limit exceeded"
        elif fraud_risk < 0.15:  # 5% chance
            return False, "Geographic anomaly detected"
        
        return True, "No fraud detected"
    
    def get_card_info(self, card_number: str) -> Dict:
        """Get card information from bank database"""
        return self.valid_cards.get(card_number, {})
    
    def update_card_balance(self, card_number: str, amount: float):
        """Update card balance after transaction"""
        if card_number in self.valid_cards:
            self.valid_cards[card_number]['balance'] -= amount
    
    def add_fraud_pattern(self, pattern_type: str, value):
        """Add new fraud detection pattern"""
        self.fraud_patterns[pattern_type] = value