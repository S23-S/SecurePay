from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
from enum import Enum
import json
from datetime import datetime

class MessageType(Enum):
    PAYMENT_REQUEST = "payment_request"
    PAYMENT_RESPONSE = "payment_response"
    TOKENIZATION_REQUEST = "tokenization_request"
    TOKENIZATION_RESPONSE = "tokenization_response"
    STATUS_CHECK = "status_check"
    ERROR = "error"

class TransactionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    FRAUD = "fraud"
    ERROR = "error"

@dataclass
class PaymentMessage:
    """Standardized payment message format"""
    message_type: MessageType
    transaction_id: str
    timestamp: str
    payload: Dict[str, Any]
    signature: Optional[str] = None  # For future HMAC implementation
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps({
            'message_type': self.message_type.value,
            'transaction_id': self.transaction_id,
            'timestamp': self.timestamp,
            'payload': self.payload,
            'signature': self.signature
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PaymentMessage':
        """Create PaymentMessage from JSON string"""
        data = json.loads(json_str)
        return cls(
            message_type=MessageType(data['message_type']),
            transaction_id=data['transaction_id'],
            timestamp=data['timestamp'],
            payload=data['payload'],
            signature=data.get('signature')
        )

class MessageFactory:
    """Factory for creating standardized messages"""
    
    @staticmethod
    def create_payment_request(card_data: Dict, amount: float, token: str = None) -> PaymentMessage:
        """Create a payment request message"""
        return PaymentMessage(
            message_type=MessageType.PAYMENT_REQUEST,
            transaction_id=MessageFactory._generate_transaction_id(),
            timestamp=datetime.now().isoformat(),
            payload={
                'card_data': card_data,
                'amount': amount,
                'token': token,
                'merchant_id': 'VENDOR_001'  # In real system, this would be configurable
            }
        )
    
    @staticmethod
    def create_payment_response(transaction_id: str, status: TransactionStatus, 
                              reason: str, amount: float, card_last4: str) -> PaymentMessage:
        """Create a payment response message"""
        return PaymentMessage(
            message_type=MessageType.PAYMENT_RESPONSE,
            transaction_id=transaction_id,
            timestamp=datetime.now().isoformat(),
            payload={
                'status': status.value,
                'reason': reason,
                'amount': amount,
                'card_last4': card_last4,
                'authorization_code': MessageFactory._generate_auth_code() if status == TransactionStatus.APPROVED else None
            }
        )
    
    @staticmethod
    def create_error_message(transaction_id: str, error_message: str) -> PaymentMessage:
        """Create an error message"""
        return PaymentMessage(
            message_type=MessageType.ERROR,
            transaction_id=transaction_id,
            timestamp=datetime.now().isoformat(),
            payload={
                'error': error_message,
                'severity': 'high'
            }
        )
    
    @staticmethod
    def _generate_transaction_id() -> str:
        """Generate unique transaction ID"""
        import uuid
        return f"TXN_{uuid.uuid4().hex[:8].upper()}"
    
    @staticmethod
    def _generate_auth_code() -> str:
        """Generate authorization code"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class ProtocolValidator:
    """Validates message protocol compliance"""
    
    @staticmethod
    def validate_message(message: PaymentMessage) -> Tuple[bool, str]:
        """Validate message structure and content"""
        try:
            # Check required fields
            if not message.transaction_id:
                return False, "Missing transaction ID"
            
            if not message.timestamp:
                return False, "Missing timestamp"
            
            # Validate timestamp format
            try:
                datetime.fromisoformat(message.timestamp.replace('Z', '+00:00'))
            except ValueError:
                return False, "Invalid timestamp format"
            
            # Validate payload based on message type
            if message.message_type == MessageType.PAYMENT_REQUEST:
                return ProtocolValidator._validate_payment_request(message.payload)
            elif message.message_type == MessageType.PAYMENT_RESPONSE:
                return ProtocolValidator._validate_payment_response(message.payload)
            
            return True, "Valid message"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def _validate_payment_request(payload: Dict) -> Tuple[bool, str]:
        """Validate payment request payload"""
        required_fields = ['card_data', 'amount']
        for field in required_fields:
            if field not in payload:
                return False, f"Missing required field: {field}"
        
        card_data = payload['card_data']
        card_required = ['number', 'expiry', 'cvv']
        for field in card_required:
            if field not in card_data:
                return False, f"Missing card data field: {field}"
        
        return True, "Valid payment request"
    
    @staticmethod
    def _validate_payment_response(payload: Dict) -> Tuple[bool, str]:
        """Validate payment response payload"""
        required_fields = ['status', 'reason', 'amount', 'card_last4']
        for field in required_fields:
            if field not in payload:
                return False, f"Missing required field: {field}"
        
        return True, "Valid payment response"