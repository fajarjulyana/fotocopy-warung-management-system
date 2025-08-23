
import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate database to add missing columns"""
    db_path = "instance/integrated_business_app.db"
    
    # Backup database
    if os.path.exists(db_path):
        backup_path = f"instance/integrated_business_app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if products table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Get current columns
            cursor.execute("PRAGMA table_info(products)")
            existing_columns = [column[1] for column in cursor.fetchall()]
            print(f"Existing columns: {existing_columns}")
            
            # List of ALL required columns with their definitions
            required_columns = {
                'category': 'TEXT DEFAULT "Lainnya"',
                'brand': 'TEXT',
                'supplier': 'TEXT',
                'barcode': 'TEXT UNIQUE',
                'qr_code': 'TEXT UNIQUE',
                'purchase_price': 'REAL NOT NULL DEFAULT 0',
                'selling_price': 'REAL NOT NULL DEFAULT 0',
                'initial_stock': 'INTEGER NOT NULL DEFAULT 0',
                'current_stock': 'INTEGER NOT NULL DEFAULT 0',
                'minimum_stock': 'INTEGER NOT NULL DEFAULT 5',
                'maximum_stock': 'INTEGER NOT NULL DEFAULT 1000',
                'unit': 'TEXT DEFAULT "pcs"',
                'weight': 'REAL DEFAULT 0',
                'dimensions': 'TEXT',
                'expiry_date': 'DATE',
                'profit': 'REAL NOT NULL DEFAULT 0',
                'total_sold': 'INTEGER NOT NULL DEFAULT 0',
                'total_revenue': 'REAL NOT NULL DEFAULT 0',
                'is_active': 'BOOLEAN DEFAULT 1',
                'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
            }
            
            # Add missing columns
            for column, definition in required_columns.items():
                if column not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE products ADD COLUMN {column} {definition}")
                        print(f"Added column: {column}")
                    except sqlite3.OperationalError as e:
                        print(f"Error adding column {column}: {e}")
            
            # Update existing records with default values
            cursor.execute("""
                UPDATE products 
                SET category = COALESCE(category, 'Lainnya'),
                    brand = COALESCE(brand, ''),
                    supplier = COALESCE(supplier, ''),
                    unit = COALESCE(unit, 'pcs'),
                    weight = COALESCE(weight, 0),
                    minimum_stock = COALESCE(minimum_stock, 5),
                    maximum_stock = COALESCE(maximum_stock, 1000),
                    profit = COALESCE(profit, 0),
                    total_sold = COALESCE(total_sold, 0),
                    total_revenue = COALESCE(total_revenue, 0),
                    is_active = COALESCE(is_active, 1),
                    created_at = COALESCE(created_at, datetime('now')),
                    updated_at = COALESCE(updated_at, datetime('now'))
            """)
            
        else:
            # Create products table from scratch with all columns
            cursor.execute("""
                CREATE TABLE products (
                    id TEXT PRIMARY KEY CHECK(length(id) <= 50),
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'Lainnya',
                    brand TEXT,
                    supplier TEXT,
                    barcode TEXT UNIQUE,
                    qr_code TEXT UNIQUE,
                    purchase_price REAL NOT NULL DEFAULT 0,
                    selling_price REAL NOT NULL DEFAULT 0,
                    initial_stock INTEGER NOT NULL DEFAULT 0,
                    current_stock INTEGER NOT NULL DEFAULT 0,
                    minimum_stock INTEGER NOT NULL DEFAULT 5,
                    maximum_stock INTEGER NOT NULL DEFAULT 1000,
                    unit TEXT DEFAULT 'pcs',
                    weight REAL DEFAULT 0,
                    dimensions TEXT,
                    expiry_date DATE,
                    profit REAL NOT NULL DEFAULT 0,
                    total_sold INTEGER NOT NULL DEFAULT 0,
                    total_revenue REAL NOT NULL DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Created products table with all columns")
        
        # Check and create other required tables
        tables_to_check = [
            ('users', """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'cashier',
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """),
            ('business_settings', """
                CREATE TABLE business_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_name TEXT NOT NULL DEFAULT 'Business App by fajarmandiri.store',
                    address TEXT,
                    phone TEXT,
                    website TEXT DEFAULT 'fajarmandiri.store',
                    copyright_text TEXT DEFAULT '© 2025 Fajar Julyana - fajarmandiri.store',
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_by INTEGER,
                    FOREIGN KEY (updated_by) REFERENCES users (id)
                )
            """),
            ('customers', """
                CREATE TABLE customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """),
            ('customer_debts', """
                CREATE TABLE customer_debts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    invoice_number TEXT,
                    description TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    paid_amount REAL DEFAULT 0.0,
                    remaining_amount REAL NOT NULL,
                    due_date DATE,
                    status TEXT DEFAULT 'active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    FOREIGN KEY (customer_id) REFERENCES customers (id),
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            """),
            ('debt_payments', """
                CREATE TABLE debt_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debt_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_date DATE NOT NULL,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    FOREIGN KEY (debt_id) REFERENCES customer_debts (id),
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            """),
            ('material_costs', """
                CREATE TABLE material_costs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """),
            ('service_costs', """
                CREATE TABLE service_costs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    hours REAL NOT NULL,
                    hourly_rate REAL NOT NULL,
                    total_cost REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """),
            ('maintenance_costs', """
                CREATE TABLE maintenance_costs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    maintenance_type TEXT NOT NULL,
                    frequency TEXT NOT NULL,
                    cost_per_occurrence REAL NOT NULL,
                    annual_cost REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """),
            ('inventory_items', """
                CREATE TABLE inventory_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    code TEXT UNIQUE NOT NULL,
                    purchase_price REAL NOT NULL DEFAULT 0,
                    selling_price REAL NOT NULL DEFAULT 0,
                    initial_stock INTEGER NOT NULL DEFAULT 0,
                    current_stock INTEGER NOT NULL DEFAULT 0,
                    minimum_stock INTEGER NOT NULL DEFAULT 5,
                    profit REAL NOT NULL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """),
            ('savers', """
                CREATE TABLE savers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    address TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """),
            ('savings_transactions', """
                CREATE TABLE savings_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    saver_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    amount REAL NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    balance_after REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (saver_id) REFERENCES savers (id)
                )
            """),
            ('cashier_transactions', """
                CREATE TABLE cashier_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    items TEXT NOT NULL,
                    total REAL NOT NULL,
                    profit REAL NOT NULL,
                    payment_amount REAL NOT NULL,
                    change_amount REAL NOT NULL,
                    cashier_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cashier_id) REFERENCES users (id)
                )
            """),
            ('invoices', """
                CREATE TABLE invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE NOT NULL,
                    client_name TEXT NOT NULL,
                    client_email TEXT,
                    client_phone TEXT,
                    client_address TEXT,
                    service_date DATE NOT NULL,
                    issue_date DATE NOT NULL,
                    due_date DATE NOT NULL,
                    status TEXT DEFAULT 'draft',
                    notes TEXT,
                    subtotal REAL DEFAULT 0.0,
                    tax_rate REAL DEFAULT 0.0,
                    tax_amount REAL DEFAULT 0.0,
                    total REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """),
            ('service_items', """
                CREATE TABLE service_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    rate REAL NOT NULL,
                    amount REAL NOT NULL,
                    FOREIGN KEY (invoice_id) REFERENCES invoices (id)
                )
            """)
        ]
        
        for table_name, create_sql in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                cursor.execute(create_sql)
                print(f"Created table: {table_name}")
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Ensure instance directory exists
    os.makedirs("instance", exist_ok=True)
    migrate_database()
