# Billing Software

A comprehensive billing software with inventory management, built with Python and MySQL.

## Features

- Product management with HSN codes
- Client management (B2B and B2C)
- Sales and purchase invoicing
- Barcode scanning support
- PDF invoice generation
- Stock management
- Thermal printer support

## Installation

1. Install Python 3.7+
2. Install MySQL Server
3. Clone this repository
4. Install dependencies: `pip install -r requirements.txt`
5. Run the setup: `python create_config_files.py`
6. Set up the database: Import `database_schema.sql` into MySQL
7. Run the application: `python main.py`

## Building Executable

To build a standalone executable:

```bash
python build.py