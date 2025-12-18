import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bank.transaction_manager import TransactionManager

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color='#00d9ff', width=200, height=50):
        super().__init__(parent, width=width, height=height, bg='#1a2942', 
                        highlightthickness=0, cursor="hand2")
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = self._adjust_color(bg_color, 1.2)
        self.pressed_color = self._adjust_color(bg_color, 0.8)
        self.text = text
        self.is_hovered = False
        self.is_pressed = False
        
        self.draw_button()
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def _adjust_color(self, color, factor):
        """Lighten or darken a hex color"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def draw_button(self):
        self.delete("all")
        color = self.pressed_color if self.is_pressed else (
                self.hover_color if self.is_hovered else self.bg_color)
        
        # Rounded rectangle
        self.create_rounded_rect(5, 5, self.winfo_reqwidth()-5, 
                                self.winfo_reqheight()-5, 10, fill=color, outline="")
        
        # Shadow effect
        if not self.is_pressed:
            self.create_rounded_rect(7, 7, self.winfo_reqwidth()-3, 
                                    self.winfo_reqheight()-3, 10, fill="", 
                                    outline=self._adjust_color(color, 0.5), width=1)
        
        # Text
        self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2,
                        text=self.text, fill="white", 
                        font=("Segoe UI", 11, "bold"))
    
    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1,
                 x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2,
                 x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2,
                 x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, e):
        self.is_hovered = True
        self.draw_button()
    
    def on_leave(self, e):
        self.is_hovered = False
        self.draw_button()
    
    def on_press(self, e):
        self.is_pressed = True
        self.draw_button()
    
    def on_release(self, e):
        self.is_pressed = False
        self.draw_button()
        if self.is_hovered:
            self.command()


class BankMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏦 Bank Payment Processor")
        self.root.geometry("900x700")
        self.root.configure(bg='#0a1628')
        
        self.transaction_manager = TransactionManager()
        self.setup_styles()
        self.setup_gui()
        self.start_transaction_monitor()
        self.update_log("🟢 Bank System Started - Ready for Transactions")
    
    def setup_styles(self):
        """Setup custom styles for modern look"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Treeview
        style.configure("Custom.Treeview",
                       background="#1a2942",
                       foreground="#00d9ff",
                       fieldbackground="#1a2942",
                       borderwidth=0,
                       font=('Segoe UI', 10))
        style.configure("Custom.Treeview.Heading",
                       background="#0f1d33",
                       foreground="#00d9ff",
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'))
        style.map('Custom.Treeview', background=[('selected', '#00d9ff')])
    
    def setup_gui(self):
        # Header with gradient effect
        header_frame = tk.Frame(self.root, bg='#0a1628', height=100)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title with icon
        title_container = tk.Frame(header_frame, bg='#0a1628')
        title_container.pack(expand=True)
        
        title_label = tk.Label(title_container, text="🏦 BANK PAYMENT PROCESSOR", 
                              font=('Segoe UI', 24, 'bold'), 
                              fg='#00d9ff', bg='#0a1628')
        title_label.pack()
        
        subtitle_label = tk.Label(title_container, text="Real-time Transaction Monitoring System", 
                                 font=('Segoe UI', 11), 
                                 fg='#6c7a8f', bg='#0a1628')
        subtitle_label.pack(pady=(5, 0))
        
        # Main container
        main_container = tk.Frame(self.root, bg='#0a1628')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Statistics Frame
        self.create_stats_frame(main_container)
        
        # Transactions Frame
        self.create_transactions_frame(main_container)
        
        # Log Frame
        self.create_log_frame(main_container)
    
    def create_stats_frame(self, parent):
        stats_frame = tk.Frame(parent, bg='#0a1628')
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create 4 stat cards
        stats = [
            ("Total Transactions", "0", "#00d9ff"),
            ("Approved", "0", "#00ff88"),
            ("Declined", "0", "#ff6b6b"),
            ("Fraud Detected", "0", "#ffd93d")
        ]
        
        for i, (label, value, color) in enumerate(stats):
            self.create_stat_card(stats_frame, label, value, color, i)
    
    def create_stat_card(self, parent, label_text, value, color, index):
        card = tk.Frame(parent, bg='#1a2942', highlightbackground='#2d3e5f', 
                       highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Icon/Value
        value_label = tk.Label(card, text=value, font=('Segoe UI', 28, 'bold'),
                              fg=color, bg='#1a2942')
        value_label.pack(pady=(15, 5))
        
        # Label
        text_label = tk.Label(card, text=label_text, font=('Segoe UI', 10),
                             fg='#8a9ab0', bg='#1a2942')
        text_label.pack(pady=(0, 15))
        
        # Store reference based on index
        if index == 0:
            self.total_label = value_label
        elif index == 1:
            self.approved_label = value_label
        elif index == 2:
            self.declined_label = value_label
        elif index == 3:
            self.fraud_label = value_label
    
    def create_transactions_frame(self, parent):
        trans_frame = tk.Frame(parent, bg='#1a2942', highlightbackground='#2d3e5f',
                              highlightthickness=1)
        trans_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Header
        header = tk.Frame(trans_frame, bg='#1a2942')
        header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(header, text="💳 Recent Transactions", 
                font=('Segoe UI', 13, 'bold'),
                fg='#00d9ff', bg='#1a2942').pack(side=tk.LEFT)
        
        # Treeview for transactions
        tree_container = tk.Frame(trans_frame, bg='#1a2942')
        tree_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        columns = ('Time', 'Transaction ID', 'Card', 'Amount', 'Status')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', 
                                height=10, style="Custom.Treeview")
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
        
        # Set column widths
        self.tree.column('Time', width=100)
        self.tree.column('Transaction ID', width=150)
        self.tree.column('Card', width=120)
        self.tree.column('Amount', width=100)
        self.tree.column('Status', width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_log_frame(self, parent):
        log_frame = tk.Frame(parent, bg='#1a2942', highlightbackground='#2d3e5f',
                            highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(log_frame, bg='#1a2942')
        header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(header, text="📋 System Log", 
                font=('Segoe UI', 13, 'bold'),
                fg='#00d9ff', bg='#1a2942').pack(side=tk.LEFT)
        
        # Modern Clear button
        clear_btn = ModernButton(header, "🗑️ Clear Log", self.clear_log, 
                                bg_color="#ff0051", width=150, height=40)
        clear_btn.pack(side=tk.RIGHT)
        
        # Log text
        self.log_text = tk.Text(log_frame, height=6, font=('Consolas', 9),
                               bg='#0f1d33', fg='#00ff88',
                               insertbackground='#00d9ff',
                               selectbackground='#2d3e5f',
                               bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
    
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


if __name__ == "__main__":
    root = tk.Tk()
    app = BankMonitorGUI(root)
    root.mainloop()