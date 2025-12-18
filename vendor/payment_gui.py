import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vendor.payment_processor import PaymentProcessor

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


class ModernEntry(tk.Canvas):
    def __init__(self, parent, placeholder="", width=300, height=45, show='', state='normal'):
        super().__init__(parent, width=width, height=height, bg='#1a2942', 
                        highlightthickness=0)
        
        self.width = width
        self.height = height
        self.show = show
        self.placeholder = placeholder
        self.is_disabled = state == 'disabled'
        
        # Create rounded rectangle background
        fill_color = '#0a1628' if self.is_disabled else '#0f1d33'
        text_color = '#6c7a8f' if self.is_disabled else '#00d9ff'
        
        self.create_rounded_rect(2, 2, width-2, height-2, 8, 
                               fill=fill_color, outline='#2d3e5f', width=2)
        
        # Create entry widget
        self.entry = tk.Entry(self, font=('Segoe UI', 11),
                             bg=fill_color, fg=text_color,
                             insertbackground='#00d9ff',
                             bd=0, show=show,
                             relief=tk.FLAT,
                             state=state,
                             disabledbackground=fill_color,    # Fix white overlay
                             disabledforeground=text_color,    # Fix white overlay
                             readonlybackground=fill_color)    # Alternative fix
        
        # Position entry inside canvas
        self.create_window(width//2, height//2, window=self.entry, width=width-20)
        
        # Bind focus events for border highlight
        self.entry.bind('<FocusIn>', self.on_focus_in)
        self.entry.bind('<FocusOut>', self.on_focus_out)
    
    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1,
                 x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2,
                 x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2,
                 x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        self.rect = self.create_polygon(points, smooth=True, **kwargs)
        return self.rect
    
    def on_focus_in(self, e):
        if not self.is_disabled:
            self.itemconfig(self.rect, outline='#00d9ff', width=2)
    
    def on_focus_out(self, e):
        if not self.is_disabled:
            self.itemconfig(self.rect, outline='#2d3e5f', width=2)
    
    def get(self):
        return self.entry.get()
    
    def delete(self, start, end):
        if not self.is_disabled:
            self.entry.delete(start, end)
    
    def insert(self, index, string):
        if not self.is_disabled:
            self.entry.insert(index, string)
    
    def config(self, **kwargs):
        if 'state' in kwargs:
            self.is_disabled = kwargs['state'] == 'disabled'
            self.entry.config(state=kwargs['state'])
            fill_color = '#0a1628' if self.is_disabled else '#0f1d33'
            text_color = '#6c7a8f' if self.is_disabled else '#00d9ff'
            
            # Update entry colors
            self.entry.config(
                bg=fill_color,
                fg=text_color,
                disabledbackground=fill_color,    # Fix white overlay
                disabledforeground=text_color,    # Fix white overlay
                readonlybackground=fill_color     # Alternative fix
            )
            
            # Update canvas rectangle
            self.itemconfig(self.rect, fill=fill_color)


class VendorPaymentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏪 Vendor Payment System")
        self.root.geometry("700x850")
        self.root.configure(bg='#0a1628')
        
        self.processor = PaymentProcessor()
        self.current_token = None  # Track if using a tokenized card
        self.current_real_card_number = None  # Store real card number when using token
        self.current_expiry = None  # Store expiry when using token
        
        self.setup_gui()
        self.start_status_monitor()
    
    def setup_gui(self):
        # Main container with padding
        main_container = tk.Frame(self.root, bg='#0a1628')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header - Reduced height
        header_frame = tk.Frame(main_container, bg='#0a1628', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Title with icon
        title_container = tk.Frame(header_frame, bg='#0a1628')
        title_container.pack(expand=True)
        
        title_label = tk.Label(title_container, text="💳 SECURE PAYMENT GATEWAY", 
                              font=('Segoe UI', 22, 'bold'), 
                              fg='#00d9ff', bg='#0a1628')
        title_label.pack()
        
        subtitle_label = tk.Label(title_container, text="Encrypted Vendor Payment Processing", 
                                 font=('Segoe UI', 10), 
                                 fg='#6c7a8f', bg='#0a1628')
        subtitle_label.pack(pady=(2, 0))
        
        # Create a container for the three main sections
        sections_container = tk.Frame(main_container, bg='#0a1628')
        sections_container.pack(fill=tk.BOTH, expand=True)
        
        # Payment Form Section - Reduced height
        self.create_payment_form(sections_container)
        
        # Token Section - Reduced height
        self.create_token_section(sections_container)
        
        # Status Section - Increased height
        self.create_status_section(sections_container)
    
    def create_payment_form(self, parent):
        form_frame = tk.Frame(parent, bg='#1a2942', highlightbackground='#2d3e5f',
                             highlightthickness=1)
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Header with less padding
        header = tk.Frame(form_frame, bg='#1a2942')
        header.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(header, text="🛒 New Payment Transaction", 
                font=('Segoe UI', 12, 'bold'),
                fg='#00d9ff', bg='#1a2942').pack(anchor='w')
        
        # Form fields container with reduced padding
        fields_frame = tk.Frame(form_frame, bg='#1a2942')
        fields_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Card Number
        tk.Label(fields_frame, text="Card Number", 
                font=('Segoe UI', 10), fg='#8a9ab0', bg='#1a2942').pack(anchor='w', pady=(0, 5))
        self.card_entry = ModernEntry(fields_frame, width=500, height=45)
        self.card_entry.pack(fill=tk.X, pady=(0, 12))
        
        # Expiry and CVV row - Aligned properly
        row_frame = tk.Frame(fields_frame, bg='#1a2942')
        row_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Expiry
        expiry_frame = tk.Frame(row_frame, bg='#1a2942')
        expiry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(expiry_frame, text="Expiry (MM/YY)", 
                font=('Segoe UI', 10), fg='#8a9ab0', bg='#1a2942').pack(anchor='w', pady=(0, 5))
        self.expiry_entry = ModernEntry(expiry_frame, width=220, height=45)
        self.expiry_entry.pack(anchor='w')
        
        # CVV - Aligned to the right
        cvv_frame = tk.Frame(row_frame, bg='#1a2942')
        cvv_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(cvv_frame, text="CVV", 
                font=('Segoe UI', 10), fg='#8a9ab0', bg='#1a2942').pack(anchor='w', pady=(0, 5))
        self.cvv_entry = ModernEntry(cvv_frame, width=220, height=45, show='*')
        self.cvv_entry.pack(anchor='w')
        
        # Amount
        amount_frame = tk.Frame(fields_frame, bg='#1a2942')
        amount_frame.pack(fill=tk.X, pady=(0, 12))
        tk.Label(amount_frame, text="Amount ($)", 
                font=('Segoe UI', 10), fg='#8a9ab0', bg='#1a2942').pack(anchor='w', pady=(0, 5))
        self.amount_entry = ModernEntry(amount_frame, width=250, height=45)
        self.amount_entry.pack(anchor='w')
        
        # Save Token Checkbox
        checkbox_frame = tk.Frame(fields_frame, bg='#1a2942')
        checkbox_frame.pack(fill=tk.X, pady=(8, 0))
        
        self.save_token_var = tk.BooleanVar(value=True)
        self.save_checkbox = tk.Checkbutton(checkbox_frame, 
                              text="Save card for future payments", 
                              variable=self.save_token_var,
                              bg='#1a2942', fg='#8a9ab0',
                              activebackground='#1a2942',
                              activeforeground='#00d9ff',
                              selectcolor='#0f1d33',
                              font=('Segoe UI', 10))
        self.save_checkbox.pack(anchor='w')
        
        # Submit and New Payment Buttons
        button_frame = tk.Frame(form_frame, bg='#1a2942')
        button_frame.pack(fill=tk.X, padx=20, pady=(10, 15))
        
        self.submit_btn = ModernButton(button_frame, "🚀 Process Payment", 
                                      self.process_payment, bg_color="#3fe363", 
                                      width=250, height=50)
        self.submit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.new_payment_btn = ModernButton(button_frame, "🆕 New Payment", 
                                           self.reset_form_for_new_payment, 
                                           bg_color='#00d9ff', width=200, height=50)
        self.new_payment_btn.pack(side=tk.LEFT)
    
    def create_token_section(self, parent):
        token_frame = tk.Frame(parent, bg='#1a2942', highlightbackground='#2d3e5f',
                              highlightthickness=1)
        token_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Header with less padding
        header = tk.Frame(token_frame, bg='#1a2942')
        header.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(header, text="💾 Saved Cards (Tokenized)", 
                font=('Segoe UI', 12, 'bold'),
                fg='#00d9ff', bg='#1a2942').pack(anchor='w')
        
        # Token Listbox with custom style
        listbox_frame = tk.Frame(token_frame, bg='#0f1d33', 
                                highlightbackground='#2d3e5f', highlightthickness=2)
        listbox_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Smaller listbox height
        self.token_listbox = tk.Listbox(listbox_frame, height=3, 
                                       font=('Consolas', 10),
                                       bg='#0f1d33', fg='#00d9ff',
                                       selectbackground='#2d3e5f',
                                       selectforeground='#00d9ff',
                                       bd=0,
                                       highlightthickness=0)
        self.token_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        # Token Buttons
        btn_frame = tk.Frame(token_frame, bg='#1a2942')
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        buttons = [
            ("Use Selected Card", self.use_saved_card, '#00d9ff', 150),
            ("Refresh List", self.load_tokens, '#6c7a8f', 130),
            ("Delete Selected", self.delete_token, '#ff6b6b', 140)
        ]
        
        for text, command, color, width in buttons:
            btn = ModernButton(btn_frame, text, command, bg_color=color, 
                             width=width, height=38)
            btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.load_tokens()
    
    def create_status_section(self, parent):
        status_frame = tk.Frame(parent, bg='#1a2942', highlightbackground='#2d3e5f',
                               highlightthickness=1)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        # Header
        header = tk.Frame(status_frame, bg='#1a2942')
        header.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(header, text="📊 System Status & Activity Log", 
                font=('Segoe UI', 12, 'bold'),
                fg='#00d9ff', bg='#1a2942').pack(side=tk.LEFT)
        
        # Clear button
        clear_btn = ModernButton(header, "🗑️ Clear Log", self.clear_status,
                               bg_color='#ff0051', width=150, height=40)
        clear_btn.pack(side=tk.RIGHT)
        
        # Status Text - Increased height
        self.status_text = tk.Text(status_frame, height=12, 
                                  font=('Consolas', 9),
                                  bg='#0f1d33', fg='#00ff88',
                                  insertbackground='#00d9ff',
                                  selectbackground='#2d3e5f',
                                  bd=0)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
    
    def process_payment(self):
        # Get form data
        card_data = {
            'number': '',
            'expiry': '',
            'cvv': self.cvv_entry.get().strip(),
            'amount': self.amount_entry.get().strip(),
            'save_token': self.save_token_var.get() if not self.current_token else False
        }
        
        # Check if using token or manual entry
        if self.current_token:
            # Using token - use stored real card data
            card_data['number'] = self.current_real_card_number
            card_data['expiry'] = self.current_expiry
        else:
            # Manual entry - get from form fields
            card_data['number'] = self.card_entry.get().strip()
            card_data['expiry'] = self.expiry_entry.get().strip()
        
        # Validate input
        if not all([card_data['cvv'], card_data['amount']]):
            messagebox.showerror("Error", "Please enter CVV and amount!")
            return
        
        if not self.current_token and not card_data['number']:
            messagebox.showerror("Error", "Please enter card number or use saved card!")
            return
        
        if not self.current_token and not card_data['expiry']:
            messagebox.showerror("Error", "Please enter expiry date!")
            return
        
        # Process in background
        threading.Thread(target=self._process_payment_thread, 
                        args=(card_data, self.current_token,), daemon=True).start()
        
        # Reset form after processing
        self.root.after(1000, self.reset_form_for_new_payment)
    
    def _process_payment_thread(self, card_data, token=None):
        try:
            result = self.processor.process_payment(card_data, token)
            self.update_status(f"📱 {result}")
        except Exception as e:
            self.update_status(f"❌ Payment Failed: {str(e)}")
    
    def use_saved_card(self):
        selection = self.token_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a saved card!")
            return
        
        # Get token from selection
        selected_text = self.token_listbox.get(selection[0])
        token = selected_text.split(' - ')[0]
        
        try:
            # Get partial card data (NO CVV!)
            card_data = self.processor.get_card_from_token(token)
            
            # Show security information
            info_message = (
                "🔒 SECURE TOKEN PAYMENT\n\n"
                f"Card: {card_data['masked']}\n"
                f"Expiry: {card_data['expiry']}\n\n"
                "⚠️  SECURITY FEATURES:\n"
                "• CVV NOT stored with token\n"
                "• Must enter CVV fresh each time\n"
                "• Amount must be entered fresh\n"
                "• Rate limiting protects against guessing\n\n"
                "Please enter CVV and amount to continue."
            )
            messagebox.showinfo("Using Saved Card", info_message)
            
            # Clear all fields first
            self.card_entry.delete(0, tk.END)
            self.expiry_entry.delete(0, tk.END)
            self.cvv_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            
            # Fill only safe fields
            self.card_entry.insert(0, card_data['masked'])  # Masked number only
            self.expiry_entry.insert(0, card_data['expiry'])  # Expiry is safe
            
            # CVV and Amount remain EMPTY - user must enter fresh!
            
            # Store token AND real card data for processing
            self.current_token = token
            self.current_real_card_number = card_data['number']  # Store REAL card number!
            self.current_expiry = card_data['expiry']  # Store expiry
            
            # Disable editing of card and expiry fields when using token
            self.card_entry.config(state='disabled')
            self.expiry_entry.config(state='disabled')
            
            # Disable save token checkbox when using token
            self.save_checkbox.config(state='disabled')
            self.save_token_var.set(False)
            
            # Focus on CVV field for user convenience
            self.cvv_entry.focus_set()
            
            self.update_status(f"🔐 Token loaded: {card_data['masked']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load card: {str(e)}")
    
    def reset_form_for_new_payment(self):
        """Reset form for a new payment"""
        # Re-enable all fields
        self.card_entry.config(state='normal')
        self.expiry_entry.config(state='normal')
        
        # Re-enable save token checkbox
        self.save_checkbox.config(state='normal')
        self.save_token_var.set(True)
        
        # Clear all fields
        self.card_entry.delete(0, tk.END)
        self.expiry_entry.delete(0, tk.END)
        self.cvv_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        
        # Reset token and stored card data
        self.current_token = None
        self.current_real_card_number = None
        self.current_expiry = None
        
        # Update status
        self.update_status("🆕 Ready for new payment")
    
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


if __name__ == "__main__":
    root = tk.Tk()
    app = VendorPaymentGUI(root)
    root.mainloop()