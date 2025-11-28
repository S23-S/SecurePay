import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bank.transaction_manager import TransactionManager

class BankMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏦 Bank Payment Processor")
        self.root.geometry("800x600")
        self.root.configure(bg='#f5f6fa')
        
        self.transaction_manager = TransactionManager()
        self.setup_gui()
        self.start_transaction_monitor()
        self.update_log("🟢 Bank System Started - Ready for Transactions")
    
    def setup_gui(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#34495e', height=70)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🏦 Bank Transaction Monitor", 
                              font=('Arial', 18, 'bold'), 
                              fg='white', bg='#34495e')
        title_label.pack(expand=True)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f5f6fa')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Statistics Frame
        self.create_stats_frame(main_container)
        
        # Transactions Frame
        self.create_transactions_frame(main_container)
        
        # Log Frame
        self.create_log_frame(main_container)
    
    def create_stats_frame(self, parent):
        stats_frame = tk.LabelFrame(parent, text="📈 Real-time Statistics", 
                                   font=('Arial', 11, 'bold'),
                                   bg='#f5f6fa', fg='#2c3e50')
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Stats labels
        stats_grid = tk.Frame(stats_frame, bg='#f5f6fa')
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        self.total_label = self.create_stat_label(stats_grid, "Total Transactions:", "0", 0)
        self.approved_label = self.create_stat_label(stats_grid, "Approved:", "0", 1)
        self.declined_label = self.create_stat_label(stats_grid, "Declined:", "0", 2)
        self.fraud_label = self.create_stat_label(stats_grid, "Fraud Detected:", "0", 3)
    
    def create_stat_label(self, parent, text, value, row):
        tk.Label(parent, text=text, bg='#f5f6fa', font=('Arial', 10)).grid(
            row=row, column=0, sticky='w', padx=5, pady=2)
        value_label = tk.Label(parent, text=value, bg='#f5f6fa', 
                              font=('Arial', 10, 'bold'), fg='#e74c3c')
        value_label.grid(row=row, column=1, sticky='w', padx=5, pady=2)
        return value_label
    
    def create_transactions_frame(self, parent):
        trans_frame = tk.LabelFrame(parent, text="💳 Recent Transactions", 
                                   font=('Arial', 11, 'bold'),
                                   bg='#f5f6fa', fg='#2c3e50')
        trans_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview for transactions
        columns = ('Time', 'Transaction ID', 'Card', 'Amount', 'Status')
        self.tree = ttk.Treeview(trans_frame, columns=columns, show='headings', height=8)
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
        
        # Set column widths
        self.tree.column('Time', width=80)
        self.tree.column('Transaction ID', width=120)
        self.tree.column('Card', width=100)
        self.tree.column('Amount', width=80)
        self.tree.column('Status', width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(trans_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_log_frame(self, parent):
        log_frame = tk.LabelFrame(parent, text="📋 System Log", 
                                 font=('Arial', 11, 'bold'),
                                 bg='#f5f6fa', fg='#2c3e50')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=6, font=('Consolas', 9),
                               bg='#2c3e50', fg='#00ff00')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Clear Button
        tk.Button(log_frame, text="Clear Log", 
                 command=self.clear_log, bg='#7f8c8d', fg='white').pack(pady=5)
    
    def start_transaction_monitor(self):
        def monitor():
            self.update_log("🔄 Transaction monitor started - Listening for payments...")
            message_count = 0
            
            while True:
                try:
                    # Check for new messages
                    encrypted_message = self.transaction_manager.message_bus.receive_from_vendor()
                    if encrypted_message:
                        message_count += 1
                        self.update_log(f"📥 Received payment request #{message_count}")
                        self.process_transaction(encrypted_message)
                    
                    # Update statistics every 2 seconds
                    if message_count == 0 or message_count % 5 == 0:
                        self.update_statistics()
                    
                    # Small delay
                    time.sleep(0.5)  # Check every 500ms
                    
                except Exception as e:
                    self.update_log(f"❌ Monitor error: {str(e)}")
                    time.sleep(2)  # Wait longer on error
        
        # Start the monitor in a separate thread
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        self.update_log("✅ Monitor thread started successfully")
    
    def process_transaction(self, encrypted_message):
        try:
            # Process the transaction
            result = self.transaction_manager.process_transaction(encrypted_message)
            
            if result:
                # Update GUI in main thread
                self.root.after(0, lambda: self._update_gui_with_transaction(result))
                self.update_log(f"✅ Processed: {result['card_last4']} - ${result['amount']} - {result['status']}")
            else:
                self.update_log("❌ Failed to process transaction")
                
        except Exception as e:
            self.update_log(f"❌ Transaction processing error: {str(e)}")
    
    def _update_gui_with_transaction(self, result):
        """Update GUI with new transaction (called in main thread)"""
        # Add to transactions table
        self.tree.insert('', 0, values=(
            result['timestamp'][11:19],  # Time only
            result['transaction_id'][:8] + '...',
            f"****{result['card_last4']}",
            f"${result['amount']:.2f}",
            result['status']
        ))
        
        # Keep only last 15 transactions
        if len(self.tree.get_children()) > 15:
            self.tree.delete(self.tree.get_children()[-1])
        
        # Update statistics
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics display"""
        stats = self.transaction_manager.get_statistics()
        self.total_label.config(text=str(stats['total']))
        self.approved_label.config(text=str(stats['approved']))
        self.declined_label.config(text=str(stats['declined']))
        self.fraud_label.config(text=str(stats['fraud']))
    
    def update_log(self, message):
        """Update log display (thread-safe)"""
        def _update():
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
            self.log_text.update()
        
        self.root.after(0, _update)
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
        self.update_log("📋 Log cleared")