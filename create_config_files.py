import json
import uuid

def create_config_files():
    print("=== Billing Software Setup ===")
    print("Please provide the following information:")
    
    # Get user input
    company_name = input("Enter your company name: ")
    db_host = input("Database host [localhost]: ") or "localhost"
    db_name = input("Database name [billing_software]: ") or "billing_software"
    db_user = input("Database user [root]: ") or "root"
    db_password = input("Database password: ")
    
    # Create config.json
    config = {
        "DB_HOST": db_host,
        "DB_NAME": db_name,
        "DB_USER": db_user,
        "DB_PASSWORD": db_password,
        "COMPANY_NAME": company_name,
        "ALLOW_NEGATIVE_STOCK": True,
        "THERMAL_PRINTER_WIDTH": 80,
        "COMPANY_ADDRESS": input("Company address: "),
        "COMPANY_GST": input("Company GST number: "),
        "COMPANY_PHONE": input("Company phone number: ")
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    # Create license.key
    license_data = {
        "company_name": company_name,
        "license_key": f"LIC_{uuid.uuid4().hex[:16].upper()}",
        "machine_id": f"MACH_{uuid.uuid4().hex[:12].upper()}",
        "expiry_date": "2025-12-31",
        "version": "1.0"
    }
    
    with open('license.key', 'w') as f:
        json.dump(license_data, f, indent=4)
    
    print("\nConfiguration files created successfully!")
    print("Please make sure your MySQL database is set up with the provided credentials.")
    print("You can now run the application.")

if __name__ == "__main__":
    create_config_files()