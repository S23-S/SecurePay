# 🔐 SecurePay - Cryptographic Payment Processing System

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Cryptography](https://img.shields.io/badge/Security-AES-red?logo=lock&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-yellowgreen)
![Status](https://img.shields.io/badge/Status-Active-success)


The SecurePay System is a comprehensive payment processing platform that implements secure communication between vendor and bank systems using modern cryptographic techniques. The primary goal is to create a robust, secure, and user-friendly payment ecosystem that demonstrates real-world financial transaction security principles.


## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Cryptographic Flow](#-cryptographic-flow)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Security Features](#-security-features)
- [Troubleshooting](#-troubleshooting)
- [Future Enhancements](#-future-enhancements)
- [License](#-license)


## 🎯 Overview

SecurePay simulates a real-world payment processing ecosystem where:
1. **Vendors** securely collect payment information
2. **Banks** validate and process transactions
3. **Cryptographic security** protects data at every stage

The system demonstrates secure communication using symmetric encryption (AES via Fernet), secure tokenization, and fraud detection algorithms.


## 🏗️ Architecture

### Components:
- **Vendor System**: Processes customer payments, tokenizes cards, communicates with bank
- **Bank System**: Verifies transactions, detects fraud, manages card balances
- **Communication Layer**: Secure message passing with encryption
- **Cryptography Layer**: AES encryption, secure key management


## ✨ Features

### Security Features
- 🔐 **AES-256 Encryption** using Fernet symmetric encryption
- 🔑 **Secure Key Management** with auto-generated and stored keys
- 🛡️ **Card Tokenization** - Never store raw card numbers
- 🚨 **Fraud Detection** - Pattern-based and random fraud simulation
- ✅ **Luhn Algorithm** validation for card numbers

### Functional Features
- 💳 **Payment Processing** with real-time validation
- 🏦 **Bank Simulation** with account balances and transaction history
- 🔄 **Secure Communication** via JSON message queues
- 📊 **Real-time Monitoring** with both vendor and bank GUIs
- 💾 **Token Storage** for recurring payments
- 📝 **Transaction Logging** with comprehensive audit trails


## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
git clone https://github.com/S23-S/SecurePay.git
cd SecurePay

### Step 2: Install Dependencies
pip install -r requirements.txt

### Step 3: Verify Installation
python --version
pip show cryptography

### Step 4: Initialize the System
python run_securepay.py

This will:
- Create necessary directories
- Generate encryption keys
- Create sample bank data
- Start both systems

## 💻 Usage

### Quick Start
1. **Start both systems:**
python run_securepay.py

This launches both Vendor and Bank interfaces automatically.

2. **Test a payment:**
- In Vendor GUI: Enter card details and amount
- Use sample card: `4111111111111111`
- Expiry: `12/25`, CVV: `123`, Amount: `100`

3. **Monitor transactions:**
- Bank GUI shows real-time transaction processing
- Both systems log activities

### Manual Startup (Advanced)

Terminal 1 - Start Bank System
python bank/bank_app.py

Terminal 2 - Start Vendor System (after bank is running)
python vendor/vendor_app.py


## 🔐 Cryptographic Flow

### Step-by-Step Encryption Process

INPUT
↓
VALIDATION (Luhn algorithm, expiry, CVV)
↓
TOKENIZATION (SHA-256 hash)
↓
ENCRYPTION (AES-256 via Fernet)
↓
SECURE TRANSMISSION (JSON message queue)
↓
BANK PROCESSING (Decryption → Verification)
↓
ENCRYPTED RESPONSE
↓
VENDOR DECRYPTION → USER NOTIFICATION


### Key Generation & Management
- Auto-generates Fernet key on first run
- Stores key in `shared/key.key`
- Uses PBKDF2 for key derivation
- Each message is independently encrypted


## 📁 Project Structure

SECUREPAY/
│
├── run_securepay.py               # System launcher
├── requirements.txt               # Python dependencies
├── README.md                      # Project documentation
│
├── shared/                        # Shared utilities & security
│   ├── __init__.py
│   ├── config.py                  # Configuration & validation
│   ├── encryption.py              # Cryptography implementation
│   └── key.key                    # Auto-generated encryption key
│
├── communication/                 # Secure communication layer
│   ├── __init__.py
│   ├── message_bus.py             # Message queue system
│   ├── protocols.py               # Message formats & rules
│   └── communication_data/        # Message storage
│       ├── bank_to_vendor.json
│       └── vendor_to_bank.json
│
├── bank/                          # Bank system components
│   ├── __init__.py
│   ├── bank_app.py                # Bank main application
│   ├── bank_gui.py                # Bank monitoring interface
│   ├── card_verifier.py           # Card validation logic
│   ├── transaction_manager.py     # Core transaction processing
│   └── data/                      # Bank data storage
│       ├── valid_cards.json
│       └── transactions.json
│
├── vendor/                        # Vendor system components
│   ├── __init__.py
│   ├── vendor_app.py              # Vendor main application
│   ├── payment_gui.py             # Vendor payment interface
│   ├── payment_processor.py       # Payment processing logic
│   ├── token_manager.py           # Token management
│   └── data/                      # Vendor data storage
│       ├── tokens.json
│       └── payment_log.json


## 🧪 Testing

### Test Card Numbers
Use these test cards from the sample data:

| Card Number      | Expiry | CVV | Balance   | Type             |
|------------------|--------|-----|-----------|------------------|
| 4111111111111111 | 12/25  | 123 | $1000.00  | Visa             |
| 5500000000000004 | 06/24  | 456 | $500.00   | Mastercard       |
| 340000000000009  | 09/26  | 789 | $1500.00  | American Express |
| 6011000000000004 | 03/25  | 012 | $750.00   | Discover         |


### Testing Scenarios

1. **Successful Payment:**
Card: 4111111111111111
Amount: 100
Result: ✅ APPROVED

2. **Insufficient Funds:**
Card: 5500000000000004
Amount: 600
Result: ❌ DECLINED - Insufficient funds

3. **Fraud Detection:**
- System randomly flags 10% of transactions as suspicious
- High amounts (>$1000) have higher scrutiny

4. **Tokenization Test:**
- Check "Save card" option
- Token appears in Saved Cards list
- Token can be reused for payments


## 🛡️ Security Features

### Encryption Implementation
- **Algorithm**: AES-256 via Fernet (symmetric encryption)
- **Key Management**: Auto-generated, securely stored
- **Data Protection**: All sensitive data encrypted before transmission
- **Message Integrity**: Each message independently encrypted/decrypted

### Card Data Protection
- **Never Stored**: Raw card numbers never saved by vendor
- **Tokenization**: SHA-256 tokens replace card numbers
- **Masked Display**: Only last 4 digits visible in interfaces
- **Secure Deletion**: Proper deletion mechanisms

### Fraud Prevention
- **Pattern Detection**: Velocity limits, high amount flags
- **Suspicious BINs**: Known risky card issuers flagged
- **Random Checks**: 10% transactions undergo extra scrutiny
- **Balance Verification**: Real-time fund checking


## 🔧 Troubleshooting

### Common Issues & Solutions

1. **"Key file not found" error**
- Delete and regenerate key
rm shared/key.key
python run_securepay.py

2. **Bank not responding**
- Check bank is running
python bank/bank_app.py

- Check communication files
ls communication_data/

3. **Import errors**
- Ensure you're in the right directory
pwd # Should show /path/to/securepay

- Install dependencies
pip install -r requirements.txt

4. **GUI not showing**
- Check Tkinter installation
python -m tkinter

- Install Tkinter (Ubuntu/Debian)
sudo apt-get install python3-tk


### Debug Mode
- Enable verbose logging by modifying `run_securepay.py`:
- Add at the beginning of main()
- import logging
- logging.basicConfig(level=logging.DEBUG)


## 📈 Future Enhancements

### Planned Features
- **Asymmetric Encryption**: RSA for key exchange
- **Digital Signatures**: HMAC for message integrity
- **Multi-bank Support**: Multiple bank connections
- **Database Integration**: PostgreSQL for production
- **REST API**: HTTP/S communication layer
- **Web Interface**: Browser-based access

### Security Improvements
- **HSM Integration**: Hardware Security Module support
- **PCI DSS Compliance**: Full payment card compliance
- **Quantum Resistance**: Post-quantum cryptography
- **Audit Logging**: Comprehensive security audits

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Cryptography Library**: `cryptography` Python package
- **GUI Framework**: Tkinter for interface
- **Card Validation**: Luhn algorithm implementation
- **Educational Purpose**: Designed for cryptography learning

## 📞 Support

For issues, questions, or contributions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Open a GitHub Issue

---

**⚠️ DISCLAIMER**: This is an educational project demonstrating cryptographic principles. Not for production use with real financial data. Always consult security professionals for production payment systems.











