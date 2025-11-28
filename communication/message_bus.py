import json
import time
import os
import uuid
from threading import Lock
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MessageBus:
    def __init__(self):
        self.comm_dir = "communication_data"
        os.makedirs(self.comm_dir, exist_ok=True)
        self.vendor_to_bank_file = os.path.join(self.comm_dir, "vendor_to_bank.json")
        self.bank_to_vendor_file = os.path.join(self.comm_dir, "bank_to_vendor.json")
        self.lock = Lock()
    
    def send_to_bank(self, message: str):
        """Send encrypted message to bank via file"""
        with self.lock:
            message_data = {
                'id': str(uuid.uuid4()),
                'timestamp': time.time(),
                'message': message,
                'read': False
            }
            
            # Read existing messages
            try:
                with open(self.vendor_to_bank_file, 'r') as f:
                    messages = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                messages = []
            
            # Add new message
            messages.append(message_data)
            
            # Write back
            with open(self.vendor_to_bank_file, 'w') as f:
                json.dump(messages, f, indent=2)
            
            print(f"📤 Vendor → Bank: Message {message_data['id'][:8]} sent")
    
    def send_to_vendor(self, message: str):
        """Send encrypted message to vendor via file"""
        with self.lock:
            message_data = {
                'id': str(uuid.uuid4()),
                'timestamp': time.time(),
                'message': message,
                'read': False
            }
            
            # Read existing messages
            try:
                with open(self.bank_to_vendor_file, 'r') as f:
                    messages = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                messages = []
            
            # Add new message
            messages.append(message_data)
            
            # Write back
            with open(self.bank_to_vendor_file, 'w') as f:
                json.dump(messages, f, indent=2)
            
            print(f"📤 Bank → Vendor: Message {message_data['id'][:8]} sent")
    
    def receive_from_bank(self, timeout: int = 10):
        """Receive message from bank with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self.lock:
                try:
                    with open(self.bank_to_vendor_file, 'r') as f:
                        messages = json.load(f)
                    
                    # Find unread messages
                    unread_messages = [msg for msg in messages if not msg.get('read', False)]
                    
                    if unread_messages:
                        message = unread_messages[0]
                        # Mark as read
                        for msg in messages:
                            if msg['id'] == message['id']:
                                msg['read'] = True
                        
                        # Write back
                        with open(self.bank_to_vendor_file, 'w') as f:
                            json.dump(messages, f, indent=2)
                        
                        print(f"📥 Vendor ← Bank: Message {message['id'][:8]} received")
                        return message['message']
                
                except (FileNotFoundError, json.JSONDecodeError):
                    pass
            
            time.sleep(0.5)  # Check every 500ms
        
        print("⏰ Vendor: Timeout waiting for bank response")
        return None
    
    def receive_from_vendor(self):
        """Receive message from vendor (non-blocking)"""
        with self.lock:
            try:
                with open(self.vendor_to_bank_file, 'r') as f:
                    messages = json.load(f)
                
                # Find unread messages
                unread_messages = [msg for msg in messages if not msg.get('read', False)]
                
                if unread_messages:
                    message = unread_messages[0]
                    # Mark as read
                    for msg in messages:
                        if msg['id'] == message['id']:
                            msg['read'] = True
                    
                    # Write back
                    with open(self.vendor_to_bank_file, 'w') as f:
                        json.dump(messages, f, indent=2)
                    
                    print(f"📥 Bank ← Vendor: Message {message['id'][:8]} received")
                    return message['message']
            
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        
        return None
    
    def clear_queues(self):
        """Clear all messages (for testing)"""
        with self.lock:
            for file_path in [self.vendor_to_bank_file, self.bank_to_vendor_file]:
                try:
                    with open(file_path, 'w') as f:
                        json.dump([], f)
                except:
                    pass