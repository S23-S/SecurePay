import tkinter as tk
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import the modules
from bank.bank_gui import BankMonitorGUI

def main():
    # Create necessary directories
    os.makedirs("bank/data", exist_ok=True)
    os.makedirs("shared", exist_ok=True)
    
    print("🏦 Starting SecurePay Bank System...")
    print("📁 Working directory:", os.getcwd())
    
    root = tk.Tk()
    app = BankMonitorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()