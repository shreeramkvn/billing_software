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