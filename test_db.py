#!/usr/bin/env python3
import mysql.connector
from database import Database

# def test_database_connection():
#     print("Testing database connection...")
    
#     try:
#         # Test direct connection
#         print("1. Testing direct MySQL connection...")
#         conn = mysql.connector.connect(
#             host="localhost",
#             user="root",  # Change if needed
#             password="admin",  # Change if needed
#             database="billing_software"  # Change if needed
#         )
#         print("✓ Direct MySQL connection successful!")
#         conn.close()
#     except Exception as e:
#         print(f"✗ Direct MySQL connection failed: {e}")
    
#     try:
#         # Test your Database class
#         print("2. Testing Database class connection...")
#         db = Database()
#         print("✓ Database class instantiation successful!")
        
#         # Test a simple query
#         result = db.fetch_one("SELECT 1")
#         print(f"✓ Simple query test: {result}")
        
#     except Exception as e:
#         print(f"✗ Database class test failed: {e}")

# if __name__ == "__main__":
#     test_database_connection()

# from database import Database
# db = Database()
# print(hasattr(db, 'add_product'))

# check_schema.py
# import mysql.connector

def check_schema():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='admin',
        database='billing_software'
    )
    
    cursor = conn.cursor(dictionary=True)
    
    # Check clients table structure
    cursor.execute("DESCRIBE clients")
    columns = cursor.fetchall()
    print("Clients table columns:")
    for col in columns:
        print(f"  - {col['Field']} ({col['Type']})")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_schema()