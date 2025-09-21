#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error
import getpass

def create_database():
    """Create database and user with proper permissions"""
    print("Setting up database for Billing Software...")

    # Get database credentials
    print("\nPlease enter MySQL root credentials (press Enter for no password):")
    root_user = input("Root username [root]: ") or "root"
    root_password = getpass.getpass("Root password: ")

    # Database configuration
    db_name = "billing_software"
    db_user = "root"
    db_password = "admin"  # You can change this or make it configurable

    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host="localhost",
            user=root_user,
            password=root_password or None
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Create database
            print(f"Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print("✓ Database created")

            # Create user
            print(f"Creating user '{db_user}'...")
            cursor.execute(f"CREATE USER IF NOT EXISTS '{db_user}'@'localhost' IDENTIFIED BY '{db_password}'")
            print("✓ User created")

            # Grant privileges
            print("Granting privileges...")
            cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            print("✓ Privileges granted")

            # Switch to the new database
            cursor.execute(f"USE {db_name}")

            # Create tables
            print("Creating tables...")

            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE NOT NULL,
                    setting_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # Default settings
            default_settings = [
                ("company_name", "Your Company Name"),
                ("company_address", "Your Company Address"),
                ("tax_rate", "0.18"),
                ("currency", "₹"),
                ("receipt_footer", "Thank you for your business!")
            ]

            for key, value in default_settings:
                cursor.execute(
                    "INSERT IGNORE INTO settings (setting_key, setting_value) VALUES (%s, %s)",
                    (key, value)
                )

            # Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    stock_quantity INT DEFAULT 0,
                    barcode VARCHAR(100) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # Customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(20),
                    email VARCHAR(255),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Invoices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    invoice_number VARCHAR(50) UNIQUE NOT NULL,
                    customer_id INT,
                    customer_name VARCHAR(255),
                    date DATE NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL,
                    tax_amount DECIMAL(10, 2) NOT NULL,
                    discount DECIMAL(10, 2) DEFAULT 0,
                    grand_total DECIMAL(10, 2) NOT NULL,
                    payment_method VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
                )
            """)

            # Invoice items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoice_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    invoice_id INT NOT NULL,
                    product_id INT,
                    product_name VARCHAR(255) NOT NULL,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(10, 2) NOT NULL,
                    total_price DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
                )
            """)

            print("✓ Tables created")

            # Create config file for the application
            config_content = f"""# Database configuration
[database]
host = localhost
user = {db_user}
password = {db_password}
database = {db_name}

# Application settings
[application]
company_name = Your Company Name
tax_rate = 0.18
currency = ₹
"""

            # Write config file with UTF-8 encoding to support Unicode
            with open('config.ini', 'w', encoding='utf-8') as f:
                f.write(config_content)

            print("✓ Config file created")

            connection.commit()
            print("\n✅ Database setup completed successfully!")
            print(f"Database: {db_name}")
            print(f"Username: {db_user}")
            print(f"Password: {db_password}")
            print("\nConfig file 'config.ini' has been created with these settings.")

    except Error as e:
        print(f"❌ Error: {e}")
        print("\nPlease check your MySQL root credentials and ensure MySQL server is running.")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_database()