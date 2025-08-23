
import os
import logging
import sqlite3
from datetime import datetime
import base64
import io
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from werkzeug.middleware.proxy_fix import ProxyFix

# Import barcode and QR code libraries
try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from barcode import Code128
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database file path
DATABASE_PATH = 'databases.db'

# Transaction data will still be stored in memory for simplicity
transactions_data = []
next_transaction_id = 1

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    
    # Create barang table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS barang (
            id TEXT PRIMARY KEY,
            kode TEXT,
            nama TEXT,
            harga_awal INTEGER,
            harga_jual INTEGER,
            stok_awal INTEGER,
            stok_akhir INTEGER,
            profit INTEGER
        )
    ''')
    
    # Create transactions table for future use
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            items TEXT,
            total INTEGER,
            profit INTEGER,
            payment_amount INTEGER,
            change_amount INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def initialize_sample_data():
    """Initialize some sample items for testing"""
    conn = get_db_connection()
    
    # Check if data already exists
    existing_items = conn.execute('SELECT COUNT(*) FROM barang').fetchone()[0]
    
    if existing_items == 0:  # Only add if no data exists
        sample_items = [
            ('BRG001', 'BRG001', 'Buku Tulis', 3000, 5000, 50, 50, 0),
            ('BRG002', 'BRG002', 'Pulpen', 2000, 3500, 100, 100, 0),
            ('BRG003', 'BRG003', 'Penggaris', 5000, 8000, 30, 30, 0)
        ]
        
        conn.executemany('''
            INSERT INTO barang (id, kode, nama, harga_awal, harga_jual, stok_awal, stok_akhir, profit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_items)
        
        conn.commit()
    
    conn.close()
    
    # Add sample transactions for testing
    global next_transaction_id, transactions_data
    if not transactions_data:  # Only add if no transactions exist
        sample_transactions = [
            {
                'id': 1,
                'timestamp': '2025-08-03 14:30:15',
                'items': [
                    {
                        'kode': 'BRG001',
                        'nama': 'Buku Tulis',
                        'harga_awal': 3000,
                        'harga_jual': 5000,
                        'quantity': 2,
                        'subtotal': 10000
                    },
                    {
                        'kode': 'BRG002',
                        'nama': 'Pulpen',
                        'harga_awal': 2000,
                        'harga_jual': 3500,
                        'quantity': 3,
                        'subtotal': 10500
                    }
                ],
                'total': 20500,
                'profit': 8500,
                'payment_amount': 25000,
                'change': 4500
            },
            {
                'id': 2,
                'timestamp': '2025-08-03 15:15:22',
                'items': [
                    {
                        'kode': 'BRG003',
                        'nama': 'Penggaris',
                        'harga_awal': 5000,
                        'harga_jual': 8000,
                        'quantity': 1,
                        'subtotal': 8000
                    }
                ],
                'total': 8000,
                'profit': 3000,
                'payment_amount': 10000,
                'change': 2000
            }
        ]
        
        transactions_data.extend(sample_transactions)
        next_transaction_id = 3

# Initialize database and sample data when app starts
init_database()
initialize_sample_data()

# Sample admin credentials (in production, use proper authentication)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def calculate_profit(harga_awal, harga_jual, quantity=1):
    """Calculate profit from selling items"""
    return (harga_jual - harga_awal) * quantity

def calculate_total_profit(harga_awal, harga_jual, stok_awal, stok_akhir):
    """Calculate total profit based on items sold"""
    items_sold = stok_awal - stok_akhir
    return (harga_jual - harga_awal) * items_sold

def get_item_by_code(kode):
    """Get item by its code"""
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM barang WHERE kode = ?', (kode,)).fetchone()
    conn.close()
    return dict(item) if item else None

def get_item_by_id(item_id):
    """Get item by its ID"""
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM barang WHERE id = ?', (item_id,)).fetchone()
    conn.close()
    return dict(item) if item else None

def get_all_items():
    """Get all items from database"""
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM barang ORDER BY kode').fetchall()
    conn.close()
    return [dict(item) for item in items]

