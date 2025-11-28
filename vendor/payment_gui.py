import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vendor.payment_processor import PaymentProcessor

class VendorPaymentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏪 Vendor Payment System")
        self.root.geometry("600x700")
        self.root.configure(bg='#f0f8ff')
        
        self.processor = PaymentProcessor()
        self.setup_gui()
        self.start_status_monitor()
    
    def setup_gui(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="💳 Secure Payment Gateway", 
                              font=('Arial', 20, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f8ff')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Payment Form
        self.create_payment_form(main_container)
        
        # Token Section
        self.create_token_section(main_container)
        
        # Status Section
        self.create_status_section(main_container)
    
    def create_payment_form(self, parent):
        form_frame = tk.LabelFrame(parent, text="🛒 New Payment", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#f0f8ff', fg='#2c3e50')
        form_frame.pack(fill=tk.X, pady=10)
        
        # Card Number
        tk.Label(form_frame, text="Card Number:", bg='#f0f8ff', 
                font=('Arial', 10)).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.card_entry = tk.Entry(form_frame, font=('Arial', 11), width=25)
        self.card_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Expiry Date
        tk.Label(form_frame, text="Expiry (MM/YY):", bg='#f0f8ff',
                font=('Arial', 10)).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.expiry_entry = tk.Entry(form_frame, font=('Arial', 11), width=15)
        self.expiry_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        
        # CVV
        tk.Label(form_frame, text="CVV:", bg='#f0f8ff',
                font=('Arial', 10)).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.cvv_entry = tk.Entry(form_frame, font=('Arial', 11), width=10, show='*')
        self.cvv_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        
        # Amount
        tk.Label(form_frame, text="Amount ($):", bg='#f0f8ff',
                font=('Arial', 10)).grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.amount_entry = tk.Entry(form_frame, font=('Arial', 11), width=15)
        self.amount_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')
        
        # Save Token Checkbox
        self.save_token_var = tk.BooleanVar(value=True)
        tk.Checkbutton(form_frame, text="Save card for future payments", 
                      variable=self.save_token_var, bg='#f0f8ff',
                      font=('Arial', 10)).grid(row=4, column=0, columnspan=2, 
                                             sticky='w', padx=10, pady=10)
        
        # Submit Button
        submit_btn = tk.Button(form_frame, text="🚀 Process Payment", 
                              command=self.process_payment,
                              font=('Arial', 12, 'bold'), 
                              bg='#27ae60', fg='white',
                              width=20, height=2)
        submit_btn.grid(row=5, column=0, columnspan=2, pady=15)
    
    def create_token_section(self, parent):
        token_frame = tk.LabelFrame(parent, text="💾 Saved Cards", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#f0f8ff', fg='#2c3e50')
        token_frame.pack(fill=tk.X, pady=10)
        
        # Token Listbox
        self.token_listbox = tk.Listbox(token_frame, height=4, font=('Arial', 10))
        self.token_listbox.pack(fill=tk.X, padx=10, pady=10)
        
        # Token Buttons
        btn_frame = tk.Frame(token_frame, bg='#f0f8ff')
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="Use Selected Card", 
                 command=self.use_saved_card, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh List", 
                 command=self.load_tokens, bg='#95a5a6', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Selected", 
                 command=self.delete_token, bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=5)
        
        self.load_tokens()
    
    def create_status_section(self, parent):
        status_frame = tk.LabelFrame(parent, text="📊 System Status", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#f0f8ff', fg='#2c3e50')
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Status Text
        self.status_text = tk.Text(status_frame, height=8, font=('Consolas', 9),
                                 bg='#2c3e50', fg='#00ff00')
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Clear Button
        tk.Button(status_frame, text="Clear Log", 
                 command=self.clear_status, bg='#7f8c8d', fg='white').pack(pady=5)
    
    def process_payment(self):
        # Get form data
        card_data = {
            'number': self.card_entry.get().strip(),
            'expiry': self.expiry_entry.get().strip(),
            'cvv': self.cvv_entry.get().strip(),
            'amount': self.amount_entry.get().strip(),
            'save_token': self.save_token_var.get()
        }
        
        # Validate input
        if not all(card_data.values()):
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        # Process in background
        threading.Thread(target=self._process_payment_thread, 
                        args=(card_data,), daemon=True).start()
    
    def _process_payment_thread(self, card_data):
        try:
            result = self.processor.process_payment(card_data)
            self.update_status(f"✅ Payment Result: {result}")
        except Exception as e:
            self.update_status(f"❌ Payment Failed: {str(e)}")
    
    def use_saved_card(self):
        selection = self.token_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a saved card!")
            return
        
        token = self.token_listbox.get(selection[0]).split(' - ')[0]
        try:
            card_data = self.processor.get_card_from_token(token)
            self.card_entry.delete(0, tk.END)
            self.card_entry.insert(0, f"**** **** **** {card_data['number'][-4:]}")
            self.update_status(f"🔐 Using tokenized card: {token}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load card: {str(e)}")
    
    def load_tokens(self):
        self.token_listbox.delete(0, tk.END)
        tokens = self.processor.get_all_tokens()
        for token, masked_card in tokens.items():
            self.token_listbox.insert(tk.END, f"{token} - {masked_card}")
    
    def delete_token(self):
        selection = self.token_listbox.curselection()
        if not selection:
            return
        
        token = self.token_listbox.get(selection[0]).split(' - ')[0]
        self.processor.delete_token(token)
        self.load_tokens()
        self.update_status(f"🗑️ Deleted token: {token}")
    
    def update_status(self, message):
        def _update():
            self.status_text.insert(tk.END, f"{message}\n")
            self.status_text.see(tk.END)
        self.root.after(0, _update)
    
    def clear_status(self):
        self.status_text.delete(1.0, tk.END)
    
    def start_status_monitor(self):
        def monitor():
            while True:
                status = self.processor.get_system_status()
                self.update_status(f"🔄 {status}")
                threading.Event().wait(5)  # Update every 5 seconds
        
        threading.Thread(target=monitor, daemon=True).start()