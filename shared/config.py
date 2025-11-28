import os

class Config:
    # Encryption
    KEY_FILE = "shared/key.key"
    ENCRYPTION_ALGORITHM = "AES"
    
    # Communication
    VENDOR_TO_BANK_QUEUE = "vendor_to_bank.queue"
    BANK_TO_VENDOR_QUEUE = "bank_to_vendor.queue"
    
    # File paths
    VENDOR_DATA_DIR = "vendor/data/"
    BANK_DATA_DIR = "bank/data/"
    
    # Security
    TOKEN_LENGTH = 16
    MAX_RETRY_ATTEMPTS = 3

class CardValidator:
    @staticmethod
    def validate_card_format(card_number: str) -> bool:
        """Basic Luhn algorithm check"""
        card_number = card_number.replace(" ", "").replace("-", "")
        if not card_number.isdigit():
            return False
            
        digits = [int(d) for d in card_number]
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 0:
                checksum += digit
            else:
                checksum += sum(divmod(digit * 2, 10))
        return checksum % 10 == 0
    
    @staticmethod
    def validate_expiry(expiry: str) -> bool:
        try:
            month, year = expiry.split('/')
            month = int(month)
            year = int(year)
            return 1 <= month <= 12 and year >= 23  # Valid until 2023+
        except:
            return False
    
    @staticmethod
    def validate_cvv(cvv: str) -> bool:
        return cvv.isdigit() and len(cvv) in [3, 4]