CREATE DATABASE billing_software;

USE billing_software;

-- Company information table
CREATE TABLE company (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    gst_number VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100)
);

select * from products;

DESCRIBE products;

-- Products table
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    hsn_code VARCHAR(8) NOT NULL CHECK (LENGTH(hsn_code) BETWEEN 4 AND 8),
    rate DECIMAL(10, 2) NOT NULL,
    current_stock DECIMAL(10, 2) DEFAULT 0,
    barcode VARCHAR(100) UNIQUE
);

-- Clients table (both B2B and B2C)
CREATE TABLE clients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    gst_number VARCHAR(50),
    phone VARCHAR(20),
    client_type ENUM('B2B', 'B2C') NOT NULL,
    last_bill_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Describe clients;

ALTER TABLE products ADD COLUMN hsn_code VARCHAR(8);

-- Invoices table
CREATE TABLE invoices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    client_id INT,
    date DATE NOT NULL,
    type ENUM('PURCHASE', 'SALE') NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- Invoice items table
CREATE TABLE invoice_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_id INT,
    product_id INT,
    description TEXT,
    hsn_code VARCHAR(8),
    quantity DECIMAL(10, 2) NOT NULL,
    rate DECIMAL(10, 2) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Stock movements table
CREATE TABLE stock_movements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    quantity DECIMAL(10, 2) NOT NULL,
    movement_type ENUM('IN', 'OUT') NOT NULL,
    reference_id INT, -- links to invoice_id
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- System settings table
CREATE TABLE settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT
);

ALTER TABLE products ADD COLUMN rate DECIMAL(10, 2) NOT NULL DEFAULT 0;

ALTER TABLE products ADD COLUMN current_stock DECIMAL(10, 2) DEFAULT 0;

-- Check your current table structure
DESCRIBE items;
DESCRIBE invoices;
DESCRIBE invoice_items;

-- You likely need to add missing columns:
ALTER TABLE items ADD COLUMN type VARCHAR(50);
ALTER TABLE invoice_items ADD COLUMN client_id INT;
ALTER TABLE items MODIFY COLUMN price DECIMAL(10,2) NOT NULL;

-- Or if the price column doesn't exist:
ALTER TABLE items ADD COLUMN price DECIMAL(10,2) NOT NULL;

-- First, create the items table
CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    type VARCHAR(50),
    barcode VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create clients table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create invoices table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT,
    invoice_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
);

-- Update invoice_items table to include client_id and fix relationships
ALTER TABLE invoice_items 
ADD COLUMN client_id INT,
ADD COLUMN item_name VARCHAR(255),
ADD COLUMN unit_price DECIMAL(10, 2),
ADD FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL;

-- Add some sample data to get started
INSERT INTO items (name, price, type) VALUES
('Product A', 100.00, 'product'),
('Product B', 200.00, 'product'),
('Service A', 150.00, 'service'),
('Service B', 250.00, 'service');

INSERT INTO clients (name, phone, email) VALUES
('Client A', '123-456-7890', 'clienta@email.com'),
('Client B', '098-765-4321', 'clientb@email.com');

-- First, check the current structure of your clients table
DESCRIBE clients;

-- Add the missing email column
ALTER TABLE clients ADD COLUMN email VARCHAR(255);

-- If you want to add other missing columns that might be needed:
ALTER TABLE clients 
ADD COLUMN phone VARCHAR(20),
ADD COLUMN address TEXT;

-- Alternatively, if you want to recreate the clients table properly:
DROP TABLE IF EXISTS clients;

CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Now insert the sample data without errors
INSERT INTO clients (name, phone, email) VALUES
('Client A', '123-456-7890', 'clienta@email.com'),
('Client B', '098-765-4321', 'clientb@email.com');

-- Add the missing gst_number column to clients table
ALTER TABLE clients ADD COLUMN gst_number VARCHAR(50);

-- Also add other commonly used columns that might be missing
ALTER TABLE clients 
ADD COLUMN address TEXT,
ADD COLUMN city VARCHAR(100),
ADD COLUMN state VARCHAR(100),
ADD COLUMN pin_code VARCHAR(20);

-- Check the updated structure
DESCRIBE clients;

-- Add stock_quantity column to items table
ALTER TABLE items ADD COLUMN stock_quantity INT DEFAULT 0;

-- Add low_stock_threshold column if needed
ALTER TABLE items ADD COLUMN low_stock_threshold INT DEFAULT 10;

ALTER TABLE clients ADD COLUMN gst_number VARCHAR(50) DEFAULT '';