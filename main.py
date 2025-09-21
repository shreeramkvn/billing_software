import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
from ui import MainUI
from database import Database
from security import SecurityManager
import config

class BillingSoftware:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Billing Software")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize security manager
        self.security_manager = SecurityManager()
        
        # Check license
        # if not self.security_manager.check_license():
        #     messagebox.showerror("License Error", "Invalid license or machine. Please contact PhoenixTechSolutions.inc")
        #     self.root.destroy()
        #     return
        
        # Initialize database
        self.db = Database()
        
        # Load company name
        self.company_name = self.db.get_setting('company_name', 'Default Company')
        
        # Initialize UI
        self.ui = MainUI(self.root, self.db, self.company_name)
        
        # Add footer
        self.add_footer()
        
        # Start the application
        self.root.mainloop()
    
    def add_footer(self):
        footer = ttk.Label(
            self.root, 
            text="Powered by PhoenixTechSolutions.inc", 
            font=("Arial", 8), 
            foreground="gray",
            anchor="center"
        )
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

if __name__ == "__main__":
    app = BillingSoftware()