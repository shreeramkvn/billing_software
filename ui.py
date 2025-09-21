import os
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from tkinter import filedialog
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from database import Database
from barcode_utils import BarcodeScanner
from pdf_generator import PDFGenerator
import config

class MainUI:
    def __init__(self, root, db, company_name):
        self.root = root
        self.db = db
        self.company_name = company_name
        self.pdf_generator = PDFGenerator(company_name)
        self.barcode_scanner = BarcodeScanner()
        
        # Set up the main notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_dashboard_tab()
        self.setup_products_tab()
        self.setup_clients_tab()
        self.setup_sales_tab()
        self.setup_purchase_tab()
        self.setup_reports_tab()
        self.setup_settings_tab()
        
        # Load initial data
        self.load_products()
        self.load_clients()
        self.load_recent_invoices()
        
    def setup_dashboard_tab(self):
        """Create the dashboard tab"""
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text='Dashboard')
        
        # Welcome label
        welcome_label = ttk.Label(
            self.dashboard_tab, 
            text=f"Welcome to {self.company_name} Billing Software",
            font=("Arial", 16, "bold")
        )
        welcome_label.pack(pady=20)
        
        # Summary frame
        summary_frame = ttk.LabelFrame(self.dashboard_tab, text="Summary")
        summary_frame.pack(fill='x', padx=20, pady=10)
        
        # Summary metrics - Use safe method calls to avoid errors during initialization
        total_products = len(self.get_products_safe())
        total_clients = len(self.get_clients_safe())
        low_stock = self.count_low_stock_items()
        today_sales = self.get_today_sales()
        
        metrics = [
            ("Total Products", total_products),
            ("Total Clients", total_clients),
            ("Low Stock Items", low_stock),
            ("Today's Sales", today_sales)
        ]
        
        for i, (label, value) in enumerate(metrics):
            frame = ttk.Frame(summary_frame)
            frame.grid(row=0, column=i, padx=20, pady=10)
            
            ttk.Label(frame, text=label, font=("Arial", 10)).pack()
            ttk.Label(frame, text=str(value), font=("Arial", 14, "bold")).pack()
        
        # Recent invoices frame
        invoice_frame = ttk.LabelFrame(self.dashboard_tab, text="Recent Invoices")
        invoice_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create treeview for recent invoices
        columns = ('id', 'number', 'client', 'date', 'type', 'amount')
        self.invoice_tree = ttk.Treeview(invoice_frame, columns=columns, show='headings')
        
        # Define headings
        self.invoice_tree.heading('id', text='ID')
        self.invoice_tree.heading('number', text='Invoice Number')
        self.invoice_tree.heading('client', text='Client')
        self.invoice_tree.heading('date', text='Date')
        self.invoice_tree.heading('type', text='Type')
        self.invoice_tree.heading('amount', text='Amount')
        
        # Define columns
        self.invoice_tree.column('id', width=50)
        self.invoice_tree.column('number', width=100)
        self.invoice_tree.column('client', width=150)
        self.invoice_tree.column('date', width=100)
        self.invoice_tree.column('type', width=100)
        self.invoice_tree.column('amount', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(invoice_frame, orient=tk.VERTICAL, command=self.invoice_tree.yview)
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.invoice_tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # View invoice button
        view_btn = ttk.Button(
            self.dashboard_tab, 
            text="View Selected Invoice", 
            command=self.view_selected_invoice
        )
        view_btn.pack(pady=10)
    
    def setup_products_tab(self):
        """Create the products management tab"""
        self.products_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.products_tab, text='Products')
        
        # Top frame for form
        form_frame = ttk.LabelFrame(self.products_tab, text="Add/Edit Product")
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # Form fields
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.product_name = ttk.Entry(form_frame, width=30)
        self.product_name.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.product_desc = ttk.Entry(form_frame, width=30)
        self.product_desc.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(form_frame, text="HSN Code:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.product_hsn = ttk.Entry(form_frame, width=30)
        self.product_hsn.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(form_frame, text="Rate:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.product_rate = ttk.Entry(form_frame, width=30)
        self.product_rate.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(form_frame, text="Barcode:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        barcode_frame = ttk.Frame(form_frame)
        barcode_frame.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        
        self.product_barcode = ttk.Entry(barcode_frame, width=25)
        self.product_barcode.pack(side=tk.LEFT)
        
        scan_btn = ttk.Button(barcode_frame, text="Scan", command=self.scan_barcode_for_product)
        scan_btn.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Add Product", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update Product", command=self.update_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_product_form).pack(side=tk.LEFT, padx=5)
        
        # Products list
        list_frame = ttk.LabelFrame(self.products_tab, text="Products List")
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create treeview
        columns = ('id', 'name', 'description', 'hsn', 'rate', 'stock', 'barcode')
        self.product_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Define headings
        self.product_tree.heading('id', text='ID')
        self.product_tree.heading('name', text='Name')
        self.product_tree.heading('description', text='Description')
        self.product_tree.heading('hsn', text='HSN Code')
        self.product_tree.heading('rate', text='Rate')
        self.product_tree.heading('stock', text='Stock')
        self.product_tree.heading('barcode', text='Barcode')
        
        # Define columns
        self.product_tree.column('id', width=50)
        self.product_tree.column('name', width=150)
        self.product_tree.column('description', width=200)
        self.product_tree.column('hsn', width=80)
        self.product_tree.column('rate', width=80)
        self.product_tree.column('stock', width=80)
        self.product_tree.column('barcode', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.product_tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.product_tree.bind('<<TreeviewSelect>>', self.on_product_select)
        
        # Action buttons for products list
        action_frame = ttk.Frame(self.products_tab)
        action_frame.pack(pady=10)
        
        ttk.Button(action_frame, text="Delete Selected", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refresh List", command=self.load_products).pack(side=tk.LEFT, padx=5)
    
    def setup_clients_tab(self):
        """Create the clients management tab"""
        self.clients_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.clients_tab, text='Clients')
        
        # Top frame for form
        form_frame = ttk.LabelFrame(self.clients_tab, text="Add/Edit Client")
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # Client type selection
        ttk.Label(form_frame, text="Client Type:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.client_type = tk.StringVar(value="B2C")
        ttk.Radiobutton(form_frame, text="B2C", variable=self.client_type, value="B2C").grid(row=0, column=1, sticky='w')
        ttk.Radiobutton(form_frame, text="B2B", variable=self.client_type, value="B2B").grid(row=0, column=2, sticky='w')
        
        # Form fields
        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.client_name = ttk.Entry(form_frame, width=30)
        self.client_name.grid(row=1, column=1, padx=5, pady=5, sticky='w', columnspan=2)
        
        ttk.Label(form_frame, text="Address:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.client_address = scrolledtext.ScrolledText(form_frame, width=28, height=3)
        self.client_address.grid(row=2, column=1, padx=5, pady=5, sticky='w', columnspan=2)
        
        ttk.Label(form_frame, text="Phone:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.client_phone = ttk.Entry(form_frame, width=30)
        self.client_phone.grid(row=3, column=1, padx=5, pady=5, sticky='w', columnspan=2)
        
        ttk.Label(form_frame, text="GST Number:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.client_gst = ttk.Entry(form_frame, width=30)
        self.client_gst.grid(row=4, column=1, padx=5, pady=5, sticky='w', columnspan=2)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="Add Client", command=self.add_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update Client", command=self.update_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_client_form).pack(side=tk.LEFT, padx=5)
        
        # Clients list
        list_frame = ttk.LabelFrame(self.clients_tab, text="Clients List")
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Filter frame
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill='x', pady=5)
        
        ttk.Label(filter_frame, text="Filter by Type:").pack(side=tk.LEFT, padx=5)
        self.client_filter = tk.StringVar(value="ALL")
        ttk.Combobox(filter_frame, textvariable=self.client_filter, 
                    values=["ALL", "B2B", "B2C"], state="readonly", width=10).pack(side=tk.LEFT, padx=5)
        self.client_filter.trace('w', self.load_clients)
        
        # Create treeview
        columns = ('id', 'name', 'address', 'phone', 'gst', 'type', 'last_bill')
        self.client_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Define headings
        self.client_tree.heading('id', text='ID')
        self.client_tree.heading('name', text='Name')
        self.client_tree.heading('address', text='Address')
        self.client_tree.heading('phone', text='Phone')
        self.client_tree.heading('gst', text='GST Number')
        self.client_tree.heading('type', text='Type')
        self.client_tree.heading('last_bill', text='Last Bill')
        
        # Define columns
        self.client_tree.column('id', width=50)
        self.client_tree.column('name', width=150)
        self.client_tree.column('address', width=200)
        self.client_tree.column('phone', width=100)
        self.client_tree.column('gst', width=120)
        self.client_tree.column('type', width=80)
        self.client_tree.column('last_bill', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.client_tree.yview)
        self.client_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.client_tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.client_tree.bind('<<TreeviewSelect>>', self.on_client_select)
        
        # Action buttons for clients list
        action_frame = ttk.Frame(self.clients_tab)
        action_frame.pack(pady=10)
        
        ttk.Button(action_frame, text="Delete Selected", command=self.delete_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refresh List", command=self.load_clients).pack(side=tk.LEFT, padx=5)
    
    def setup_sales_tab(self):
        """Create the sales (stock out) tab"""
        self.sales_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_tab, text='Sales')
        
        # Top frame for client selection
        client_frame = ttk.LabelFrame(self.sales_tab, text="Client Selection")
        client_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(client_frame, text="Select Client:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.sale_client = tk.StringVar()
        clients = [c['name'] for c in self.get_clients_safe()]
        self.client_combo = ttk.Combobox(client_frame, textvariable=self.sale_client, values=clients, state="readonly")
        self.client_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Button(client_frame, text="New Client", command=self.add_client_from_sales).grid(row=0, column=2, padx=5, pady=5)
        
        # Product selection frame
        product_frame = ttk.LabelFrame(self.sales_tab, text="Add Product to Invoice")
        product_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(product_frame, text="Product:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.sale_product = tk.StringVar()
        products = [p['name'] for p in self.get_products_safe()]
        self.product_combo = ttk.Combobox(product_frame, textvariable=self.sale_product, values=products, state="readonly")
        self.product_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.product_combo.bind('<<ComboboxSelected>>', self.on_product_selected)
        
        ttk.Label(product_frame, text="Quantity:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.sale_quantity = ttk.Entry(product_frame, width=10)
        self.sale_quantity.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        ttk.Label(product_frame, text="Rate:").grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.sale_rate = ttk.Entry(product_frame, width=10, state='readonly')
        self.sale_rate.grid(row=0, column=5, padx=5, pady=5, sticky='w')
        
        ttk.Button(product_frame, text="Scan Barcode", command=self.scan_barcode_for_sale).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(product_frame, text="Add to Invoice", command=self.add_to_invoice).grid(row=0, column=7, padx=5, pady=5)
        
        # Invoice items frame
        items_frame = ttk.LabelFrame(self.sales_tab, text="Invoice Items")
        items_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create treeview for invoice items
        columns = ('sno', 'description', 'hsn', 'qty', 'rate', 'amount')
        self.invoice_items_tree = ttk.Treeview(items_frame, columns=columns, show='headings')
        
        # Define headings
        self.invoice_items_tree.heading('sno', text='SNo')
        self.invoice_items_tree.heading('description', text='Description')
        self.invoice_items_tree.heading('hsn', text='HSN Code')
        self.invoice_items_tree.heading('qty', text='Quantity')
        self.invoice_items_tree.heading('rate', text='Rate')
        self.invoice_items_tree.heading('amount', text='Amount')
        
        # Define columns
        self.invoice_items_tree.column('sno', width=50)
        self.invoice_items_tree.column('description', width=250)
        self.invoice_items_tree.column('hsn', width=80)
        self.invoice_items_tree.column('qty', width=80)
        self.invoice_items_tree.column('rate', width=80)
        self.invoice_items_tree.column('amount', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.invoice_items_tree.yview)
        self.invoice_items_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.invoice_items_tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Total amount frame
        total_frame = ttk.Frame(self.sales_tab)
        total_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(total_frame, text="Total Amount:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.total_amount = ttk.Label(total_frame, text="0.00", font=("Arial", 10, "bold"))
        self.total_amount.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = ttk.Frame(self.sales_tab)
        action_frame.pack(pady=10)
        
        ttk.Button(action_frame, text="Remove Selected", command=self.remove_invoice_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Clear Invoice", command=self.clear_invoice).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Generate Invoice", command=self.generate_sale_invoice).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Print Receipt", command=self.print_receipt).pack(side=tk.LEFT, padx=5)
        
        # Initialize invoice items list
        self.invoice_items = []
    
    def setup_purchase_tab(self):
        """Create the purchase (stock in) tab"""
        self.purchase_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.purchase_tab, text='Purchase')
        
        # This tab would be similar to sales tab but for purchases
        # Implementation would follow similar pattern as sales tab
        
        placeholder = ttk.Label(self.purchase_tab, text="Purchase Management - Similar to Sales Tab", font=("Arial", 12))
        placeholder.pack(pady=50)
    
    def setup_reports_tab(self):
        """Create the reports tab"""
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text='Reports')
        
        # Filter frame
        filter_frame = ttk.LabelFrame(self.reports_tab, text="Report Filters")
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(filter_frame, text="From:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.report_from_date = DateEntry(filter_frame, width=12, background='darkblue', 
                                         foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.report_from_date.set_date(datetime.now() - timedelta(days=30))
        self.report_from_date.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(filter_frame, text="To:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.report_to_date = DateEntry(filter_frame, width=12, background='darkblue', 
                                       foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.report_to_date.set_date(datetime.now())
        self.report_to_date.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        ttk.Label(filter_frame, text="Report Type:").grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.report_type = tk.StringVar(value="SALES")
        report_combo = ttk.Combobox(filter_frame, textvariable=self.report_type, 
                                   values=["SALES", "PURCHASE", "STOCK"], state="readonly", width=10)
        report_combo.grid(row=0, column=5, padx=5, pady=5, sticky='w')
        
        ttk.Button(filter_frame, text="Generate Report", command=self.generate_report).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(filter_frame, text="Export to PDF", command=self.export_report).grid(row=0, column=7, padx=5, pady=5)
        
        # Report display frame
        report_frame = ttk.LabelFrame(self.reports_tab, text="Report Results")
        report_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create text widget for report display
        self.report_text = scrolledtext.ScrolledText(report_frame, width=80, height=20)
        self.report_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def setup_settings_tab(self):
        """Create the settings tab"""
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text='Settings')
        
        # Company settings frame
        company_frame = ttk.LabelFrame(self.settings_tab, text="Company Settings")
        company_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(company_frame, text="Company Name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.setting_company_name = ttk.Entry(company_frame, width=30)
        self.setting_company_name.insert(0, self.company_name)
        self.setting_company_name.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(company_frame, text="Address:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.setting_company_address = scrolledtext.ScrolledText(company_frame, width=28, height=3)
        self.setting_company_address.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(company_frame, text="GST Number:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.setting_company_gst = ttk.Entry(company_frame, width=30)
        self.setting_company_gst.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(company_frame, text="Phone:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.setting_company_phone = ttk.Entry(company_frame, width=30)
        self.setting_company_phone.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Button(company_frame, text="Save Company Settings", command=self.save_company_settings).grid(row=4, column=1, padx=5, pady=10, sticky='w')
        
        # Application settings frame
        app_frame = ttk.LabelFrame(self.settings_tab, text="Application Settings")
        app_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(app_frame, text="Allow Negative Stock:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.setting_negative_stock = tk.BooleanVar(value=config.ALLOW_NEGATIVE_STOCK)
        ttk.Checkbutton(app_frame, variable=self.setting_negative_stock).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(app_frame, text="Thermal Printer Width:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.setting_printer_width = ttk.Entry(app_frame, width=10)
        self.setting_printer_width.insert(0, str(config.THERMAL_PRINTER_WIDTH))
        self.setting_printer_width.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Button(app_frame, text="Save Application Settings", command=self.save_app_settings).grid(row=2, column=1, padx=5, pady=10, sticky='w')
        
        # Database operations frame
        db_frame = ttk.LabelFrame(self.settings_tab, text="Database Operations")
        db_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(db_frame, text="Backup Database", command=self.backup_database).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(db_frame, text="Restore Database", command=self.restore_database).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(db_frame, text="Optimize Database", command=self.optimize_database).pack(side=tk.LEFT, padx=5, pady=5)
    
    # Safe methods to handle missing database methods
    def get_products_safe(self):
        """Safely get products, handling missing method"""
        try:
            if hasattr(self.db, 'get_products'):
                return self.db.get_products()
            else:
                # Fallback to direct database query
                return self.db.fetch_all("SELECT * FROM products")
        except Exception as e:
            print(f"Error getting products: {e}")
            return []
    
    def get_clients_safe(self):
        """Safely get clients, handling missing method"""
        try:
            if hasattr(self.db, 'get_clients'):
                return self.db.get_clients()
            else:
                # Fallback to direct database query
                return self.db.fetch_all("SELECT * FROM clients")
        except Exception as e:
            print(f"Error getting clients: {e}")
            return []
    
    # Data loading methods
    def load_products(self):
        """Load products into the products treeview"""
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        products = self.get_products_safe()
        for product in products:
            self.product_tree.insert('', 'end', values=(
                product['id'],
                product['name'],
                product['description'],
                product['hsn_code'],
                f"{product['rate']:.2f}",
                f"{product['current_stock']:.2f}",
                product['barcode'] or ''
            ))
    
    def load_clients(self):
        """Load clients into the clients treeview"""
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        
        client_type = self.client_filter.get()
        try:
            if hasattr(self.db, 'get_clients'):
                clients = self.db.get_clients(client_type if client_type != "ALL" else None)
            else:
                # Fallback to direct database query
                if client_type != "ALL":
                    clients = self.db.fetch_all("SELECT * FROM clients WHERE client_type = %s", (client_type,))
                else:
                    clients = self.db.fetch_all("SELECT * FROM clients")
        except Exception as e:
            print(f"Error loading clients: {e}")
            clients = []
        
        for client in clients:
            self.client_tree.insert('', 'end', values=(
                client['id'],
                client['name'],
                client['address'],
                client['phone'],
                client['gst_number'] or '',
                client['client_type'],
                client['last_bill_date'] or 'Never'
            ))
    
    def load_recent_invoices(self):
        """Load recent invoices into the dashboard treeview"""
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        
        # Get invoices from last 30 days
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        try:
            if hasattr(self.db, 'get_invoices'):
                invoices = self.db.get_invoices(start_date=start_date)
            else:
                # Fallback to direct database query
                invoices = self.db.fetch_all("""
                    SELECT i.*, c.name as client_name, c.gst_number 
                    FROM invoices i 
                    LEFT JOIN clients c ON i.client_id = c.id 
                    WHERE i.date >= %s
                """, (start_date,))
        except Exception as e:
            print(f"Error loading invoices: {e}")
            invoices = []
        
        for invoice in invoices:
            self.invoice_tree.insert('', 'end', values=(
                invoice['id'],
                invoice['invoice_number'],
                invoice['client_name'] or 'Walk-in Customer',
                invoice['date'],
                invoice['type'],
                f"{invoice['total_amount']:.2f}"
            ))
    
    # Event handlers
    def on_product_select(self, event):
        """Handle product selection event"""
        selected = self.product_tree.selection()
        if not selected:
            return
        
        item = self.product_tree.item(selected[0])
        values = item['values']
        
        # Fill form with selected product details
        self.product_name.delete(0, tk.END)
        self.product_name.insert(0, values[1])
        
        self.product_desc.delete(0, tk.END)
        self.product_desc.insert(0, values[2])
        
        self.product_hsn.delete(0, tk.END)
        self.product_hsn.insert(0, values[3])
        
        self.product_rate.delete(0, tk.END)
        self.product_rate.insert(0, values[4])
        
        self.product_barcode.delete(0, tk.END)
        self.product_barcode.insert(0, values[6] or '')
    
    def on_client_select(self, event):
        """Handle client selection event"""
        selected = self.client_tree.selection()
        if not selected:
            return
        
        item = self.client_tree.item(selected[0])
        values = item['values']
        
        # Fill form with selected client details
        self.client_name.delete(0, tk.END)
        self.client_name.insert(0, values[1])
        
        self.client_address.delete('1.0', tk.END)
        self.client_address.insert('1.0', values[2])
        
        self.client_phone.delete(0, tk.END)
        self.client_phone.insert(0, values[3])
        
        self.client_gst.delete(0, tk.END)
        self.client_gst.insert(0, values[4] or '')
        
        self.client_type.set(values[5])
    
    def on_product_selected(self, event):
        """Handle product selection in sales tab"""
        product_name = self.sale_product.get()
        if not product_name:
            return
        
        products = self.get_products_safe()
        product = next((p for p in products if p['name'] == product_name), None)
        
        if product:
            self.sale_rate.config(state='normal')
            self.sale_rate.delete(0, tk.END)
            self.sale_rate.insert(0, f"{product['rate']:.2f}")
            self.sale_rate.config(state='readonly')
            # Auto-focus on quantity field for faster entry
            self.sale_quantity.focus_set()
    
    def scan_barcode_for_product(self):
        """Scan barcode for product form"""
        barcode = self.barcode_scanner.scan_barcode()
        if barcode:
            self.product_barcode.delete(0, tk.END)
            self.product_barcode.insert(0, barcode)
    
    def scan_barcode_for_sale(self):
        """Scan barcode for sales tab"""
        barcode = self.barcode_scanner.scan_barcode()
        if barcode:
            # Find product by barcode
            products = self.get_products_safe()
            product = next((p for p in products if p['barcode'] == barcode), None)
            
            if product:
                self.sale_product.set(product['name'])
                self.sale_rate.config(state='normal')
                self.sale_rate.delete(0, tk.END)
                self.sale_rate.insert(0, f"{product['rate']:.2f}")
                self.sale_rate.config(state='readonly')
                self.sale_quantity.focus_set()
            else:
                messagebox.showwarning("Product Not Found", f"No product found with barcode: {barcode}")
    
    def add_to_invoice(self):
        """Add selected product to invoice"""
        product_name = self.sale_product.get()
        quantity_str = self.sale_quantity.get()
        rate_str = self.sale_rate.get()
        
        if not product_name or not quantity_str or not rate_str:
            messagebox.showerror("Error", "Please select a product and enter quantity")
            return
        
        try:
            quantity = float(quantity_str)
            rate = float(rate_str)
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
            return
        
        # Get product details
        products = self.get_products_safe()
        product = next((p for p in products if p['name'] == product_name), None)
        
        if not product:
            messagebox.showerror("Error", "Selected product not found")
            return
        
        # Check stock availability
        if not config.ALLOW_NEGATIVE_STOCK and product['current_stock'] < quantity:
            messagebox.showerror("Error", f"Insufficient stock. Available: {product['current_stock']}")
            return
        
        amount = quantity * rate
        item_number = len(self.invoice_items) + 1
        
        # Add to invoice items list
        item = {
            'product_id': product['id'],
            'description': product['name'],
            'hsn': product['hsn_code'],
            'quantity': quantity,
            'rate': rate,
            'amount': amount
        }
        self.invoice_items.append(item)
        
        # Add to treeview
        self.invoice_items_tree.insert('', 'end', values=(
            item_number,
            product['name'],
            product['hsn_code'],
            f"{quantity:.2f}",
            f"{rate:.2f}",
            f"{amount:.2f}"
        ))
        
        # Update total amount
        self.update_total_amount()
        
        # Clear selection and focus on next entry
        self.sale_quantity.delete(0, tk.END)
        self.sale_product.set('')
        self.sale_rate.config(state='normal')
        self.sale_rate.delete(0, tk.END)
        self.sale_rate.config(state='readonly')
        self.product_combo.focus_set()
    
    def update_total_amount(self):
        """Update the total amount display"""
        total = sum(item['amount'] for item in self.invoice_items)
        self.total_amount.config(text=f"{total:.2f}")
    
    def remove_invoice_item(self):
        """Remove selected item from invoice"""
        selected = self.invoice_items_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        # Get the index of selected item
        index = self.invoice_items_tree.index(selected[0])
        
        # Remove from list and treeview
        if 0 <= index < len(self.invoice_items):
            self.invoice_items.pop(index)
            self.invoice_items_tree.delete(selected[0])
            
            # Renumber the items
            for i, item_id in enumerate(self.invoice_items_tree.get_children()):
                values = list(self.invoice_items_tree.item(item_id)['values'])
                values[0] = i + 1
                self.invoice_items_tree.item(item_id, values=values)
            
            self.update_total_amount()
    
    def clear_invoice(self):
        """Clear the current invoice"""
        if self.invoice_items and not messagebox.askyesno("Confirm", "Clear current invoice?"):
            return
        
        self.invoice_items.clear()
        for item in self.invoice_items_tree.get_children():
            self.invoice_items_tree.delete(item)
        
        self.update_total_amount()
        self.sale_client.set('')
        self.sale_product.set('')
        self.sale_quantity.delete(0, tk.END)
        self.sale_rate.config(state='normal')
        self.sale_rate.delete(0, tk.END)
        self.sale_rate.config(state='readonly')
    
    def generate_sale_invoice(self):
        """Generate sale invoice"""
        if not self.invoice_items:
            messagebox.showerror("Error", "No items in invoice")
            return
        
        client_name = self.sale_client.get()
        client_id = None
        
        # If client is selected, get client ID
        if client_name:
            clients = self.get_clients_safe()
            client = next((c for c in clients if c['name'] == client_name), None)
            if client:
                client_id = client['id']
            else:
                messagebox.showerror("Error", "Selected client not found")
                return
        
        try:
            # Generate invoice in database
            invoice_id = self.db.create_invoice(
                client_id=client_id,
                invoice_type='SALE',
                items=self.invoice_items
            )
            
            # Generate PDF
            invoice_data = self.db.get_invoice(invoice_id)
            pdf_path = self.pdf_generator.generate_invoice_pdf(invoice_data)
            
            messagebox.showinfo("Success", f"Invoice generated successfully!\nPDF saved at: {pdf_path}")
            
            # Clear invoice and refresh data
            self.clear_invoice()
            self.load_products()  # Refresh stock levels
            self.load_recent_invoices()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate invoice: {str(e)}")
    
    def print_receipt(self):
        """Print thermal receipt"""
        if not self.invoice_items:
            messagebox.showerror("Error", "No items in invoice")
            return
        
        # This would interface with thermal printer
        # For now, just show a message
        messagebox.showinfo("Print", "This would print a thermal receipt")
    
    def add_product(self):
        """Add new product"""
        name = self.product_name.get().strip()
        description = self.product_desc.get().strip()
        hsn = self.product_hsn.get().strip()
        rate_str = self.product_rate.get().strip()
        barcode = self.product_barcode.get().strip()
        
        if not name or not rate_str:
            messagebox.showerror("Error", "Name and Rate are required")
            return
        
        try:
            rate = float(rate_str)
            if rate <= 0:
                messagebox.showerror("Error", "Rate must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid rate")
            return
        
        try:
            self.db.add_product(
                name=name,
                description=description,
                hsn_code=hsn,
                rate=rate,
                barcode=barcode
            )
            messagebox.showinfo("Success", "Product added successfully")
            self.clear_product_form()
            self.load_products()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")
    
    def update_product(self):
        """Update selected product"""
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to update")
            return
        
        product_id = self.product_tree.item(selected[0])['values'][0]
        name = self.product_name.get().strip()
        description = self.product_desc.get().strip()
        hsn = self.product_hsn.get().strip()
        rate_str = self.product_rate.get().strip()
        barcode = self.product_barcode.get().strip()
        
        if not name or not rate_str:
            messagebox.showerror("Error", "Name and Rate are required")
            return
        
        try:
            rate = float(rate_str)
            if rate <= 0:
                messagebox.showerror("Error", "Rate must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid rate")
            return
        
        try:
            self.db.update_product(
                product_id=product_id,
                name=name,
                description=description,
                hsn_code=hsn,
                rate=rate,
                barcode=barcode
            )
            messagebox.showinfo("Success", "Product updated successfully")
            self.load_products()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update product: {str(e)}")
    
    def delete_product(self):
        """Delete selected product"""
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
            return
        
        product_id = self.product_tree.item(selected[0])['values'][0]
        
        try:
            self.db.delete_product(product_id)
            messagebox.showinfo("Success", "Product deleted successfully")
            self.clear_product_form()
            self.load_products()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
    
    def clear_product_form(self):
        """Clear product form fields"""
        self.product_name.delete(0, tk.END)
        self.product_desc.delete(0, tk.END)
        self.product_hsn.delete(0, tk.END)
        self.product_rate.delete(0, tk.END)
        self.product_barcode.delete(0, tk.END)
        self.product_tree.selection_remove(self.product_tree.selection())
    
    def add_client(self):
        """Add new client"""
        name = self.client_name.get().strip()
        address = self.client_address.get('1.0', tk.END).strip()
        phone = self.client_phone.get().strip()
        gst = self.client_gst.get().strip()
        client_type = self.client_type.get()
        
        if not name:
            messagebox.showerror("Error", "Client name is required")
            return
        
        # Validate GST for B2B clients
        if client_type == 'B2B' and not gst:
            if not messagebox.askyesno("Confirm", "B2B client without GST number. Continue?"):
                return
        
        try:
            self.db.add_client(
                name=name,
                address=address,
                phone=phone,
                gst_number=gst,
                client_type=client_type
            )
            messagebox.showinfo("Success", "Client added successfully")
            self.clear_client_form()
            self.load_clients()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add client: {str(e)}")
    
    def update_client(self):
        """Update selected client"""
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a client to update")
            return
        
        client_id = self.client_tree.item(selected[0])['values'][0]
        name = self.client_name.get().strip()
        address = self.client_address.get('1.0', tk.END).strip()
        phone = self.client_phone.get().strip()
        gst = self.client_gst.get().strip()
        client_type = self.client_type.get()
        
        if not name:
            messagebox.showerror("Error", "Client name is required")
            return
        
        # Validate GST for B2B clients
        if client_type == 'B2B' and not gst:
            if not messagebox.askyesno("Confirm", "B2B client without GST number. Continue?"):
                return
        
        try:
            self.db.update_client(
                client_id=client_id,
                name=name,
                address=address,
                phone=phone,
                gst_number=gst,
                client_type=client_type
            )
            messagebox.showinfo("Success", "Client updated successfully")
            self.load_clients()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update client: {str(e)}")
    
    def delete_client(self):
        """Delete selected client"""
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a client to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this client?"):
            return
        
        client_id = self.client_tree.item(selected[0])['values'][0]
        
        try:
            self.db.delete_client(client_id)
            messagebox.showinfo("Success", "Client deleted successfully")
            self.clear_client_form()
            self.load_clients()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete client: {str(e)}")
    
    def clear_client_form(self):
        """Clear client form fields"""
        self.client_name.delete(0, tk.END)
        self.client_address.delete('1.0', tk.END)
        self.client_phone.delete(0, tk.END)
        self.client_gst.delete(0, tk.END)
        self.client_type.set("B2C")
        self.client_tree.selection_remove(self.client_tree.selection())
    
    def add_client_from_sales(self):
        """Open client form from sales tab"""
        self.notebook.select(self.clients_tab)
    
    def view_selected_invoice(self):
        """View selected invoice details"""
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an invoice to view")
            return
        
        invoice_id = self.invoice_tree.item(selected[0])['values'][0]
        
        try:
            invoice_data = self.db.get_invoice(invoice_id)
            
            # Display invoice details
            details = f"Invoice #{invoice_data['invoice_number']}\n"
            details += f"Date: {invoice_data['date']}\n"
            details += f"Client: {invoice_data.get('client_name', 'Walk-in Customer')}\n"
            details += f"Type: {invoice_data['type']}\n"
            details += f"Total Amount: ₹{invoice_data['total_amount']:.2f}\n\n"
            details += "Items:\n"
            
            for item in invoice_data.get('items', []):
                details += f"- {item['description']}: {item['quantity']} × ₹{item['rate']:.2f} = ₹{item['amount']:.2f}\n"
            
            messagebox.showinfo("Invoice Details", details)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load invoice details: {str(e)}")
    
    def generate_report(self):
        """Generate report based on filters"""
        report_type = self.report_type.get()
        from_date = self.report_from_date.get_date().strftime('%Y-%m-%d')
        to_date = self.report_to_date.get_date().strftime('%Y-%m-%d')
        
        try:
            if report_type == "SALES":
                report_data = self.db.get_sales_report(from_date, to_date)
                self.display_sales_report(report_data, from_date, to_date)
            elif report_type == "PURCHASE":
                report_data = self.db.get_purchase_report(from_date, to_date)
                self.display_purchase_report(report_data, from_date, to_date)
            elif report_type == "STOCK":
                report_data = self.db.get_stock_report()
                self.display_stock_report(report_data)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def display_sales_report(self, report_data, from_date, to_date):
        """Display sales report"""
        self.report_text.delete('1.0', tk.END)
        
        self.report_text.insert(tk.END, f"SALES REPORT\n", 'header')
        self.report_text.insert(tk.END, f"Period: {from_date} to {to_date}\n\n")
        
        total_sales = 0
        total_items = 0
        
        for item in report_data:
            self.report_text.insert(tk.END, 
                f"{item['date']} - {item['invoice_number']} - {item.get('client_name', 'Walk-in')} - ₹{item['total_amount']:.2f}\n")
            total_sales += item['total_amount']
            total_items += 1
        
        self.report_text.insert(tk.END, f"\nTotal Sales: ₹{total_sales:.2f}\n")
        self.report_text.insert(tk.END, f"Total Invoices: {total_items}\n")
    
    def display_purchase_report(self, report_data, from_date, to_date):
        """Display purchase report"""
        self.report_text.delete('1.0', tk.END)
        
        self.report_text.insert(tk.END, f"PURCHASE REPORT\n", 'header')
        self.report_text.insert(tk.END, f"Period: {from_date} to {to_date}\n\n")
        
        total_purchases = 0
        total_items = 0
        
        for item in report_data:
            self.report_text.insert(tk.END, 
                f"{item['date']} - {item['invoice_number']} - ₹{item['total_amount']:.2f}\n")
            total_purchases += item['total_amount']
            total_items += 1
        
        self.report_text.insert(tk.END, f"\nTotal Purchases: ₹{total_purchases:.2f}\n")
        self.report_text.insert(tk.END, f"Total Invoices: {total_items}\n")
    
    def display_stock_report(self, report_data):
        """Display stock report"""
        self.report_text.delete('1.0', tk.END)
        
        self.report_text.insert(tk.END, "STOCK REPORT\n", 'header')
        self.report_text.insert(tk.END, f"As of: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        low_stock_count = 0
        total_value = 0
        
        for item in report_data:
            status = "LOW" if item['current_stock'] < 10 else "OK"
            if status == "LOW":
                low_stock_count += 1
            
            item_value = item['current_stock'] * item['rate']
            total_value += item_value
            
            self.report_text.insert(tk.END, 
                f"{item['name']}: {item['current_stock']} ({status}) - ₹{item_value:.2f}\n")
        
        self.report_text.insert(tk.END, f"\nTotal Stock Value: ₹{total_value:.2f}\n")
        self.report_text.insert(tk.END, f"Low Stock Items: {low_stock_count}\n")
    
    def export_report(self):
        """Export current report to PDF"""
        report_text = self.report_text.get('1.0', tk.END).strip()
        if not report_text:
            messagebox.showwarning("Warning", "No report to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.pdf_generator.generate_report_pdf(report_text, filename)
                messagebox.showinfo("Success", f"Report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
    def save_company_settings(self):
        """Save company settings"""
        company_name = self.setting_company_name.get().strip()
        company_address = self.setting_company_address.get('1.0', tk.END).strip()
        company_gst = self.setting_company_gst.get().strip()
        company_phone = self.setting_company_phone.get().strip()
        
        if not company_name:
            messagebox.showerror("Error", "Company name is required")
            return
        
        try:
            # Save to config or database
            config.COMPANY_NAME = company_name
            config.COMPANY_ADDRESS = company_address
            config.COMPANY_GST = company_gst
            config.COMPANY_PHONE = company_phone
            
            # Update the main window title if needed
            self.root.title(f"{company_name} - Billing Software")
            
            messagebox.showinfo("Success", "Company settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def save_app_settings(self):
        """Save application settings"""
        try:
            printer_width = int(self.setting_printer_width.get().strip())
            if printer_width <= 0:
                messagebox.showerror("Error", "Printer width must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid printer width")
            return
        
        config.ALLOW_NEGATIVE_STOCK = self.setting_negative_stock.get()
        config.THERMAL_PRINTER_WIDTH = printer_width
        
        messagebox.showinfo("Success", "Application settings saved successfully")
    
    def backup_database(self):
        """Backup database"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.db.backup_database(filename)
                messagebox.showinfo("Success", f"Database backed up to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to backup database: {str(e)}")
    
    def restore_database(self):
        """Restore database from backup"""
        if not messagebox.askyesno("Confirm", "This will replace current database. Continue?"):
            return
        
        filename = filedialog.askopenfilename(
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.db.restore_database(filename)
                messagebox.showinfo("Success", "Database restored successfully")
                # Reload all data
                self.load_products()
                self.load_clients()
                self.load_recent_invoices()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore database: {str(e)}")
    
    def optimize_database(self):
        """Optimize database"""
        try:
            self.db.optimize_database()
            messagebox.showinfo("Success", "Database optimized successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to optimize database: {str(e)}")
    
    def count_low_stock_items(self):
        """Count low stock items"""
        try:
            products = self.get_products_safe()
            return sum(1 for p in products if p['current_stock'] < 10)
        except:
            return 0
    
    def get_today_sales(self):
        """Get today's sales total"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            if hasattr(self.db, 'get_daily_sales'):
                return self.db.get_daily_sales(today)
            else:
                result = self.db.fetch_one(
                    "SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE date = %s AND type = 'SALE'",
                    (today,)
                )
                return result[0] if result else 0
        except:
            return 0

# Configure text tags for reports
def configure_text_tags(report_text):
    report_text.tag_configure('header', font=('Arial', 12, 'bold'), justify='center')

# Main application
def main():
    root = tk.Tk()
    root.title(f"{config.COMPANY_NAME} - Billing Software")
    root.geometry("1200x800")
    
    # Initialize database
    db = Database(config.DATABASE_NAME)
    
    # Create main UI
    app = MainUI(root, db, config.COMPANY_NAME)
    
    # Configure report text tags
    configure_text_tags(app.report_text)
    
    root.mainloop()

if __name__ == "__main__":
    main()