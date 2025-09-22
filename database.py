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
                'user': 'root',
                'password': 'admin',
                'database': 'billing_software'
            }
        
        self.connect()

    def add_product(self, name, description, hsn_code, rate, barcode):
        query = "INSERT INTO products (name, description, hsn_code, rate, barcode) VALUES (%s, %s, %s, %s, %s)"
        return self.execute_query(query, (name, description, hsn_code, rate, barcode))
    
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
            cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE invoice_date = %s", (today,))
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()  # <-- Add this line
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
            cursor = self.connection.cursor(dictionary=True)  # <-- Add dictionary=True
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

def get_total_items(self):
    """Get total number of items"""
    try:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM items")
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error getting total items: {e}")
        return 0

def get_total_clients(self):
    """Get total number of clients"""
    try:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clients")
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error getting total clients: {e}")
        return 0

def get_total_sales(self):
    """Get total sales amount"""
    try:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE type = 'SALE'")
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error getting total sales: {e}")
        return 0

if __name__ == "__main__":
    test_connection()