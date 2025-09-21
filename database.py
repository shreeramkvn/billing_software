import mysql.connector
from mysql.connector import Error
import configparser
import os
import sys

class Database:
    def __init__(self):
        self.connection = None
        self.config = configparser.ConfigParser()
        
        # Try to load config from different possible locations
        config_files = ['config.ini', 'config/config.ini', '../config.ini']
        
        for config_file in config_files:
            if os.path.exists(config_file):
                self.config.read(config_file)
                break
        else:
            # If no config file found, use defaults
            self.config['database'] = {
                'host': 'localhost',
                'user': 'billing_user',
                'password': 'billing_password',
                'database': 'billing_software'
            }
        
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config['database'].get('host', 'localhost'),
                user=self.config['database'].get('user', 'billing_user'),
                password=self.config['database'].get('password', 'billing_password'),
                database=self.config['database'].get('database', 'billing_software'),
                autocommit=True
            )
            
            if self.connection.is_connected():
                print("Connected to MySQL database")
                return True
                
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            self.connection = None
            return False
    
    def is_connected(self):
        """Check if database is connected"""
        if self.connection and self.connection.is_connected():
            return True
        return False
    
    def reconnect(self):
        """Reconnect to database"""
        self.close()
        return self.connect()
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query that doesn't return results"""
        if not self.is_connected() and not self.reconnect():
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            return True
        except Error as e:
            print(f"Error executing query: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def fetch_one(self, query, params=None):
        """Fetch a single row"""
        if not self.is_connected() and not self.reconnect():
            return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching data: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def fetch_all(self, query, params=None):
        """Fetch all rows"""
        if not self.is_connected() and not self.reconnect():
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching data: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def get_setting(self, key, default=None):
        """Get a setting from the settings table"""
        result = self.fetch_one("SELECT setting_value FROM settings WHERE setting_key = %s", (key,))
        return result[0] if result else default
    
    def set_setting(self, key, value):
        """Set a setting in the settings table"""
        query = """
            INSERT INTO settings (setting_key, setting_value) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE setting_value = %s
        """
        return self.execute_query(query, (key, value, value))

# Singleton instance
db_instance = None

def get_db():
    """Get database instance (singleton)"""
    global db_instance
    if db_instance is None:
        db_instance = Database()
    return db_instance

# Test function
def test_connection():
    """Test database connection"""
    db = get_db()
    if db.is_connected():
        print("Database connection test: ✓ SUCCESS")
        # Test a simple query
        result = db.fetch_one("SELECT 1")
        if result:
            print("Query test: ✓ SUCCESS")
        else:
            print("Query test: ✗ FAILED")
    else:
        print("Database connection test: ✗ FAILED")
    
    return db.is_connected()

if __name__ == "__main__":
    test_connection()

# import mysql.connector
# from mysql.connector import Error
# from datetime import datetime
# import json
# import os

# class Database:
#     def __init__(self):
#         self.connection = None
#         self.config = self.load_config()
#         self.connect()
    
#     def load_config(self):
#         """Load configuration from config.json"""
#         default_config = {
#             'DB_HOST': 'localhost',
#             'DB_NAME': 'billing_software',
#             'DB_USER': 'root',
#             'DB_PASSWORD': '',
#             'COMPANY_NAME': 'Default Company'
#         }
        
#         if os.path.exists('config.json'):
#             try:
#                 with open('config.json', 'r') as f:
#                     config_data = json.load(f)
#                     return {**default_config, **config_data}
#             except Exception as e:
#                 print(f"Error loading config: {e}")
#                 return default_config
#         else:
#             return default_config
    
#     def connect(self):
#         try:
#             self.connection = mysql.connector.connect(
#                 host=self.config['DB_HOST'],
#                 database=self.config['DB_NAME'],
#                 user=self.config['DB_USER'],
#                 password=self.config['DB_PASSWORD']
#             )
#             if self.connection.is_connected():
#                 print("Connected to MySQL database")
#         except Error as e:
#             print(f"Error while connecting to MySQL: {e}")
    
#     def execute_query(self, query, params=None):
#         try:
#             cursor = self.connection.cursor()
#             cursor.execute(query, params or ())
#             self.connection.commit()
#             return cursor
#         except Error as e:
#             print(f"Error executing query: {e}")
#             return None
    
#     def fetch_all(self, query, params=None):
#         try:
#             cursor = self.connection.cursor(dictionary=True)
#             cursor.execute(query, params or ())
#             return cursor.fetchall()
#         except Error as e:
#             print(f"Error fetching data: {e}")
#             return []
    
#     def fetch_one(self, query, params=None):
#         try:
#             cursor = self.connection.cursor(dictionary=True)
#             cursor.execute(query, params or ())
#             return cursor.fetchone()
#         except Error as e:
#             print(f"Error fetching data: {e}")
#             return None
    
#     def add_product(self, name, description, hsn_code, rate, barcode=None):
#         query = """
#             INSERT INTO products (name, description, hsn_code, rate, barcode)
#             VALUES (%s, %s, %s, %s, %s)
#         """
#         return self.execute_query(query, (name, description, hsn_code, rate, barcode))
    
#     def get_products(self):
#         return self.fetch_all("SELECT * FROM products ORDER BY name")
    
#     def get_product_by_barcode(self, barcode):
#         return self.fetch_one("SELECT * FROM products WHERE barcode = %s", (barcode,))
    
#     def update_stock(self, product_id, quantity, movement_type, reference_id=None):
#         # Update product stock
#         sign = 1 if movement_type == 'IN' else -1
#         query = "UPDATE products SET current_stock = current_stock + (%s * %s) WHERE id = %s"
#         self.execute_query(query, (quantity, sign, product_id))
        
#         # Record stock movement
#         query = """
#             INSERT INTO stock_movements (product_id, quantity, movement_type, reference_id)
#             VALUES (%s, %s, %s, %s)
#         """
#         return self.execute_query(query, (product_id, quantity, movement_type, reference_id))
    
#     def add_client(self, name, address, phone, gst_number=None, client_type='B2C'):
#         query = """
#             INSERT INTO clients (name, address, phone, gst_number, client_type)
#             VALUES (%s, %s, %s, %s, %s)
#         """
#         return self.execute_query(query, (name, address, phone, gst_number, client_type))
    
#     def get_clients(self, client_type=None):
#         if client_type:
#             return self.fetch_all("SELECT * FROM clients WHERE client_type = %s ORDER BY name", (client_type,))
#         return self.fetch_all("SELECT * FROM clients ORDER BY name")
    
#     def create_invoice(self, invoice_number, client_id, invoice_date, invoice_type, items):
#         # Calculate total amount
#         total_amount = sum(item['quantity'] * item['rate'] for item in items)
        
#         # Insert invoice
#         query = """
#             INSERT INTO invoices (invoice_number, client_id, date, type, total_amount)
#             VALUES (%s, %s, %s, %s, %s)
#         """
#         cursor = self.execute_query(query, (invoice_number, client_id, invoice_date, invoice_type, total_amount))
#         invoice_id = cursor.lastrowid if cursor else None
        
#         if invoice_id:
#             # Insert invoice items
#             for item in items:
#                 query = """
#                     INSERT INTO invoice_items (invoice_id, product_id, description, hsn_code, quantity, rate, amount)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s)
#                 """
#                 self.execute_query(query, (
#                     invoice_id, 
#                     item.get('product_id'), 
#                     item.get('description'), 
#                     item.get('hsn_code'), 
#                     item['quantity'], 
#                     item['rate'], 
#                     item['quantity'] * item['rate']
#                 ))
                
#                 # Update stock if it's a sale or purchase
#                 if invoice_type == 'SALE':
#                     self.update_stock(item['product_id'], item['quantity'], 'OUT', invoice_id)
#                 elif invoice_type == 'PURCHASE':
#                     self.update_stock(item['product_id'], item['quantity'], 'IN', invoice_id)
            
#             # Update client's last bill date
#             self.execute_query(
#                 "UPDATE clients SET last_bill_date = %s WHERE id = %s", 
#                 (invoice_date, client_id)
#             )
        
#         return invoice_id
    
#     def get_invoices(self, start_date=None, end_date=None, invoice_type=None):
#         query = "SELECT i.*, c.name as client_name FROM invoices i LEFT JOIN clients c ON i.client_id = c.id WHERE 1=1"
#         params = []
        
#         if start_date:
#             query += " AND i.date >= %s"
#             params.append(start_date)
        
#         if end_date:
#             query += " AND i.date <= %s"
#             params.append(end_date)
        
#         if invoice_type:
#             query += " AND i.type = %s"
#             params.append(invoice_type)
        
#         query += " ORDER BY i.date DESC"
#         return self.fetch_all(query, params)
    
#     def get_invoice_items(self, invoice_id):
#         return self.fetch_all("""
#             SELECT ii.*, p.name as product_name 
#             FROM invoice_items ii 
#             LEFT JOIN products p ON ii.product_id = p.id 
#             WHERE ii.invoice_id = %s
#         """, (invoice_id,))
    
#     def get_setting(self, key, default=None):
#         result = self.fetch_one("SELECT setting_value FROM settings WHERE setting_key = %s", (key,))
#         return result['setting_value'] if result else default
    
#     def set_setting(self, key, value):
#         # Check if setting exists
#         existing = self.get_setting(key)
#         if existing is not None:
#             self.execute_query("UPDATE settings SET setting_value = %s WHERE setting_key = %s", (value, key))
#         else:
#             self.execute_query("INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s)", (key, value))
    
#     def close(self):
#         if self.connection and self.connection.is_connected():
#             self.connection.close()