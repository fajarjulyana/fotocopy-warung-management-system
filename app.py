
import os
import logging
import json
import base64
import io
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash

# Import barcode and QR code libraries
try:
    import qrcode
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
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "business-app-fajarmandiri-2025")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///integrated_business_app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Database Models
class BusinessSettings(db.Model):
    __tablename__ = 'business_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(255), nullable=False, default='Business App by fajarmandiri.store')
    address = db.Column(db.Text)
    phone = db.Column(db.String(50))
    website = db.Column(db.String(255), default='fajarmandiri.store')
    copyright_text = db.Column(db.String(255), default='© 2025 Fajar Julyana - fajarmandiri.store')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    debts = db.relationship('CustomerDebt', backref='customer', cascade='all, delete-orphan')
    
    @property
    def total_debt(self):
        active_debts = CustomerDebt.query.filter_by(customer_id=self.id, status='active').all()
        return sum(debt.remaining_amount for debt in active_debts)

class CustomerDebt(db.Model):
    __tablename__ = 'customer_debts'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    invoice_number = db.Column(db.String(50))
    description = db.Column(db.Text, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    remaining_amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')  # active, paid, overdue
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    payments = db.relationship('DebtPayment', backref='debt', cascade='all, delete-orphan')

class DebtPayment(db.Model):
    __tablename__ = 'debt_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    debt_id = db.Column(db.Integer, db.ForeignKey('customer_debts.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='cashier')  # admin, manager, cashier
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Product/Inventory Models
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    barcode = db.Column(db.String(100), unique=True)
    qr_code = db.Column(db.String(100), unique=True)
    purchase_price = db.Column(db.Float, nullable=False, default=0)
    selling_price = db.Column(db.Float, nullable=False, default=0)
    initial_stock = db.Column(db.Integer, nullable=False, default=0)
    current_stock = db.Column(db.Integer, nullable=False, default=0)
    profit = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    material_costs = db.relationship('MaterialCost', backref='product', cascade='all, delete-orphan')
    service_costs = db.relationship('ServiceCost', backref='product', cascade='all, delete-orphan')
    maintenance_costs = db.relationship('MaintenanceCost', backref='product', cascade='all, delete-orphan')
    inventory_items = db.relationship('InventoryItem', backref='product', cascade='all, delete-orphan')
    
    def calculate_profit(self):
        """Calculate profit based on purchase price, selling price, initial stock, and current stock"""
        sold_quantity = self.initial_stock - self.current_stock
        if sold_quantity > 0:
            self.profit = (self.selling_price - self.purchase_price) * sold_quantity
        else:
            self.profit = 0
        return self.profit

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), db.ForeignKey('products.id'), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False, default=0)
    selling_price = db.Column(db.Float, nullable=False, default=0)
    initial_stock = db.Column(db.Integer, nullable=False, default=0)
    current_stock = db.Column(db.Integer, nullable=False, default=0)
    minimum_stock = db.Column(db.Integer, nullable=False, default=5)
    profit = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MaterialCost(db.Model):
    __tablename__ = 'material_costs'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), db.ForeignKey('products.id'), nullable=False)
    item_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ServiceCost(db.Model):
    __tablename__ = 'service_costs'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), db.ForeignKey('products.id'), nullable=False)
    service_name = db.Column(db.String(255), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MaintenanceCost(db.Model):
    __tablename__ = 'maintenance_costs'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), db.ForeignKey('products.id'), nullable=False)
    maintenance_type = db.Column(db.String(255), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    cost_per_occurrence = db.Column(db.Float, nullable=False)
    annual_cost = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Savings Models
class Saver(db.Model):
    __tablename__ = 'savers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    transactions = db.relationship('SavingsTransaction', backref='saver', lazy=True, cascade='all, delete-orphan')
    
    def get_balance(self):
        deposits = db.session.query(db.func.sum(SavingsTransaction.amount)).filter(
            SavingsTransaction.saver_id == self.id,
            SavingsTransaction.type == 'deposit'
        ).scalar() or 0
        
        withdrawals = db.session.query(db.func.sum(SavingsTransaction.amount)).filter(
            SavingsTransaction.saver_id == self.id,
            SavingsTransaction.type == 'withdrawal'
        ).scalar() or 0
        
        return deposits - withdrawals

class SavingsTransaction(db.Model):
    __tablename__ = 'savings_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    saver_id = db.Column(db.Integer, db.ForeignKey('savers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'deposit' or 'withdrawal'
    description = db.Column(db.Text)
    balance_after = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Transaction Models
class CashierTransaction(db.Model):
    __tablename__ = 'cashier_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    items = db.Column(db.Text, nullable=False)  # JSON string
    total = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    change_amount = db.Column(db.Float, nullable=False)
    cashier_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Invoice Models
class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    client_name = db.Column(db.String(255), nullable=False)
    client_email = db.Column(db.String(255))
    client_phone = db.Column(db.String(50))
    client_address = db.Column(db.Text)
    service_date = db.Column(db.Date, nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, overdue
    notes = db.Column(db.Text)
    subtotal = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    service_items = db.relationship('ServiceItem', backref='invoice', cascade='all, delete-orphan')

class ServiceItem(db.Model):
    __tablename__ = 'service_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)

# Utility functions
def format_currency(amount):
    """Format amount as Indonesian Rupiah"""
    return f"Rp {amount:,.0f}".replace(',', '.')

def format_date_indonesian(date):
    """Format date in Indonesian"""
    months = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
        5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
        9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }
    return f"{date.day} {months[date.month]} {date.year}"

def generate_product_id():
    """Generate unique product ID"""
    import string
    import random
    
    # Get last product count
    last_product = Product.query.order_by(Product.created_at.desc()).first()
    count = 1
    if last_product:
        try:
            # Extract number from last ID (assuming format like PRD001, PRD002, etc.)
            last_num = int(''.join(filter(str.isdigit, last_product.id)))
            count = last_num + 1
        except:
            count = 1
    
    return f"PRD{count:03d}"

def generate_barcode_data(product_id):
    """Generate barcode data for product"""
    return f"BC{product_id}{datetime.now().strftime('%m%d')}"

def generate_qr_data(product_id, product_name):
    """Generate QR code data for product"""
    return f"QR{product_id}|{product_name}|{datetime.now().strftime('%Y%m%d')}"

def login_required(f):
    """Decorator to require login"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """Decorator to require admin or manager role"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'manager']:
            flash('Akses ditolak. Hanya admin atau manager yang dapat mengakses halaman ini.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def cashier_access(f):
    """Decorator to allow cashier and above roles"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'manager', 'cashier']:
            flash('Akses ditolak.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# PDF Generation Functions
def generate_receipt_pdf(transaction):
    """Generate receipt PDF for transaction"""
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Business info
    business = BusinessSettings.query.first()
    if business:
        elements.append(Paragraph(business.business_name, styles['Title']))
        if business.address:
            elements.append(Paragraph(business.address, styles['Normal']))
        if business.phone:
            elements.append(Paragraph(f"Telp: {business.phone}", styles['Normal']))
    
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("STRUK BELANJA", styles['Heading1']))
    elements.append(Spacer(1, 6))
    
    # Transaction info
    elements.append(Paragraph(f"No. Transaksi: {transaction.id}", styles['Normal']))
    elements.append(Paragraph(f"Tanggal: {transaction.timestamp.strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Paragraph(f"Kasir: {User.query.get(transaction.cashier_id).username if transaction.cashier_id else 'N/A'}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Items table
    items = json.loads(transaction.items)
    data = [['Item', 'Qty', 'Harga', 'Subtotal']]
    
    for item in items:
        data.append([
            item['name'][:20],
            str(item['quantity']),
            format_currency(item['selling_price']),
            format_currency(item['subtotal'])
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 12))
    
    # Totals
    elements.append(Paragraph(f"Total: {format_currency(transaction.total)}", styles['Heading2']))
    elements.append(Paragraph(f"Bayar: {format_currency(transaction.payment_amount)}", styles['Normal']))
    elements.append(Paragraph(f"Kembali: {format_currency(transaction.change_amount)}", styles['Normal']))
    
    elements.append(Spacer(1, 24))
    elements.append(Paragraph("Terima kasih atas kunjungan Anda!", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_savings_statement_pdf(saver):
    """Generate savings statement PDF"""
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    
    # Business info
    business = BusinessSettings.query.first()
    if business:
        elements.append(Paragraph(business.business_name, styles['Title']))
        if business.address:
            elements.append(Paragraph(business.address, styles['Normal']))
    
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("REKENING KORAN TABUNGAN", styles['Heading1']))
    elements.append(Spacer(1, 6))
    
    # Saver info
    elements.append(Paragraph(f"Nama: {saver.name}", styles['Normal']))
    if saver.phone:
        elements.append(Paragraph(f"Telepon: {saver.phone}", styles['Normal']))
    if saver.address:
        elements.append(Paragraph(f"Alamat: {saver.address}", styles['Normal']))
    
    elements.append(Paragraph(f"Saldo Saat Ini: {format_currency(saver.get_balance())}", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    # Transactions table
    transactions = SavingsTransaction.query.filter_by(saver_id=saver.id).order_by(SavingsTransaction.date.desc()).all()
    
    data = [['Tanggal', 'Jenis', 'Jumlah', 'Keterangan', 'Saldo']]
    
    for transaction in transactions:
        data.append([
            transaction.date.strftime('%d/%m/%Y'),
            'Setor' if transaction.type == 'deposit' else 'Tarik',
            format_currency(transaction.amount),
            transaction.description[:30],
            format_currency(transaction.balance_after)
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 24))
    elements.append(Paragraph(f"Dicetak pada: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_admin_report_pdf(start_date, end_date):
    """Generate admin report PDF"""
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    
    # Business info
    business = BusinessSettings.query.first()
    if business:
        elements.append(Paragraph(business.business_name, styles['Title']))
        
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("LAPORAN BISNIS", styles['Heading1']))
    elements.append(Paragraph(f"Periode: {start_date} - {end_date}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Revenue calculation
    transactions = CashierTransaction.query.filter(
        CashierTransaction.timestamp >= datetime.strptime(start_date, '%Y-%m-%d'),
        CashierTransaction.timestamp <= datetime.strptime(end_date, '%Y-%m-%d')
    ).all()
    
    total_revenue = sum(t.total for t in transactions)
    total_profit = sum(t.profit for t in transactions)
    total_loss = total_revenue - total_profit - sum(t.total for t in transactions if t.profit < 0)
    
    # Summary table
    summary_data = [
        ['Metrik', 'Nilai'],
        ['Total Penjualan', format_currency(total_revenue)],
        ['Total Keuntungan', format_currency(total_profit)],
        ['Total Kerugian', format_currency(abs(total_loss) if total_loss < 0 else 0)],
        ['Jumlah Transaksi', str(len(transactions))]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 24))
    
    # Best selling items
    elements.append(Paragraph("ITEM TERLARIS", styles['Heading2']))
    
    # Calculate best selling items
    item_sales = {}
    for transaction in transactions:
        items = json.loads(transaction.items)
        for item in items:
            if item['name'] in item_sales:
                item_sales[item['name']] += item['quantity']
            else:
                item_sales[item['name']] = item['quantity']
    
    # Sort by quantity sold
    sorted_items = sorted(item_sales.items(), key=lambda x: x[1], reverse=True)[:10]
    
    bestseller_data = [['Item', 'Terjual']]
    for item, qty in sorted_items:
        bestseller_data.append([item[:30], str(qty)])
    
    bestseller_table = Table(bestseller_data)
    bestseller_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(bestseller_table)
    elements.append(Spacer(1, 24))
    
    # Low stock items
    elements.append(Paragraph("STOK RENDAH", styles['Heading2']))
    low_stock_items = InventoryItem.query.filter(InventoryItem.current_stock <= InventoryItem.minimum_stock).all()
    
    stock_data = [['Item', 'Stok Saat Ini', 'Minimum Stok']]
    for item in low_stock_items:
        stock_data.append([
            item.product.name[:30],
            str(item.current_stock),
            str(item.minimum_stock)
        ])
    
    stock_table = Table(stock_data)
    stock_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(stock_table)
    elements.append(Spacer(1, 24))
    elements.append(Paragraph(f"Dibuat pada: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Routes
@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            flash(f'Selamat datang, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Password tidak cocok!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email sudah digunakan!', 'error')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logout berhasil!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user = User.query.get(session['user_id'])
    
    # Get business settings
    business = BusinessSettings.query.first()
    if not business:
        business = BusinessSettings()
        db.session.add(business)
        db.session.commit()
    
    # Get statistics
    stats = {
        'total_products': Product.query.count(),
        'total_inventory_items': InventoryItem.query.count(),
        'low_stock_items': InventoryItem.query.filter(InventoryItem.current_stock <= InventoryItem.minimum_stock).count(),
        'total_savers': Saver.query.count(),
        'total_savings': db.session.query(db.func.sum(SavingsTransaction.amount)).filter(SavingsTransaction.type == 'deposit').scalar() or 0,
        'total_invoices': Invoice.query.count(),
        'pending_invoices': Invoice.query.filter_by(status='draft').count(),
        'total_transactions': CashierTransaction.query.count(),
        'today_revenue': 0,
        'total_customers': Customer.query.count(),
        'total_debts': db.session.query(db.func.sum(CustomerDebt.remaining_amount)).filter(CustomerDebt.status == 'active').scalar() or 0,
        'overdue_debts': CustomerDebt.query.filter(CustomerDebt.due_date < datetime.now().date(), CustomerDebt.status == 'active').count()
    }
    
    # Calculate today's revenue
    today = datetime.now().date()
    today_transactions = CashierTransaction.query.filter(
        db.func.date(CashierTransaction.timestamp) == today
    ).all()
    stats['today_revenue'] = sum(t.total for t in today_transactions)
    
    return render_template('dashboard.html', user=user, business=business, stats=stats, format_currency=format_currency)

# Product Management Routes
@app.route('/products')
@manager_required
def products():
    """Product list"""
    products = Product.query.all()
    return render_template('products/list.html', products=products, format_currency=format_currency)

@app.route('/products/edit/<product_id>', methods=['GET', 'POST'])
@manager_required
def edit_product(product_id):
    """Edit product"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.purchase_price = float(request.form.get('purchase_price', 0))
        product.selling_price = float(request.form.get('selling_price', 0))
        product.initial_stock = int(request.form.get('initial_stock', 0))
        product.current_stock = int(request.form.get('current_stock', 0))
        
        # Recalculate profit
        product.calculate_profit()
        product.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Produk berhasil diperbarui!', 'success')
        return redirect(url_for('products'))
    
    return render_template('products/edit.html', product=product)

@app.route('/products/add', methods=['GET', 'POST'])
@manager_required
def add_product():
    """Add product"""
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        if not product_id:
            product_id = generate_product_id()
        
        name = request.form.get('name')
        description = request.form.get('description')
        purchase_price = float(request.form.get('purchase_price', 0))
        selling_price = float(request.form.get('selling_price', 0))
        initial_stock = int(request.form.get('initial_stock', 0))
        
        if Product.query.get(product_id):
            flash('ID Produk sudah ada!', 'error')
            return render_template('products/add.html', generated_id=generate_product_id())
        
        # Generate barcode and QR code data
        barcode_data = generate_barcode_data(product_id)
        qr_data = generate_qr_data(product_id, name)
        
        product = Product(
            id=product_id, 
            name=name, 
            description=description,
            barcode=barcode_data,
            qr_code=qr_data,
            purchase_price=purchase_price,
            selling_price=selling_price,
            initial_stock=initial_stock,
            current_stock=initial_stock
        )
        
        # Calculate initial profit (0 since nothing sold yet)
        product.calculate_profit()
        
        db.session.add(product)
        db.session.commit()
        
        flash('Produk berhasil ditambahkan dengan barcode dan QR code!', 'success')
        return redirect(url_for('products'))
    
    return render_template('products/add.html', generated_id=generate_product_id())

# Inventory Management Routes
@app.route('/inventory')
@manager_required
def inventory():
    """Inventory list"""
    items = InventoryItem.query.join(Product).all()
    return render_template('inventory/list.html', items=items, format_currency=format_currency)

@app.route('/inventory/add', methods=['GET', 'POST'])
@manager_required
def add_inventory_item():
    """Add inventory item"""
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        code = request.form.get('code')
        purchase_price = float(request.form.get('purchase_price', 0))
        selling_price = float(request.form.get('selling_price', 0))
        initial_stock = int(request.form.get('initial_stock', 0))
        minimum_stock = int(request.form.get('minimum_stock', 5))
        
        if InventoryItem.query.filter_by(code=code).first():
            flash('Kode barang sudah ada!', 'error')
            return render_template('inventory/add.html', products=Product.query.all())
        
        item = InventoryItem(
            product_id=product_id,
            code=code,
            purchase_price=purchase_price,
            selling_price=selling_price,
            initial_stock=initial_stock,
            current_stock=initial_stock,
            minimum_stock=minimum_stock
        )
        db.session.add(item)
        db.session.commit()
        
        flash('Item inventory berhasil ditambahkan!', 'success')
        return redirect(url_for('inventory'))
    
    products = Product.query.all()
    return render_template('inventory/add.html', products=products)

@app.route('/inventory/<int:item_id>/update_stock', methods=['POST'])
@login_required
def update_inventory_stock(item_id):
    """Update inventory stock"""
    item = InventoryItem.query.get_or_404(item_id)
    action = request.form.get('action')
    quantity = int(request.form.get('quantity', 0))
    notes = request.form.get('notes', '')
    
    if quantity <= 0:
        flash('Jumlah harus lebih dari 0!', 'error')
        return redirect(url_for('inventory'))
    
    if action == 'add':
        item.current_stock += quantity
        flash(f'Berhasil menambah {quantity} stok untuk {item.product.name}!', 'success')
    elif action == 'subtract':
        if quantity > item.current_stock:
            flash(f'Stok tidak mencukupi! Stok saat ini: {item.current_stock}', 'error')
            return redirect(url_for('inventory'))
        item.current_stock -= quantity
        flash(f'Berhasil mengurangi {quantity} stok untuk {item.product.name}!', 'success')
    elif action == 'set_minimum':
        item.minimum_stock = quantity
        flash(f'Berhasil mengatur minimum stok {item.product.name} menjadi {quantity}!', 'success')
    
    db.session.commit()
    return redirect(url_for('inventory'))

# Savings Management Routes
@app.route('/savings')
@cashier_access
def savings():
    """Savings dashboard"""
    search_query = request.args.get('search', '').strip()
    
    savers_query = Saver.query
    if search_query:
        savers_query = savers_query.filter(Saver.name.contains(search_query))
    
    savers = savers_query.order_by(Saver.name).all()
    
    recent_transactions = db.session.query(SavingsTransaction).join(Saver).order_by(
        SavingsTransaction.created_at.desc()
    ).limit(20).all()
    
    total_deposits = db.session.query(db.func.sum(SavingsTransaction.amount)).filter(
        SavingsTransaction.type == 'deposit'
    ).scalar() or 0
    
    total_withdrawals = db.session.query(db.func.sum(SavingsTransaction.amount)).filter(
        SavingsTransaction.type == 'withdrawal'
    ).scalar() or 0
    
    stats = {
        'total_savers': len(savers),
        'total_balance': total_deposits - total_withdrawals,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals
    }
    
    return render_template('savings/dashboard.html', 
                         savers=savers, 
                         recent_transactions=recent_transactions,
                         stats=stats,
                         search_query=search_query,
                         format_currency=format_currency)

@app.route('/savings/deposit', methods=['GET', 'POST'])
@login_required
def savings_deposit():
    """Add deposit"""
    if request.method == 'POST':
        date_str = request.form.get('date')
        amount = float(request.form.get('amount'))
        description = request.form.get('description', '').strip()
        saver_name = request.form.get('saver_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get or create saver
        saver = Saver.query.filter_by(name=saver_name).first()
        if not saver:
            saver = Saver(name=saver_name, phone=phone, address=address)
            db.session.add(saver)
            db.session.flush()
        
        current_balance = saver.get_balance()
        new_balance = current_balance + amount
        
        transaction = SavingsTransaction(
            saver_id=saver.id,
            date=entry_date,
            amount=amount,
            type='deposit',
            description=description or 'Setoran tabungan',
            balance_after=new_balance
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Berhasil menyetor {format_currency(amount)} untuk {saver_name}!', 'success')
        
        # Redirect to receipt with option to print
        return redirect(url_for('savings_receipt', transaction_id=transaction.id))
    
    existing_savers = [s.name for s in Saver.query.order_by(Saver.name).all()]
    return render_template('savings/deposit.html', 
                         existing_savers=existing_savers,
                         datetime=datetime)

@app.route('/savings/withdraw', methods=['GET', 'POST'])
@login_required
def savings_withdraw():
    """Add withdrawal"""
    if request.method == 'POST':
        date_str = request.form.get('date')
        amount = float(request.form.get('amount'))
        description = request.form.get('description', '').strip()
        saver_name = request.form.get('saver_name', '').strip()
        
        entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get saver
        saver = Saver.query.filter_by(name=saver_name).first()
        if not saver:
            flash('Penabung tidak ditemukan!', 'error')
            return redirect(url_for('savings_withdraw'))
        
        current_balance = saver.get_balance()
        if amount > current_balance:
            flash('Saldo tidak mencukupi!', 'error')
            return redirect(url_for('savings_withdraw'))
        
        new_balance = current_balance - amount
        
        transaction = SavingsTransaction(
            saver_id=saver.id,
            date=entry_date,
            amount=amount,
            type='withdrawal',
            description=description or 'Penarikan tabungan',
            balance_after=new_balance
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Berhasil menarik {format_currency(amount)} untuk {saver_name}!', 'success')
        
        # Redirect to receipt with option to print
        return redirect(url_for('savings_receipt', transaction_id=transaction.id))
    
    existing_savers = [s.name for s in Saver.query.order_by(Saver.name).all()]
    return render_template('savings/withdraw.html', 
                         existing_savers=existing_savers,
                         datetime=datetime)

@app.route('/savings/statement/<int:saver_id>')
@login_required
def savings_statement(saver_id):
    """Generate savings statement PDF"""
    saver = Saver.query.get_or_404(saver_id)
    
    if REPORTLAB_AVAILABLE:
        pdf_buffer = generate_savings_statement_pdf(saver)
        if pdf_buffer:
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'rekening_koran_{saver.name}_{datetime.now().strftime("%Y%m%d")}.pdf'
            )
    
    flash('PDF generation tidak tersedia!', 'error')
    return redirect(url_for('savings'))

@app.route('/savings/receipt/<int:transaction_id>')
@login_required
def savings_receipt(transaction_id):
    """Display and generate savings transaction receipt PDF"""
    transaction = SavingsTransaction.query.get_or_404(transaction_id)
    
    # If requesting PDF download
    if request.args.get('format') == 'pdf':
        if REPORTLAB_AVAILABLE:
                # Create simplified receipt for savings transaction
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                styles = getSampleStyleSheet()
                elements = []
                
                # Business info
                business = BusinessSettings.query.first()
                if business:
                    elements.append(Paragraph(business.business_name, styles['Title']))
                    if business.address:
                        elements.append(Paragraph(business.address, styles['Normal']))
                
                elements.append(Spacer(1, 12))
                elements.append(Paragraph("STRUK TABUNGAN", styles['Heading1']))
                elements.append(Spacer(1, 6))
                
                # Transaction info
                elements.append(Paragraph(f"No. Transaksi: {transaction.id}", styles['Normal']))
                elements.append(Paragraph(f"Tanggal: {transaction.date.strftime('%d/%m/%Y')}", styles['Normal']))
                elements.append(Paragraph(f"Waktu: {transaction.created_at.strftime('%H:%M:%S')}", styles['Normal']))
                elements.append(Paragraph(f"Nama: {transaction.saver.name}", styles['Normal']))
                
                transaction_type = 'Setoran' if transaction.type == 'deposit' else 'Penarikan'
                elements.append(Paragraph(f"Jenis: {transaction_type}", styles['Normal']))
                elements.append(Paragraph(f"Jumlah: {format_currency(transaction.amount)}", styles['Heading2']))
                elements.append(Paragraph(f"Saldo Setelah: {format_currency(transaction.balance_after)}", styles['Normal']))
                
                if transaction.description:
                    elements.append(Paragraph(f"Keterangan: {transaction.description}", styles['Normal']))
                
                elements.append(Spacer(1, 24))
                elements.append(Paragraph("Terima kasih atas kepercayaan Anda!", styles['Normal']))
                
                if business and business.copyright_text:
                    elements.append(Paragraph(business.copyright_text, styles['Normal']))
                
                doc.build(elements)
                buffer.seek(0)
                
                return send_file(
                    buffer,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'struk_tabungan_{transaction.id}_{datetime.now().strftime("%Y%m%d")}.pdf'
                )
            
        flash('PDF generation tidak tersedia!', 'error')
        return redirect(url_for('savings'))
    
    # Display receipt page
    business = BusinessSettings.query.first()
    return render_template('savings/receipt.html', 
                         transaction=transaction, 
                         business=business,
                         format_currency=format_currency,
                         datetime=datetime)

# Cashier/POS Routes
@app.route('/pos')
@cashier_access
def pos():
    """POS interface"""
    items = InventoryItem.query.filter(InventoryItem.current_stock > 0).join(Product).all()
    return render_template('pos/interface.html', items=items)

@app.route('/pos/search')
@login_required
def pos_search():
    """Search items for POS"""
    query = request.args.get('q', '').lower()
    items = InventoryItem.query.join(Product).filter(
        InventoryItem.current_stock > 0
    ).all()
    
    results = []
    for item in items:
        if (query in item.code.lower() or 
            query in item.product.name.lower()):
            results.append({
                'id': item.id,
                'code': item.code,
                'name': item.product.name,
                'selling_price': item.selling_price,
                'current_stock': item.current_stock
            })
    
    return jsonify(results)

@app.route('/pos/process_sale', methods=['POST'])
@login_required
def process_sale():
    """Process sale transaction"""
    data = request.get_json()
    cart_items = data.get('items', [])
    payment_amount = data.get('payment_amount', 0)
    
    if not cart_items:
        return jsonify({'success': False, 'message': 'Keranjang kosong!'})
    
    transaction_items = []
    total_amount = 0
    total_profit = 0
    
    for cart_item in cart_items:
        item_id = cart_item['id']
        quantity = cart_item['quantity']
        
        item = InventoryItem.query.get(item_id)
        if not item or item.current_stock < quantity:
            return jsonify({'success': False, 'message': f'Stok tidak mencukupi untuk {item.product.name if item else "item tidak ditemukan"}!'})
        
        subtotal = item.selling_price * quantity
        profit = (item.selling_price - item.purchase_price) * quantity
        
        # Update stock
        item.current_stock -= quantity
        
        transaction_items.append({
            'code': item.code,
            'name': item.product.name,
            'selling_price': item.selling_price,
            'quantity': quantity,
            'subtotal': subtotal
        })
        
        total_amount += subtotal
        total_profit += profit
    
    change = payment_amount - total_amount if payment_amount >= total_amount else 0
    
    # Save transaction
    transaction = CashierTransaction(
        timestamp=datetime.now(),
        items=json.dumps(transaction_items),
        total=total_amount,
        profit=total_profit,
        payment_amount=payment_amount,
        change_amount=change,
        cashier_id=session['user_id']
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Transaksi berhasil!',
        'transaction_id': transaction.id,
        'total': total_amount,
        'payment_amount': payment_amount,
        'change': change
    })

@app.route('/pos/receipt/<int:transaction_id>')
@login_required
def print_receipt(transaction_id):
    """Generate receipt PDF"""
    transaction = CashierTransaction.query.get_or_404(transaction_id)
    
    if REPORTLAB_AVAILABLE:
        pdf_buffer = generate_receipt_pdf(transaction)
        if pdf_buffer:
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'struk_{transaction.id}_{datetime.now().strftime("%Y%m%d")}.pdf'
            )
    
    flash('PDF generation tidak tersedia!', 'error')
    return redirect(url_for('pos'))

# Invoice Management Routes
@app.route('/invoices')
@cashier_access
def invoices():
    """Invoice list"""
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return render_template('invoices/list.html', invoices=invoices, format_currency=format_currency)

@app.route('/invoices/create', methods=['GET', 'POST'])
@login_required
def create_invoice():
    """Create invoice"""
    if request.method == 'POST':
        # Generate invoice number
        last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
        invoice_number = f"INV-{(last_invoice.id + 1 if last_invoice else 1):05d}"
        
        invoice = Invoice(
            invoice_number=invoice_number,
            client_name=request.form.get('client_name'),
            client_email=request.form.get('client_email'),
            client_phone=request.form.get('client_phone'),
            client_address=request.form.get('client_address'),
            service_date=datetime.strptime(request.form.get('service_date'), '%Y-%m-%d').date(),
            issue_date=datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d').date(),
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date(),
            notes=request.form.get('notes')
        )
        
        db.session.add(invoice)
        db.session.flush()
        
        # Add service items
        items_data = request.form.getlist('items')
        subtotal = 0
        
        for item_json in items_data:
            if item_json.strip():
                item_data = json.loads(item_json)
                service_item = ServiceItem(
                    invoice_id=invoice.id,
                    description=item_data['description'],
                    quantity=float(item_data['quantity']),
                    rate=float(item_data['rate']),
                    amount=float(item_data['amount'])
                )
                db.session.add(service_item)
                subtotal += service_item.amount
        
        # Calculate totals
        tax_rate = float(request.form.get('tax_rate', 0))
        invoice.subtotal = subtotal
        invoice.tax_rate = tax_rate
        invoice.tax_amount = subtotal * (tax_rate / 100)
        invoice.total = subtotal + invoice.tax_amount
        
        db.session.commit()
        
        flash('Invoice berhasil dibuat!', 'success')
        return redirect(url_for('invoices'))
    
    return render_template('invoices/create.html')

# Customer Debt Management Routes
@app.route('/debts')
@cashier_access
def customer_debts():
    """Customer debt list"""
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    
    query = CustomerDebt.query.join(Customer)
    
    if search:
        query = query.filter(Customer.name.contains(search))
    
    if status_filter != 'all':
        query = query.filter(CustomerDebt.status == status_filter)
    
    debts = query.order_by(CustomerDebt.created_at.desc()).all()
    
    # Check for overdue debts
    today = datetime.now().date()
    for debt in debts:
        if debt.due_date and debt.due_date < today and debt.status == 'active':
            debt.status = 'overdue'
    
    db.session.commit()
    
    return render_template('debts/list.html', debts=debts, search=search, status_filter=status_filter, format_currency=format_currency)

@app.route('/debts/add', methods=['GET', 'POST'])
@cashier_access
def add_customer_debt():
    """Add customer debt"""
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        customer_phone = request.form.get('customer_phone')
        customer_email = request.form.get('customer_email')
        customer_address = request.form.get('customer_address')
        
        # Get or create customer
        customer = Customer.query.filter_by(name=customer_name).first()
        if not customer:
            customer = Customer(
                name=customer_name,
                phone=customer_phone,
                email=customer_email,
                address=customer_address
            )
            db.session.add(customer)
            db.session.flush()
        
        debt = CustomerDebt(
            customer_id=customer.id,
            invoice_number=request.form.get('invoice_number'),
            description=request.form.get('description'),
            total_amount=float(request.form.get('total_amount')),
            remaining_amount=float(request.form.get('total_amount')),
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None,
            created_by=session['user_id']
        )
        
        db.session.add(debt)
        db.session.commit()
        
        flash('Hutang pelanggan berhasil ditambahkan!', 'success')
        return redirect(url_for('customer_debts'))
    
    customers = Customer.query.all()
    return render_template('debts/add.html', customers=customers)

@app.route('/debts/<int:debt_id>/pay', methods=['POST'])
@cashier_access
def pay_debt(debt_id):
    """Record debt payment"""
    debt = CustomerDebt.query.get_or_404(debt_id)
    payment_amount = float(request.form.get('payment_amount'))
    notes = request.form.get('notes', '')
    
    if payment_amount <= 0:
        flash('Jumlah pembayaran harus lebih dari 0!', 'error')
        return redirect(url_for('customer_debts'))
    
    if payment_amount > debt.remaining_amount:
        flash('Jumlah pembayaran melebihi sisa hutang!', 'error')
        return redirect(url_for('customer_debts'))
    
    # Record payment
    payment = DebtPayment(
        debt_id=debt.id,
        amount=payment_amount,
        payment_date=datetime.now().date(),
        notes=notes,
        created_by=session['user_id']
    )
    
    debt.paid_amount += payment_amount
    debt.remaining_amount -= payment_amount
    
    if debt.remaining_amount <= 0:
        debt.status = 'paid'
    
    db.session.add(payment)
    db.session.commit()
    
    flash(f'Pembayaran {format_currency(payment_amount)} berhasil dicatat!', 'success')
    return redirect(url_for('customer_debts'))

# Admin Routes
@app.route('/admin/users')
@admin_required
def admin_users():
    """User management"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/toggle/<int:user_id>')
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "diaktifkan" if user.is_active else "dinonaktifkan"
    flash(f'User {user.username} berhasil {status}!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/promote/<int:user_id>')
@admin_required
def promote_user(user_id):
    """Promote user to admin"""
    user = User.query.get_or_404(user_id)
    user.role = 'admin' if user.role != 'admin' else 'user'
    db.session.commit()
    
    role = "admin" if user.role == 'admin' else "user"
    flash(f'User {user.username} berhasil diubah menjadi {role}!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/business_settings', methods=['GET', 'POST'])
@admin_required
def business_settings():
    """Business settings management"""
    business = BusinessSettings.query.first()
    if not business:
        business = BusinessSettings()
        db.session.add(business)
        db.session.commit()
    
    if request.method == 'POST':
        business.business_name = request.form.get('business_name')
        business.address = request.form.get('address')
        business.phone = request.form.get('phone')
        business.website = request.form.get('website')
        business.copyright_text = request.form.get('copyright_text')
        business.updated_by = session['user_id']
        business.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Pengaturan bisnis berhasil diperbarui!', 'success')
        return redirect(url_for('business_settings'))
    
    return render_template('admin/business_settings.html', business=business)

@app.route('/admin/reports', methods=['GET', 'POST'])
@admin_required
def admin_reports():
    """Admin reports page"""
    if request.method == 'POST':
        start_date = request.form.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.form.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        if REPORTLAB_AVAILABLE:
            pdf_buffer = generate_admin_report_pdf(start_date, end_date)
            if pdf_buffer:
                return send_file(
                    pdf_buffer,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'laporan_bisnis_{start_date}_to_{end_date}.pdf'
                )
        
        flash('PDF generation tidak tersedia!', 'error')
    
    # Calculate statistics for display
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    
    transactions = CashierTransaction.query.filter(
        CashierTransaction.timestamp >= start_date
    ).all()
    
    total_revenue = sum(t.total for t in transactions)
    total_profit = sum(t.profit for t in transactions)
    
    # Best selling items
    item_sales = {}
    for transaction in transactions:
        items = json.loads(transaction.items)
        for item in items:
            if item['name'] in item_sales:
                item_sales[item['name']] += item['quantity']
            else:
                item_sales[item['name']] = item['quantity']
    
    sorted_items = sorted(item_sales.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Low stock items
    low_stock_items = InventoryItem.query.filter(InventoryItem.current_stock <= InventoryItem.minimum_stock).all()
    
    stats = {
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'total_loss': abs(total_revenue - total_profit) if total_profit < 0 else 0,
        'total_transactions': len(transactions),
        'best_selling': sorted_items,
        'low_stock_items': low_stock_items
    }
    
    return render_template('admin/reports.html', 
                         stats=stats, 
                         format_currency=format_currency,
                         datetime=datetime,
                         timedelta=timedelta)

# API Routes
@app.route('/api/generate_barcode/<code>')
def generate_barcode(code):
    """Generate barcode"""
    if not BARCODE_AVAILABLE:
        return "Barcode library not available", 404
    
    try:
        code128 = Code128(code, writer=ImageWriter())
        buffer = io.BytesIO()
        code128.write(buffer)
        buffer.seek(0)
        
        return send_file(buffer, mimetype='image/png', as_attachment=False)
    except Exception as e:
        return f"Error generating barcode: {str(e)}", 500

@app.route('/api/generate_qrcode/<code>')
def generate_qrcode(code):
    """Generate QR code"""
    if not QRCODE_AVAILABLE:
        return "QR code library not available", 404
    
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return send_file(buffer, mimetype='image/png', as_attachment=False)
    except Exception as e:
        return f"Error generating QR code: {str(e)}", 500

@app.route('/api/generate_product_id')
def api_generate_product_id():
    """Generate new product ID via API"""
    return jsonify({'product_id': generate_product_id()})

@app.route('/products/<product_id>/print_codes')
@manager_required
def print_product_codes(product_id):
    """Print barcode and QR code for product"""
    product = Product.query.get_or_404(product_id)
    return render_template('products/print_codes.html', product=product)

@app.route('/api/saver_balance/<saver_name>')
@login_required
def get_saver_balance(saver_name):
    """API endpoint to get saver balance"""
    saver = Saver.query.filter_by(name=saver_name).first()
    if saver:
        balance = saver.get_balance()
        return jsonify({
            'exists': True,
            'balance': balance,
            'formatted_balance': format_currency(balance)
        })
    else:
        return jsonify({
            'exists': False,
            'balance': 0,
            'formatted_balance': 'Penabung tidak ditemukan'
        })

# Template filters
@app.template_filter('currency')
def currency_filter(amount):
    return format_currency(amount)

@app.template_filter('indonesian_date')
def indonesian_date_filter(date):
    return format_date_indonesian(date)

# Initialize database
def init_database():
    """Initialize database and create admin user"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@fajarmandiri.store', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: admin/admin123")
        
        # Create default business settings
        business = BusinessSettings.query.first()
        if not business:
            business = BusinessSettings(
                business_name='Business App by fajarmandiri.store',
                address='Jl. Contoh No. 123, Jakarta',
                phone='0812-3456-7890',
                website='fajarmandiri.store',
                copyright_text='© 2025 Fajar Julyana - fajarmandiri.store'
            )
            db.session.add(business)
            db.session.commit()
            print("Default business settings created")

if __name__ == '__main__':
    init_database()
    
    import webbrowser
    import threading
    import time
    
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:5000/")
    
    threading.Thread(target=open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
