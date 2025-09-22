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
        self.root.title(f"{self.company_name} - Billing Software")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # Start maximized

        # Apply theme
        self.set_theme()
        
        # Create menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New Bill", command=self.new_bill)
        self.file_menu.add_command(label="Print Bill", command=self.print_bill)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Dashboard", command=self.show_dashboard)
        self.view_menu.add_command(label="Billing", command=self.show_billing)
        self.view_menu.add_command(label="Products", command=self.show_products)
        self.view_menu.add_command(label="Reports", command=self.show_reports)
        self.view_menu.add_command(label="Settings", command=self.show_settings)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.billing_tab = ttk.Frame(self.notebook)
        self.products_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_tab, text="📊 Dashboard")
        self.notebook.add(self.billing_tab, text="🧾 Billing")
        self.notebook.add(self.products_tab, text="📦 Products")
        self.notebook.add(self.reports_tab, text="📈 Reports")
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Setup each tab (define these methods below)
        self.setup_dashboard_tab()
        self.setup_billing_tab()  # You need to add this method
        self.setup_products_tab()
        self.setup_reports_tab()
        self.setup_settings_tab()
        self.bill_counter = 1001
        self.load_bill_counter()
        self.setup_ui()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize variables
        self.current_bill_items = []
        self.bill_counter = self.get_last_bill_number() + 1
        
        # Set focus to first tab
        self.notebook.select(0)
        
        # Update status
        self.update_status("Application started successfully")

    def setup_billing_tab(self):
        """Setup the Billing tab"""
        # Main frame
        main_frame = ttk.Frame(self.billing_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame for product selection
        left_frame = ttk.LabelFrame(main_frame, text="Product Selection", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right frame for bill details
        right_frame = ttk.LabelFrame(main_frame, text="Bill Details", padding=10, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # Product search
        ttk.Label(left_frame, text="Search Product:").pack(anchor=tk.W)
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        search_entry.bind('<KeyRelease>', self.search_products)
        
        ttk.Button(search_frame, text="Search", command=self.search_products).pack(side=tk.RIGHT)
        
        # Products treeview
        product_columns = ("ID", "Name", "Price", "Stock")
        self.products_tree = ttk.Treeview(left_frame, columns=product_columns, show='headings', height=15)
        
        for col in product_columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=80)
        
        # Bind double click to add product to bill
        self.products_tree.bind('<Double-1>', self.add_to_bill)
        
        # Scrollbar for products
        product_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=product_scrollbar.set)
        
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        product_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bill details
        # Bill number
        bill_frame = ttk.Frame(right_frame)
        bill_frame.pack(fill=tk.X, pady=5)
        ttk.Label(bill_frame, text="Bill #:").pack(side=tk.LEFT)
        self.bill_number_var = tk.StringVar(value=str(self.bill_counter))
        ttk.Label(bill_frame, textvariable=self.bill_number_var, font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Bill items treeview
        bill_columns = ("Product", "Qty", "Price", "Total")
        self.bill_tree = ttk.Treeview(right_frame, columns=bill_columns, show='headings', height=10)
        
        for col in bill_columns:
            self.bill_tree.heading(col, text=col)
            self.bill_tree.column(col, width=80)
        
        # Scrollbar for bill items
        bill_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.bill_tree.yview)
        self.bill_tree.configure(yscrollcommand=bill_scrollbar.set)
        
        self.bill_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        bill_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Total amount
        total_frame = ttk.Frame(right_frame)
        total_frame.pack(fill=tk.X, pady=5)
        ttk.Label(total_frame, text="Total:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        self.total_var = tk.StringVar(value="₹0.00")
        ttk.Label(total_frame, textvariable=self.total_var, font=('Arial', 12, 'bold')).pack(side=tk.RIGHT)
        
        # Action buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="New Bill", command=self.new_bill).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Print Bill", command=self.print_bill).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save Bill", command=self.save_bill).pack(side=tk.LEFT, padx=2)
        
        # Load initial products
        self.load_products_for_billing()

    def load_products_for_billing(self):
        """Load products for billing tab"""
        try:
            # Clear existing items
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            # Get products from database
            products = self.db.get_products()
            
            for product in products:
                self.products_tree.insert("", tk.END, values=(
                    product[0],  # ID
                    product[1],  # Name
                    f"₹{product[2]:.2f}",  # Price
                    product[3]   # Stock
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")

    def search_products(self, event=None):
        """Search products based on input"""
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        try:
            products = self.db.get_products()
            
            for product in products:
                if search_term in product[1].lower() or search_term in str(product[0]).lower():
                    self.products_tree.insert("", tk.END, values=(
                        product[0],  # ID
                        product[1],  # Name
                        f"₹{product[2]:.2f}",  # Price
                        product[3]   # Stock
                    ))
                    
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def add_to_bill(self, event):
        """Add selected product to bill"""
        selected_item = self.products_tree.selection()
        if not selected_item:
            return
        
        item = self.products_tree.item(selected_item[0])
        product_id, product_name, price_str, stock = item['values']
        
        # Extract numeric price
        price = float(price_str.replace('₹', ''))
        
        # Ask for quantity
        quantity = simpledialog.askinteger("Quantity", f"Enter quantity for {product_name}:", 
                                        minvalue=1, maxvalue=int(stock))
        
        if quantity:
            total = price * quantity
            self.bill_tree.insert("", tk.END, values=(
                product_name, quantity, f"₹{price:.2f}", f"₹{total:.2f}"
            ))
            
            # Add to current bill items
            self.current_bill_items.append({
                'product_id': product_id,
                'name': product_name,
                'quantity': quantity,
                'price': price,
                'total': total
            })
            
            # Update total
            self.update_bill_total()

    def update_bill_total(self):
        """Update the total amount of the bill"""
        total = sum(item['total'] for item in self.current_bill_items)
        self.total_var.set(f"₹{total:.2f}")

    def save_bill(self):
        """Save bill to database"""
        if not self.current_bill_items:
            messagebox.showwarning("Warning", "No items in the bill!")
            return
        
        try:
            total_amount = sum(item['total'] for item in self.current_bill_items)
            
            # Save bill header
            bill_query = """
            INSERT INTO bills (bill_number, total_amount, created_at)
            VALUES (%s, %s, NOW())
            """
            self.db.cursor.execute(bill_query, (self.bill_counter, total_amount))
            
            # Get the bill ID
            bill_id = self.db.cursor.lastrowid
            
            # Save bill items
            for item in self.current_bill_items:
                item_query = """
                INSERT INTO bill_items (bill_id, product_id, quantity, price, total)
                VALUES (%s, %s, %s, %s, %s)
                """
                self.db.cursor.execute(item_query, (
                    bill_id, item['product_id'], item['quantity'], 
                    item['price'], item['total']
                ))
                
                # Update product stock
                update_stock_query = """
                UPDATE products SET stock_quantity = stock_quantity - %s 
                WHERE product_id = %s
                """
                self.db.cursor.execute(update_stock_query, (item['quantity'], item['product_id']))
            
            self.db.conn.commit()
            messagebox.showinfo("Success", f"Bill #{self.bill_counter} saved successfully!")
            self.new_bill()
            
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Failed to save bill: {str(e)}")

    def set_theme(self):
        """Set the application theme"""
        try:
            # Try to use a modern theme if available
            self.root.tk.call("source", "azure.tcl")
            self.root.tk.call("set_theme", "light")
        except:
            # Fallback to default theme
            style = ttk.Style()
            style.theme_use('clam')

    def new_bill(self):
        """Create a new bill"""
        self.current_bill_items = []
        self.bill_counter += 1
        self.update_status("New bill created")

    def print_bill(self):
        """Print current bill"""
        messagebox.showinfo("Print", "Print functionality will be implemented")

    def show_dashboard(self):
        """Show dashboard tab"""
        self.notebook.select(0)

    def show_billing(self):
        """Show billing tab"""
        self.notebook.select(1)

    def show_products(self):
        """Show products tab"""
        self.notebook.select(2)

    def show_reports(self):
        """Show reports tab"""
        self.notebook.select(3)

    def show_settings(self):
        """Show settings tab"""
        self.notebook.select(4)

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", f"{self.company_name} Billing Software\nVersion 1.0")

    def on_tab_changed(self, event):
        """Handle tab change events"""
        tab_index = self.notebook.index(self.notebook.select())
        tab_names = ["Dashboard", "Billing", "Products", "Reports", "Settings"]
        self.update_status(f"Viewing {tab_names[tab_index]} tab")

    def get_last_bill_number(self):
        """Get the last bill number from database"""
        try:
            self.db.cursor.execute("SELECT MAX(bill_number) FROM bills")
            result = self.db.cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except:
            return 0

    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def get_products(self):
        """Get all products from database"""
        query = "SELECT product_id, name, price, stock_quantity, category FROM products ORDER BY name"
        self.cursor.execute(query)
        return self.cursor.fetchall()
        
    def setup_dashboard_tab(self):
        try:
            # Check if dashboard widgets exist before using them
            if not hasattr(self, 'dashboard_items_label'):
                print("Dashboard widgets not initialized yet")
                return
                
            total_items = self.db.get_total_items()
            total_clients = self.db.get_total_clients()
            total_sales = self.db.get_total_sales()
            
            # Add error handling for these method calls
            try:
                low_stock = self.count_low_stock_items()
            except Exception as e:
                print(f"Error counting low stock items: {e}")
                low_stock = 0
                
            try:
                today_sales = self.get_today_sales()
            except Exception as e:
                print(f"Error getting today's sales: {e}")
                today_sales = 0
            
            # Update dashboard labels with the values
            self.dashboard_items_label.setText(f"Total Items: {total_items}")
            self.dashboard_clients_label.setText(f"Total Clients: {total_clients}")
            self.dashboard_sales_label.setText(f"Total Sales: ₹{total_sales:,.2f}")
            self.dashboard_low_stock_label.setText(f"Low Stock Items: {low_stock}")
            self.dashboard_today_sales_label.setText(f"Today's Sales: ₹{today_sales:,.2f}")
            
        except Exception as e:
            print(f"Error setting up dashboard: {e}")
            # Only set text if the labels exist
            if hasattr(self, 'dashboard_items_label'):
                self.dashboard_items_label.setText("Total Items: Error")
            if hasattr(self, 'dashboard_clients_label'):
                self.dashboard_clients_label.setText("Total Clients: Error")
            if hasattr(self, 'dashboard_sales_label'):
                self.dashboard_sales_label.setText("Total Sales: Error")
            if hasattr(self, 'dashboard_low_stock_label'):
                self.dashboard_low_stock_label.setText("Low Stock Items: Error")
            if hasattr(self, 'dashboard_today_sales_label'):
                self.dashboard_today_sales_label.setText("Today's Sales: Error")
            
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

    def setup_barcode_scanner(self):
        """Setup barcode scanner with fallback"""
        try:
            from pyzbar.pyzbar import decode
            self.has_barcode_scanner = True
            print("Barcode scanner initialized successfully")
        except ImportError as e:
            print(f"Barcode scanner not available: {e}")
            self.has_barcode_scanner = False
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

    def verify_database_schema(self):
        """Verify that required database tables and columns exist"""
        required_tables = ['items', 'clients', 'invoices', 'invoice_items']
        required_columns = {
            'clients': ['id', 'name', 'phone', 'gst_number'],
            'items': ['id', 'name', 'quantity', 'min_stock', 'price'],
            'invoices': ['id', 'client_id', 'date', 'total_amount', 'type']
        }
        
        cursor = self.db.conn.cursor()
        
        for table in required_tables:
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)", (table,))
            if not cursor.fetchone()[0]:
                print(f"Warning: Table '{table}' does not exist in database")
        
        for table, columns in required_columns.items():
            for column in columns:
                cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = %s AND column_name = %s)", 
                            (table, column))
                if not cursor.fetchone()[0]:
                    print(f"Warning: Column '{column}' does not exist in table '{table}'")
        
        cursor.close()

    def get_today_sales(self):
        """Get today's sales total"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE date = %s AND type = 'SALE'", (today,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error getting today's sales: {e}")
            return 0
    
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
        """Create the purchases (stock in) tab"""
        self.purchases_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.purchases_tab, text='purchases')
        
        # Top frame for client selection
        client_frame = ttk.LabelFrame(self.purchases_tab, text="Client Selection")
        client_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(client_frame, text="Select Client:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.sale_client = tk.StringVar()
        clients = [c['name'] for c in self.get_clients_safe()]
        self.client_combo = ttk.Combobox(client_frame, textvariable=self.sale_client, values=clients, state="readonly")
        self.client_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Button(client_frame, text="New Client", command=self.add_client_from_purchases).grid(row=0, column=2, padx=5, pady=5)
        
        # Product selection frame
        product_frame = ttk.LabelFrame(self.purchases_tab, text="Add Product to Invoice")
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
        items_frame = ttk.LabelFrame(self.purchases_tab, text="Invoice Items")
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
        total_frame = ttk.Frame(self.purchases_tab)
        total_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(total_frame, text="Total Amount:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.total_amount = ttk.Label(total_frame, text="0.00", font=("Arial", 10, "bold"))
        self.total_amount.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = ttk.Frame(self.purchases_tab)
        action_frame.pack(pady=10)
        
        ttk.Button(action_frame, text="Remove Selected", command=self.remove_invoice_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Clear Invoice", command=self.clear_invoice).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Generate Invoice", command=self.generate_sale_invoice).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Print Receipt", command=self.print_receipt).pack(side=tk.LEFT, padx=5)
        
        # Initialize invoice items list
        self.invoice_items = []

    def load_products_data(self):
        """Load products data into the treeview"""
        # Clear existing data
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        try:
            # Fetch products from database
            products = self.db.get_products()
            
            # Insert products into treeview
            for product in products:
                self.products_tree.insert("", tk.END, values=product)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")

    def add_product(self):
        """Placeholder for add product functionality"""
        messagebox.showinfo("Info", "Add product functionality will be implemented here")

    def edit_product(self):
        """Placeholder for edit product functionality"""
        messagebox.showinfo("Info", "Edit product functionality will be implemented here")

    def delete_product(self):
        """Placeholder for delete product functionality"""
        messagebox.showinfo("Info", "Delete product functionality will be implemented here")

    def setup_products_tab(self):
        """Setup the Products/Inventory tab"""
        # Main frame
        main_frame = ttk.Frame(self.products_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame for treeview
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right frame for controls
        right_frame = ttk.Frame(main_frame, width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # Create treeview
        columns = ("ID", "Name", "Price", "Stock", "Category")
        self.products_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=20)
        
        # Set column headings
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add control buttons
        ttk.Button(right_frame, text="Add Product", command=self.add_product).pack(pady=5, fill=tk.X)
        ttk.Button(right_frame, text="Edit Product", command=self.edit_product).pack(pady=5, fill=tk.X)
        ttk.Button(right_frame, text="Delete Product", command=self.delete_product).pack(pady=5, fill=tk.X)
        ttk.Button(right_frame, text="Refresh", command=self.load_products_data).pack(pady=5, fill=tk.X)
        
        # Load initial data
        self.load_products_data()
    
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
        try:
            cursor = self.db.conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clients")
            clients = cursor.fetchall()
            cursor.close()
            
            # Clear existing items in the treeview
            for item in self.clients_tree.get_children():
                self.clients_tree.delete(item)
            
            # Insert clients into treeview with safe field access
            for client in clients:
                self.clients_tree.insert("", "end", values=(
                    client['id'],
                    client.get('name', ''),
                    client.get('phone', ''),
                    client.get('email', ''),
                    client.get('gst_number', '') or '',
                    client.get('address', '')
                ))
                
        except Exception as e:
            print(f"Error loading clients: {e}")
            # Show error message to user if needed
    
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

    def add_client_from_purchases(self):
        """Open client form from purchases tab"""
        self.notebook.select(self.clients_tab)

    def count_low_stock_items(self):
        """Placeholder method if you don't have stock management"""
        return 0  # Return 0 since you're not tracking stock
    
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
        """Count items with low stock (assuming you have a stock_quantity column)"""
        try:
            cursor = self.db.conn.cursor()
            # Make sure your database has the correct column names
            cursor.execute("SELECT COUNT(*) FROM items WHERE quantity <= min_stock AND quantity > 0")
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error counting low stock items: {e}")
            return 0
        
    def count_clients(self):
        """Count total clients"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            print(f"Error counting clients: {e}")
            return 0
        
    def create_dashboard_widgets(self):
        """Create dashboard widgets"""
        # Make sure dashboard_frame exists
        if not hasattr(self, 'dashboard_frame'):
            print("Creating dashboard frame...")
            self.dashboard_frame = ttk.Frame(self.dashboard_tab)
            self.dashboard_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Dashboard labels
        self.dashboard_items_label = ttk.Label(self.dashboard_frame, text="Total Items: Loading...", font=('Arial', 12))
        self.dashboard_items_label.pack(pady=10, anchor='w')
        
        self.dashboard_clients_label = ttk.Label(self.dashboard_frame, text="Total Clients: Loading...", font=('Arial', 12))
        self.dashboard_clients_label.pack(pady=10, anchor='w')
        
        self.dashboard_sales_label = ttk.Label(self.dashboard_frame, text="Total Sales: Loading...", font=('Arial', 12))
        self.dashboard_sales_label.pack(pady=10, anchor='w')
        
        self.dashboard_low_stock_label = ttk.Label(self.dashboard_frame, text="Low Stock Items: Loading...", font=('Arial', 12))
        self.dashboard_low_stock_label.pack(pady=10, anchor='w')
        
        self.dashboard_today_sales_label = ttk.Label(self.dashboard_frame, text="Today's Sales: Loading...", font=('Arial', 12))
        self.dashboard_today_sales_label.pack(pady=10, anchor='w')
        
        print("Dashboard widgets created successfully")

    def count_invoices(self):
        """Count total invoices"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM invoices")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            print(f"Error counting invoices: {e}")
            return 0
        
    def setup_items_tab(self):
        """Setup items/products tab"""
        print("Setting up items tab...")
        
        # Items frame
        self.items_frame = ttk.Frame(self.items_tab)
        self.items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Search frame
        search_frame = ttk.Frame(self.items_frame)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.item_search_var = tk.StringVar()
        self.item_search_entry = ttk.Entry(search_frame, textvariable=self.item_search_var, width=30)
        self.item_search_entry.pack(side='left', padx=5)
        self.item_search_entry.bind('<KeyRelease>', self.search_items)
        
        # Items treeview
        columns = ('id', 'name', 'quantity', 'min_stock', 'price', 'category')
        self.items_tree = ttk.Treeview(self.items_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.items_tree.heading('id', text='ID')
        self.items_tree.heading('name', text='Name')
        self.items_tree.heading('quantity', text='Quantity')
        self.items_tree.heading('min_stock', text='Min Stock')
        self.items_tree.heading('price', text='Price')
        self.items_tree.heading('category', text='Category')
        
        # Define columns
        self.items_tree.column('id', width=50, anchor='center')
        self.items_tree.column('name', width=200, anchor='w')
        self.items_tree.column('quantity', width=80, anchor='center')
        self.items_tree.column('min_stock', width=80, anchor='center')
        self.items_tree.column('price', width=80, anchor='e')
        self.items_tree.column('category', width=100, anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.items_frame, orient='vertical', command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons frame
        button_frame = ttk.Frame(self.items_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Add Item", command=self.add_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit Item", command=self.edit_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Item", command=self.delete_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.load_items).pack(side='left', padx=5)
        
        # Load items
        self.load_items()
    
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
        
    def setup_ui(self):
        """Setup main UI components"""
        self.root.title(f"{self.company_name} - Billing Software")
        self.root.geometry("1200x800")
        
        # Create notebook (tab control)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.items_tab = ttk.Frame(self.notebook)
        self.clients_tab = ttk.Frame(self.notebook)
        self.invoices_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_tab, text='Dashboard')
        self.notebook.add(self.items_tab, text='Items')
        self.notebook.add(self.clients_tab, text='Clients')
        self.notebook.add(self.invoices_tab, text='Invoices')
        self.notebook.add(self.reports_tab, text='Reports')
        
        print("UI setup completed")

    def load_bill_counter(self):
        # Example code to load the last bill number from database
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT MAX(bill_number) FROM bills")
            result = cursor.fetchone()
            self.bill_counter = result[0] + 1 if result[0] else 1001
        except:
            # Fallback if there's any error
            self.bill_counter = 1001

    def search_items(self, event=None):
        """Search items based on query"""
        query = self.item_search_var.get().lower()
        if not query:
            self.load_items()
            return
        
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT id, name, quantity, min_stock, price, category 
                FROM items 
                WHERE LOWER(name) LIKE %s OR LOWER(category) LIKE %s
            """, (f'%{query}%', f'%{query}%'))
            
            items = cursor.fetchall()
            cursor.close()
            
            # Clear treeview
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            # Add filtered items
            for item in items:
                self.items_tree.insert('', 'end', values=item)
                
        except Exception as e:
            print(f"Error searching items: {e}")

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