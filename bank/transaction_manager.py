import json
import random
from datetime import datetime
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.encryption import EncryptionManager
from shared.config import CardValidator
from communication.message_bus import MessageBus
from bank.card_verifier import CardVerifier

class TransactionManager:
    def __init__(self):
        self.encryption = EncryptionManager()
        self.validator = CardValidator()
        self.message_bus = MessageBus()
        
        # Load valid cards FIRST before creating card_verifier
        self.valid_cards = self.load_valid_cards()
        
        # Now create card_verifier with the loaded cards
        self.card_verifier = CardVerifier(self.valid_cards)
        
        self.statistics = {
            'total': 0,
            'approved': 0,
            'declined': 0,
            'fraud': 0
        }
        self.transaction_history = []
    
    def load_valid_cards(self):
        """Load valid cards from JSON file"""
        try:
            with open("bank/data/valid_cards.json", "r") as f:
                return json.load(f)
        except:
            # Sample valid cards for demo
            valid_cards = {
                "4111111111111111": {"expiry": "12/25", "balance": 1000.0},
                "5500000000000004": {"expiry": "06/24", "balance": 500.0},
                "340000000000009": {"expiry": "09/26", "balance": 1500.0},
                "6011000000000004": {"expiry": "03/25", "balance": 750.0},
                "6060123456789012": {"expiry": "12/25", "balance": 1000.0},  # For fraud testing
                "5110987654321098": {"expiry": "12/25", "balance": 1000.0},  # For fraud testing
            }
            self.save_valid_cards(valid_cards)
            return valid_cards
    
    def save_valid_cards(self, valid_cards=None):
        """Save valid cards to JSON file"""
        if valid_cards is None:
            valid_cards = self.valid_cards
        with open("bank/data/valid_cards.json", "w") as f:
            json.dump(valid_cards, f, indent=2)
    
    def check_pending_transactions(self):
        return self.message_bus.receive_from_vendor()
    
    def validate_transaction(self, card_data: dict, amount: float) -> dict:
        """Basic validation with simple fraud detection"""
        card_number = card_data['number']
        
        # Basic validation
        if not self.validator.validate_card_format(card_number):
            return {'status': 'DECLINED', 'reason': 'Invalid card format'}
        
        if not self.validator.validate_expiry(card_data['expiry']):
            return {'status': 'DECLINED', 'reason': 'Card expired'}
        
        # Check if card exists and has sufficient funds
        if card_number not in self.valid_cards:
            return {'status': 'DECLINED', 'reason': 'Card not found'}
        
        card_info = self.valid_cards[card_number]
        if card_info['expiry'] != card_data['expiry']:
            return {'status': 'DECLINED', 'reason': 'Expiry mismatch'}
        
        if card_info['balance'] < float(amount):
            return {'status': 'DECLINED', 'reason': 'Insufficient funds'}
        
        # Simulate basic fraud detection (10% chance of random decline)
        if random.random() < 0.1:
            return {'status': 'DECLINED', 'reason': 'Suspicious activity'}
        
        # Process payment
        card_info['balance'] -= float(amount)
        self.save_valid_cards()
        
        return {'status': 'APPROVED', 'reason': 'Payment successful'}
    
    def process_transaction(self, encrypted_data: str) -> dict:
        try:
            # Decrypt the message
            payment_data = self.encryption.decrypt_data(encrypted_data)
            
            # Validate transaction using ADVANCED fraud detection
            card_data = payment_data['card_data']
            amount = float(payment_data['amount'])
            
            # USE CARD VERIFIER for comprehensive fraud detection
            is_valid, reason = self.card_verifier.verify_card(card_data, amount)
            
            # Determine status based on verification
            if is_valid:
                # Card passed fraud checks, now check funds
                card_number = card_data['number']
                if card_number not in self.valid_cards:
                    status = 'DECLINED'
                    reason = 'Card not found'
                else:
                    card_info = self.valid_cards[card_number]
                    if card_info['expiry'] != card_data['expiry']:
                        status = 'DECLINED'
                        reason = 'Expiry mismatch'
                    elif card_info['balance'] < float(amount):
                        status = 'DECLINED'
                        reason = 'Insufficient funds'
                    else:
                        # Process payment
                        card_info['balance'] -= float(amount)
                        self.save_valid_cards()
                        status = 'APPROVED'
                        reason = 'Payment successful'
            else:
                # Card failed fraud checks - determine if it's fraud or regular decline
                fraud_keywords = ['suspicious', 'fraud', 'pattern', 'velocity', 
                                'geographic', 'issuer', 'high amount', 'activity', 'anomaly']
                
                if any(keyword in reason.lower() for keyword in fraud_keywords):
                    status = 'FRAUD'
                else:
                    status = 'DECLINED'
            
            # Prepare response
            response = {
                'transaction_id': payment_data['transaction_id'],
                'timestamp': datetime.now().isoformat(),
                'status': status,  # Now includes FRAUD status
                'reason': reason,
                'card_last4': card_data['number'][-4:],
                'amount': amount
            }
            
            # Update statistics with FRAUD tracking
            self.update_statistics(response['status'], response['reason'])
            
            # Send response back to vendor
            encrypted_response = self.encryption.encrypt_data(response)
            self.message_bus.send_to_vendor(encrypted_response)
            
            # Log transaction
            self.transaction_history.append(response)
            self.save_transaction_history()
            
            # Debug output
            print(f"🏦 Bank processed: {status} - {reason}")
            
            return response
            
        except Exception as e:
            error_response = {
                'status': 'ERROR',
                'reason': f'Processing error: {str(e)}'
            }
            encrypted_error = self.encryption.encrypt_data(error_response)
            self.message_bus.send_to_vendor(encrypted_error)
            raise
    
    def update_statistics(self, status: str, reason: str = ""):
        """Update statistics with fraud detection"""
        self.statistics['total'] += 1
        
        if status == 'APPROVED':
            self.statistics['approved'] += 1
        elif status == 'DECLINED':
            self.statistics['declined'] += 1
        elif status == 'FRAUD':
            self.statistics['fraud'] += 1
            # Also count fraud as declined for overall stats
            self.statistics['declined'] += 1
    
    def get_statistics(self) -> dict:
        """Get current statistics"""
        return self.statistics.copy()
    
    def save_transaction_history(self):
        """Save transaction history to file"""
        with open("bank/data/transactions.json", "w") as f:
            json.dump(self.transaction_history[-100:], f, indent=2)  # Keep last 100
    
    def process_pending_messages(self):
        """Process all pending messages from vendor"""
        processed_count = 0
        while True:
            encrypted_message = self.message_bus.receive_from_vendor()
            if encrypted_message is None:
                break
            
            try:
                result = self.process_transaction(encrypted_message)
                print(f"✅ Processed transaction: {result['status']}")
                processed_count += 1
            except Exception as e:
                print(f"❌ Failed to process transaction: {e}")
        
        return processed_count
    
    def reset_statistics(self):
        """Reset all statistics to zero (for testing)"""
        self.statistics = {
            'total': 0,
            'approved': 0,
            'declined': 0,
            'fraud': 0
        }