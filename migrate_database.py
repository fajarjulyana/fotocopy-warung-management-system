
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
            
            # List of required columns with their definitions
            required_columns = {
                'barcode': 'TEXT',
                'qr_code': 'TEXT',
                'purchase_price': 'REAL NOT NULL DEFAULT 0',
                'selling_price': 'REAL NOT NULL DEFAULT 0',
                'initial_stock': 'INTEGER NOT NULL DEFAULT 0',
                'current_stock': 'INTEGER NOT NULL DEFAULT 0',
                'profit': 'REAL NOT NULL DEFAULT 0',
                'created_at': 'DATETIME',
                'updated_at': 'DATETIME'
            }
            
            # Add missing columns
            for column, definition in required_columns.items():
                if column not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE products ADD COLUMN {column} {definition}")
                        print(f"Added column: {column}")
                    except sqlite3.OperationalError as e:
                        print(f"Error adding column {column}: {e}")
            
            # Update timestamps for existing records
            cursor.execute("""
                UPDATE products 
                SET created_at = datetime('now'), updated_at = datetime('now') 
                WHERE created_at IS NULL OR updated_at IS NULL
            """)
            
        else:
            # Create products table from scratch
            cursor.execute("""
                CREATE TABLE products (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    barcode TEXT UNIQUE,
                    qr_code TEXT UNIQUE,
                    purchase_price REAL NOT NULL DEFAULT 0,
                    selling_price REAL NOT NULL DEFAULT 0,
                    initial_stock INTEGER NOT NULL DEFAULT 0,
                    current_stock INTEGER NOT NULL DEFAULT 0,
                    profit REAL NOT NULL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Created products table")
        
        # Check and create other required tables
        tables_to_check = [
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
