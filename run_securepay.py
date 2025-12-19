"""
SecurePay System Launcher
Run this file to start both Vendor and Bank systems
"""
import os
import sys
import subprocess
import time
import json

def main():
    print("🚀 SecurePay System Launcher")
    print("=" * 40)
    
    # Check if required directories exist
    required_dirs = ['vendor', 'bank', 'shared', 'communication']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ Directory '{dir_name}' not found!")
            return
    
    print("✅ All directories found")
    
    # Create data files if they don't exist
    create_sample_data()
    
    print("\n1. Starting Bank System...")
    bank_process = None
    vendor_process = None
    
    try:
        # Start Bank system
        bank_process = subprocess.Popen([sys.executable, "bank/bank_app.py"])
        
        print("⏳ Waiting for Bank system to initialize...")
        time.sleep(5)  # Give more time for bank to start
        
        # Check if bank process is still running
        if bank_process.poll() is not None:
            print("❌ Bank system failed to start! Check the errors above.")
            return
        
        print("\n2. Starting Vendor System...")
        # Start Vendor system
        vendor_process = subprocess.Popen([sys.executable, "vendor/vendor_app.py"])
        
        print("✅ Both systems started!")
        print("💡 Close both windows to stop the systems")
        
        # Wait for processes
        bank_process.wait()
        vendor_process.wait()
        
    except Exception as e:
        print(f"❌ Error starting systems: {e}")
    finally:
        # Cleanup if any process failed
        if bank_process and bank_process.poll() is None:
            bank_process.terminate()
        if vendor_process and vendor_process.poll() is None:
            vendor_process.terminate()

def create_sample_data():
    """Create sample data files if they don't exist"""
    
    # Bank valid cards
    bank_data_dir = "bank/data"
    os.makedirs(bank_data_dir, exist_ok=True)
    
    valid_cards_file = os.path.join(bank_data_dir, "valid_cards.json")
    if not os.path.exists(valid_cards_file):
        sample_cards = {
            "4111111111111111": {
                "expiry": "12/25",
                "balance": 1000.0,
                "cardholder": "John Doe",
                "type": "Visa"
            },
            "5500000000000004": {
                "expiry": "06/24",
                "balance": 500.0,
                "cardholder": "Jane Smith",
                "type": "Mastercard"
            },
            "340000000000009": {
                "expiry": "09/26",
                "balance": 1500.0,
                "cardholder": "Bob Wilson",
                "type": "American Express"
            },
            "6011000000000004": {
                "expiry": "03/25",
                "balance": 750.0,
                "cardholder": "Alice Brown",
                "type": "Discover"
            },
            "6060123456789012": {
                "expiry": "12/25",
                "balance": 1000.0,
                "cardholder": "Test Fraud Card 1",
                "type": "Risky Issuer"
            },
            "5110987654321098": {
                "expiry": "12/25",
                "balance": 1000.0,
                "cardholder": "Test Fraud Card 2",
                "type": "Risky Issuer"
            }
        }
        with open(valid_cards_file, 'w') as f:
            json.dump(sample_cards, f, indent=2)
        print("✅ Created sample bank cards data")
    
    # Vendor data directories
    vendor_data_dir = "vendor/data"
    os.makedirs(vendor_data_dir, exist_ok=True)
    
    # Create empty tokens file
    tokens_file = os.path.join(vendor_data_dir, "tokens.json")
    if not os.path.exists(tokens_file):
        with open(tokens_file, 'w') as f:
            json.dump({}, f, indent=2)
        print("✅ Created empty tokens file")
    
    # Create empty payment log
    payment_log_file = os.path.join(vendor_data_dir, "payment_log.json")
    if not os.path.exists(payment_log_file):
        with open(payment_log_file, 'w') as f:
            json.dump([], f, indent=2)
        print("✅ Created payment log file")
    
    # Create empty transactions file for bank
    transactions_file = os.path.join(bank_data_dir, "transactions.json")
    if not os.path.exists(transactions_file):
        with open(transactions_file, 'w') as f:
            json.dump([], f, indent=2)
        print("✅ Created transactions file")

if __name__ == "__main__":
    main()