def update_item_profit(item_data):
    """Update profit for a single item based on sales"""
    profit = calculate_total_profit(item_data['harga_awal'], item_data['harga_jual'], 
                                  item_data['stok_awal'], item_data['stok_akhir'])
    
    conn = get_db_connection()
    conn.execute('UPDATE barang SET profit = ? WHERE id = ?', (profit, item_data['id']))
    conn.commit()
    conn.close()
    
    item_data['profit'] = profit
    return item_data

@app.route('/')
def index():
    """Home page with role selection"""
    return render_template('index.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_role'] = 'admin'
            session['username'] = username
            flash('Login berhasil!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username atau password salah!', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('user_role', None)
    session.pop('username', None)
    flash('Logout berhasil!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if session.get('user_role') != 'admin':
        flash('Akses ditolak! Login sebagai admin terlebih dahulu.', 'error')
        return redirect(url_for('admin_login'))
    
    # Get items from database
    items = get_all_items()
    
    # Ambil transaksi dari database untuk statistik
    all_transactions = get_all_transactions()
    
    # Calculate statistics
    total_items = len(items)
    total_transactions = len(all_transactions)
    total_revenue = sum(t['total'] for t in all_transactions)
    total_profit = sum(t['profit'] for t in all_transactions)
    
    # Update profit for each item based on sales
    for item in items:
        update_item_profit(item)
    
    # Low stock items (less than 5)
    low_stock_items = [item for item in items if item['stok_akhir'] < 5]
    
    stats = {
        'total_items': total_items,
        'total_transactions': total_transactions,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'low_stock_count': len(low_stock_items)
    }
    
    return render_template('admin/dashboard.html', stats=stats, low_stock_items=low_stock_items)

@app.route('/admin/items')
def admin_items():
    """View all items + Search + JSON untuk AJAX"""
    if session.get('user_role') != 'admin':
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify([])  # kalau AJAX, kembalikan list kosong
        flash('Akses ditolak! Login sebagai admin terlebih dahulu.', 'error')
        return redirect(url_for('admin_login'))
    
    q = request.args.get('q', '').strip().lower()
    items = get_all_items()  # <- ini list of dict dari DB

    if q:
        items = [
            item for item in items
            if q in str(item.get('kode', '')).lower() or q in str(item.get('nama', '')).lower()
        ]
    
    # Kalau request dari AJAX (fetch JS), kembalikan JSON saja
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(items)
    
    # Kalau biasa, render template
    return render_template('admin/items.html', items=items)

@app.route('/generate_barcode/<code>')
def generate_barcode(code):
    """Generate barcode image"""
    try:
        # Force re-import to ensure libraries are available
        from barcode import Code128
        from barcode.writer import ImageWriter
        
        # Generate barcode
        code128 = Code128(code, writer=ImageWriter())
        buffer = io.BytesIO()
        code128.write(buffer)
        buffer.seek(0)
        
        return send_file(buffer, mimetype='image/png', as_attachment=False)
    except ImportError as e:
        app.logger.error(f"Barcode library import error: {e}")
        # Return a simple error image instead of JSON
        return "Barcode library not available", 404
    except Exception as e:
        app.logger.error(f"Error generating barcode: {e}")
        return f"Error generating barcode: {str(e)}", 500

@app.route('/generate_qrcode/<code>')
def generate_qrcode(code):
    """Generate QR code image"""
    try:
        # Force re-import to ensure libraries are available
        import qrcode
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return send_file(buffer, mimetype='image/png', as_attachment=False)
    except ImportError as e:
        app.logger.error(f"QR code library import error: {e}")
        # Return a simple error message instead of JSON
        return "QR code library not available", 404
    except Exception as e:
        app.logger.error(f"Error generating QR code: {e}")
        return f"Error generating QR code: {str(e)}", 500

@app.route('/download_barcode/<code>')
def download_barcode(code):
    """Download barcode as file"""
    try:
        from barcode import Code128
        from barcode.writer import ImageWriter
        
        code128 = Code128(code, writer=ImageWriter())
        buffer = io.BytesIO()
        code128.write(buffer)
        buffer.seek(0)
        
        return send_file(buffer, mimetype='image/png', as_attachment=True, 
                        download_name=f'barcode_{code}.png')
    except ImportError as e:
        app.logger.error(f"Barcode library import error: {e}")
        return "Barcode library not available", 404
    except Exception as e:
        app.logger.error(f"Error downloading barcode: {e}")
        return f"Error downloading barcode: {str(e)}", 500

@app.route('/download_qrcode/<code>')
def download_qrcode(code):
    """Download QR code as file"""
    try:
        import qrcode
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return send_file(buffer, mimetype='image/png', as_attachment=True,
                        download_name=f'qrcode_{code}.png')
    except ImportError as e:
        app.logger.error(f"QR code library import error: {e}")
        return "QR code library not available", 404
    except Exception as e:
        app.logger.error(f"Error downloading QR code: {e}")
        return f"Error downloading QR code: {str(e)}", 500

@app.route('/admin/items/add', methods=['GET', 'POST'])
def admin_add_item():
    """Add new item"""
    if session.get('user_role') != 'admin':
        flash('Akses ditolak! Login sebagai admin terlebih dahulu.', 'error')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        kode = request.form.get('kode', '')
        nama = request.form.get('nama', '')
        harga_awal = int(request.form.get('harga_awal', 0))
        harga_jual = int(request.form.get('harga_jual', 0))
        stok_awal = int(request.form.get('stok_awal', 0))
        
        # Check if code already exists
        if get_item_by_code(kode):
            flash('Kode barang sudah ada!', 'error')
            return render_template('admin/add_item.html')
        
        # Create new item
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO barang (id, kode, nama, harga_awal, harga_jual, stok_awal, stok_akhir, profit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (kode, kode, nama, harga_awal, harga_jual, stok_awal, stok_awal, 0))
        conn.commit()
        conn.close()
        
        flash('Barang berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_items'))
    
    return render_template('admin/add_item.html')

@app.route('/admin/items/edit/<item_id>', methods=['GET', 'POST'])
def admin_edit_item(item_id):
    """Edit existing item"""
    if session.get('user_role') != 'admin':
        flash('Akses ditolak! Login sebagai admin terlebih dahulu.', 'error')
        return redirect(url_for('admin_login'))
    
    item = get_item_by_id(item_id)
    if not item:
        flash('Barang tidak ditemukan!', 'error')
        return redirect(url_for('admin_items'))
    
    if request.method == 'POST':
        kode = request.form.get('kode', '')
        nama = request.form.get('nama', '')
        harga_awal = int(request.form.get('harga_awal', 0))
        harga_jual = int(request.form.get('harga_jual', 0))
        stok_awal = int(request.form.get('stok_awal', 0))
        stok_akhir = int(request.form.get('stok_akhir', 0))
        
        # Check if code already exists for other items
        existing_item = get_item_by_code(kode)
        if existing_item and existing_item['id'] != item_id:
            flash('Kode barang sudah digunakan oleh barang lain!', 'error')
            return render_template('admin/edit_item.html', item=item)
        
        # Calculate profit
        profit = calculate_total_profit(harga_awal, harga_jual, stok_awal, stok_akhir)
        
        # Update data termasuk stok_awal
        conn = get_db_connection()
        conn.execute('''
            UPDATE barang 
            SET kode = ?, nama = ?, harga_awal = ?, harga_jual = ?, 
                stok_awal = ?, stok_akhir = ?, profit = ?
            WHERE id = ?
        ''', (kode, nama, harga_awal, harga_jual, stok_awal, stok_akhir, profit, item_id))
        conn.commit()
        conn.close()
        
        flash('Barang berhasil diperbarui!', 'success')
        return redirect(url_for('admin_items'))
    
    return render_template('admin/edit_item.html', item=item)

@app.route('/admin/items/delete/<item_id>')
def admin_delete_item(item_id):
    """Delete item"""
    if session.get('user_role') != 'admin':
        flash('Akses ditolak! Login sebagai admin terlebih dahulu.', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM barang WHERE id = ?', (item_id,))
    conn.commit()
    
    if cursor.rowcount > 0:
        flash('Barang berhasil dihapus!', 'success')
    else:
        flash('Barang tidak ditemukan!', 'error')
    
    conn.close()
    return redirect(url_for('admin_items'))

def get_all_transactions():
    """Get all transactions from database"""
    conn = get_db_connection()
    db_transactions = conn.execute('SELECT * FROM transactions ORDER BY timestamp DESC').fetchall()
    conn.close()
    
    transactions = []
    for row in db_transactions:
        transaction = {
            'id': row['id'],
            'timestamp': row['timestamp'],
            'items': json.loads(row['items']),
            'total': row['total'],
            'profit': row['profit'],
            'payment_amount': row['payment_amount'],
            'change': row['change_amount']
        }
        transactions.append(transaction)
    
    return transactions

@app.route('/admin/reports')
def admin_reports():
    """View reports"""
    if session.get('user_role') != 'admin':
        flash('Akses ditolak! Login sebagai admin terlebih dahulu.', 'error')
        return redirect(url_for('admin_login'))
    
    # Ambil semua transaksi dari database
    all_transactions = get_all_transactions()
    
    # Calculate daily sales
    daily_sales = {}
    for transaction in all_transactions:
        date = transaction['timestamp'].split()[0]  # Get date part
        if date not in daily_sales:
            daily_sales[date] = {'total': 0, 'profit': 0, 'count': 0}
        daily_sales[date]['total'] += transaction['total']
        daily_sales[date]['profit'] += transaction['profit']
        daily_sales[date]['count'] += 1
    
    # Top selling items
    item_sales = {}
    for transaction in all_transactions:
        for item in transaction['items']:
            kode = item['kode']
            if kode not in item_sales:
                item_sales[kode] = {'nama': item['nama'], 'quantity': 0, 'revenue': 0}
            item_sales[kode]['quantity'] += item['quantity']
            item_sales[kode]['revenue'] += item['subtotal']
    
    # Sort by quantity sold
    top_items = sorted(item_sales.items(), key=lambda x: x[1]['quantity'], reverse=True)[:10]
    
    return render_template('admin/reports.html', 
                         daily_sales=daily_sales, 
                         top_items=top_items,
                         transactions=all_transactions)

@app.route('/cashier')
def cashier_pos():
    """Cashier POS interface"""
    session['user_role'] = 'cashier'  # Simple role assignment for cashier
    items = get_all_items()
    return render_template('cashier/pos.html', items=items)

@app.route('/cashier/search_item')
def search_item():
    """Search item by code or name"""
    query = request.args.get('q', '').lower()
    results = []
    
    items = get_all_items()
    for item in items:
        if (query in item['kode'].lower() or 
            query in item['nama'].lower()) and item['stok_akhir'] > 0:
            results.append(item)
    
    return jsonify(results)

@app.route('/cashier/process_sale', methods=['POST'])
def process_sale():
    """Process a sale transaction"""
    data = request.get_json()
    cart_items = data.get('items', [])
    payment_amount = data.get('payment_amount', 0)
    
    if not cart_items:
        return jsonify({'success': False, 'message': 'Keranjang kosong!'})
    
    global next_transaction_id
    transaction_items = []
    total_amount = 0
    total_profit = 0
    
    conn = get_db_connection()
    
    # Process each item in cart
    for cart_item in cart_items:
        kode = cart_item['kode']
        quantity = cart_item['quantity']
        
        # Find item in inventory
        item = get_item_by_code(kode)
        if not item:
            conn.close()
            return jsonify({'success': False, 'message': f'Barang {kode} tidak ditemukan!'})
        
        # Check stock
        if item['stok_akhir'] < quantity:
            conn.close()
            return jsonify({'success': False, 'message': f'Stok {item["nama"]} tidak mencukupi!'})
        
        # Calculate subtotal and profit
        subtotal = item['harga_jual'] * quantity
        profit = calculate_profit(item['harga_awal'], item['harga_jual'], quantity)
        
        # Update stock
        new_stock = item['stok_akhir'] - quantity
        new_profit = calculate_total_profit(item['harga_awal'], item['harga_jual'], 
                                          item['stok_awal'], new_stock)
        
        conn.execute('''
            UPDATE barang SET stok_akhir = ?, profit = ? WHERE id = ?
        ''', (new_stock, new_profit, item['id']))
        
        # Add to transaction items
        transaction_items.append({
            'kode': kode,
            'nama': item['nama'],
            'harga_jual': item['harga_jual'],
            'quantity': quantity,
            'subtotal': subtotal
        })
        
        total_amount += subtotal
        total_profit += profit
    
    conn.commit()
    conn.close()
    
    # Calculate change
    change = payment_amount - total_amount if payment_amount >= total_amount else 0
    
    # Create transaction record
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    transaction = {
        'id': next_transaction_id,
        'timestamp': timestamp,
        'items': transaction_items,
        'total': total_amount,
        'profit': total_profit,
        'payment_amount': payment_amount,
        'change': change
    }
    
    # Simpan ke database SQLite
    conn_trans = get_db_connection()
    conn_trans.execute('''
        INSERT INTO transactions (timestamp, items, total, profit, payment_amount, change_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, json.dumps(transaction_items), total_amount, total_profit, payment_amount, change))
    conn_trans.commit()
    conn_trans.close()
    
    transactions_data.append(transaction)
    next_transaction_id += 1
    
    return jsonify({
        'success': True, 
        'message': 'Transaksi berhasil!',
        'transaction_id': transaction['id'],
        'total': total_amount,
        'payment_amount': payment_amount,
        'change': change,
        'timestamp': transaction['timestamp'],
        'items': transaction_items
    })

@app.route('/cashier/history')
def cashier_history():
    """View transaction history"""
    # Ambil transaksi dari database
    conn = get_db_connection()
    db_transactions = conn.execute('''
        SELECT * FROM transactions 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''').fetchall()
    conn.close()
    
    # Convert database rows to dictionary format
    recent_transactions = []
    for row in db_transactions:
        transaction = {
            'id': row['id'],
            'timestamp': row['timestamp'],
            'items': json.loads(row['items']),
            'total': row['total'],
            'profit': row['profit'],
            'payment_amount': row['payment_amount'],
            'change': row['change_amount']
        }
        recent_transactions.append(transaction)
    
    # Calculate summary statistics and add item count to each transaction
    total_transactions = len(recent_transactions)
    total_items_sold = 0
    total_revenue = 0
    total_profit = 0
    
    # Add item count to each transaction for easy display
    for transaction in recent_transactions:
        total_revenue += transaction['total']
        total_profit += transaction['profit']
        
        # Calculate item count for this transaction
        transaction_item_count = 0
        for item in transaction['items']:
            transaction_item_count += item['quantity']
            total_items_sold += item['quantity']
        
        # Add item count to transaction for template use
        transaction['item_count'] = transaction_item_count
    
    summary = {
        'total_transactions': total_transactions,
        'total_items_sold': total_items_sold,
        'total_revenue': total_revenue,
        'total_profit': total_profit
    }
    
    return render_template('cashier/history.html', 
                         transactions=recent_transactions,
                         summary=summary)



if __name__ == '__main__':
    import webbrowser
    import threading
    import time
    import platform
    import subprocess

    def open_browser():
        time.sleep(2)  # Tunggu server Flask siap
        url = "http://127.0.0.1:5000/"
        
        # Fullscreen hanya untuk Windows (bisa disesuaikan)
        if platform.system() == "Windows":
            try:
                # Gunakan start chrome dalam mode fullscreen
                subprocess.Popen([
                    "cmd", "/c",
                    'start chrome --kiosk ' + url
                ])
            except Exception as e:
                print(f"Gagal membuka browser fullscreen: {e}")
                webbrowser.open(url)
        else:
            webbrowser.open(url)

    # Jalankan fungsi open_browser di thread terpisah
    threading.Thread(target=open_browser).start()

    app.run(host='0.0.0.0', port=5000, debug=True)

  # app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('ssl_cert.pem', 'ssl_key.pem'))