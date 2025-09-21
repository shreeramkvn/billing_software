import hashlib
import uuid
import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox

class SecurityManager:
    def __init__(self):
        self.machine_id = self.get_machine_id()
        self.license_file = "license.key"
    
    def get_machine_id(self):
        # Get machine-specific identifier
        return str(uuid.getnode())
    
    def generate_license_key(self, company_name):
        # This would be used by the software vendor to generate licenses
        data = f"{company_name}_{self.machine_id}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def check_license(self):
        # Check if license file exists and is valid
        if not os.path.exists(self.license_file):
            # If no license file exists, run setup
            return self.run_setup()
        
        try:
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
            
            expected_key = hashlib.sha256(
                f"{license_data['company_name']}_{self.machine_id}".encode()
            ).hexdigest()
            
            return license_data['license_key'] == expected_key
        except:
            return self.run_setup()
    
    def run_setup(self):
        """Run initial setup to create a license"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Ask for company name
        company_name = simpledialog.askstring(
            "Setup", 
            "Enter your company name:",
            parent=root
        )
        
        if not company_name:
            messagebox.showerror("Error", "Company name is required")
            return False
        
        # Create license
        license_key = self.generate_license_key(company_name)
        license_data = {
            'company_name': company_name,
            'license_key': license_key,
            'machine_id': self.machine_id
        }
        
        with open(self.license_file, 'w') as f:
            json.dump(license_data, f)
        
        messagebox.showinfo("Success", f"License created for {company_name}")
        return True
    
    def create_license(self, company_name):
        # Create a new license file (should be done by vendor)
        license_key = self.generate_license_key(company_name)
        license_data = {
            'company_name': company_name,
            'license_key': license_key
        }
        
        with open(self.license_file, 'w') as f:
            json.dump(license_data, f)
        
        return True


# import hashlib
# import uuid
# import os
# import json
# from database import Database

# class SecurityManager:
#     def __init__(self):
#         self.machine_id = self.get_machine_id()
#         self.license_file = "license.key"
    
#     def get_machine_id(self):
#         # Get machine-specific identifier
#         return str(uuid.getnode())
    
#     def generate_license_key(self, company_name):
#         # This would be used by the software vendor to generate licenses
#         data = f"{company_name}_{self.machine_id}"
#         return hashlib.sha256(data.encode()).hexdigest()
    
#     def check_license(self):
#         # Check if license file exists and is valid
#         if not os.path.exists(self.license_file):
#             return False
        
#         try:
#             with open(self.license_file, 'r') as f:
#                 license_data = json.load(f)
            
#             expected_key = hashlib.sha256(
#                 f"{license_data['company_name']}_{self.machine_id}".encode()
#             ).hexdigest()
            
#             return license_data['license_key'] == expected_key
#         except:
#             return False
    
#     def create_license(self, company_name):
#         # Create a new license file (should be done by vendor)
#         license_key = self.generate_license_key(company_name)
#         license_data = {
#             'company_name': company_name,
#             'license_key': license_key
#         }
        
#         with open(self.license_file, 'w') as f:
#             json.dump(license_data, f)
        
#         return True