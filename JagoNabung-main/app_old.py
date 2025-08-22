import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_for_savings_tracker")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database - Use PostgreSQL for production or SQLite for local
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    # Fallback to SQLite for local development
    if hasattr(sys, '_MEIPASS'):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    db_dir = os.path.join(os.path.dirname(base_dir), 'SavingsTrackerData')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'savings_tracker.db')
    database_url = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True,
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Database Models
class Saver(db.Model):
    __tablename__ = 'savers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to transactions
    transactions = db.relationship('Transaction', backref='saver', lazy=True, cascade='all, delete-orphan')
    
    def get_balance(self):
        """Calculate current balance for this saver"""
        deposits = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.saver_id == self.id,
            Transaction.type == 'deposit'
        ).scalar() or 0
        
        withdrawals = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.saver_id == self.id,
            Transaction.type == 'withdrawal'
        ).scalar() or 0
        
        return deposits - withdrawals
    
    def get_transaction_count(self):
        """Get total number of transactions for this saver"""
        return Transaction.query.filter_by(saver_id=self.id).count()

    def __repr__(self):
        return f'<Saver {self.id}: {self.name}>'


class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    saver_id = db.Column(db.Integer, db.ForeignKey('savers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'deposit' or 'withdrawal'
    description = db.Column(db.Text)
    balance_after = db.Column(db.Float, nullable=False)  # Balance after transaction
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.type} {self.amount} for saver {self.saver_id}>'


# Legacy model for migration support
class SavingsEntry(db.Model):
    __tablename__ = 'savings_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    saver_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SavingsEntry {self.id}: {self.saver_name} - {self.description}>'

def format_currency(amount):
    """Format amount as Indonesian Rupiah"""
    return f"Rp {amount:,.0f}".replace(',', '.')

def parse_currency(amount_str):
    """Parse currency string to float"""
    try:
        # Remove Rp, spaces, and dots, then convert to float
        clean_amount = amount_str.replace('Rp', '').replace(' ', '').replace('.', '').replace(',', '.')
        return float(clean_amount)
    except:
        return 0.0

# Initialize database
def init_db():
    """Initialize database and create tables if they don't exist"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Migrate old data if exists
        migrate_old_data()
        
        print("Database initialized successfully!")


def migrate_old_data():
    """Migrate data from old savings_entries to new structure"""
    try:
        # Check if old table exists and has data
        old_entries = db.session.execute(text("SELECT * FROM savings_entries")).fetchall()
        
        if old_entries:
            print(f"Migrating {len(old_entries)} old savings entries...")
            
            for entry in old_entries:
                # Create or get saver
                saver = Saver.query.filter_by(name=entry.saver_name).first()
                if not saver:
                    saver = Saver(name=entry.saver_name)
                    db.session.add(saver)
                    db.session.flush()  # Get ID
                
                # Create transaction (all old entries are deposits)
                current_balance = saver.get_balance()
                new_balance = current_balance + entry.amount
                
                transaction = Transaction(
                    saver_id=saver.id,
                    date=entry.date,
                    amount=entry.amount,
                    type='deposit',
                    description=entry.description,
                    balance_after=new_balance,
                    created_at=entry.created_at
                )
                db.session.add(transaction)
            
            db.session.commit()
            print("Migration completed successfully!")
            
    except Exception as e:
        print(f"Migration note: {e}")
        # No old data or already migrated

@app.route('/')
def index():
    """Main page showing savers and their balances"""
    search_query = request.args.get('search', '').strip()
    saver_filter = request.args.get('saver_filter', '').strip()
    
    # Get all savers with their statistics
    savers_query = Saver.query
    if search_query:
        savers_query = savers_query.filter(Saver.name.contains(search_query))
    
    savers = savers_query.order_by(Saver.name).all()
    
    # Get recent transactions
    transactions_query = db.session.query(Transaction).join(Saver)
    if saver_filter:
        transactions_query = transactions_query.filter(Saver.name.contains(saver_filter))
    
    recent_transactions = transactions_query.order_by(Transaction.created_at.desc()).limit(20).all()
    
    # Calculate totals
    total_savers = len(savers)
    total_deposits = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.type == 'deposit').scalar() or 0
    total_withdrawals = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.type == 'withdrawal').scalar() or 0
    total_balance = total_deposits - total_withdrawals
    
    # Get existing saver names for filter
    existing_savers = [saver.name for saver in Saver.query.order_by(Saver.name).all()]
    
    return render_template('index.html',
                         savers=savers,
                         recent_transactions=recent_transactions,
                         total_savers=total_savers,
                         total_balance=format_currency(total_balance),
                         total_deposits=format_currency(total_deposits),
                         total_withdrawals=format_currency(total_withdrawals),
                         existing_savers=existing_savers,
                         search_query=search_query,
                         saver_filter=saver_filter,
                         format_currency=format_currency,
                         format_date_indonesian=format_date_indonesian)

# New transaction routes
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    """Add deposit transaction"""
    existing_savers = [saver.name for saver in Saver.query.order_by(Saver.name).all()]
    
    if request.method == 'POST':
        try:
            date_str = request.form.get('date')
            amount_str = request.form.get('amount')
            description = request.form.get('description', '').strip()
            saver_name = request.form.get('saver_name', '').strip()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            
            if not date_str or not amount_str or not saver_name:
                flash('Tanggal, jumlah, dan nama penabung harus diisi!', 'error')
                return render_template('deposit.html', existing_savers=existing_savers)
            
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            amount = float(amount_str)
            
            if amount <= 0:
                flash('Jumlah harus lebih besar dari 0!', 'error')
                return render_template('deposit.html', existing_savers=existing_savers)
            
            # Get or create saver
            saver = Saver.query.filter_by(name=saver_name).first()
            if not saver:
                saver = Saver(name=saver_name, phone=phone, address=address)
                db.session.add(saver)
                db.session.flush()
            else:
                # Update saver info if provided
                if phone:
                    saver.phone = phone
                if address:
                    saver.address = address
            
            # Calculate new balance
            current_balance = saver.get_balance()
            new_balance = current_balance + amount
            
            # Create transaction
            transaction = Transaction(
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
            return redirect(url_for('print_receipt', transaction_id=transaction.id))
            
        except ValueError:
            flash('Format data tidak valid!', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
    
    return render_template('deposit.html', existing_savers=existing_savers)


@app.route('/withdraw', methods=['GET', 'POST'])  
def withdraw():
    """Add withdrawal transaction"""
    existing_savers = [saver.name for saver in Saver.query.order_by(Saver.name).all()]
    
    if request.method == 'POST':
        try:
            date_str = request.form.get('date')
            amount_str = request.form.get('amount')
            description = request.form.get('description', '').strip()
            saver_name = request.form.get('saver_name', '').strip()
            
            if not date_str or not amount_str or not saver_name:
                flash('Tanggal, jumlah, dan nama penabung harus diisi!', 'error')
                return render_template('withdraw.html', existing_savers=existing_savers)
            
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            amount = float(amount_str)
            
            if amount <= 0:
                flash('Jumlah harus lebih besar dari 0!', 'error')
                return render_template('withdraw.html', existing_savers=existing_savers)
            
            # Get saver
            saver = Saver.query.filter_by(name=saver_name).first()
            if not saver:
                flash(f'Penabung {saver_name} tidak ditemukan!', 'error')
                return render_template('withdraw.html', existing_savers=existing_savers)
            
            # Check balance
            current_balance = saver.get_balance()
            if amount > current_balance:
                flash(f'Saldo tidak mencukupi! Saldo saat ini: {format_currency(current_balance)}', 'error')
                return render_template('withdraw.html', existing_savers=existing_savers)
            
            # Calculate new balance
            new_balance = current_balance - amount
            
            # Create transaction
            transaction = Transaction(
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
            return redirect(url_for('print_receipt', transaction_id=transaction.id))
            
        except ValueError:
            flash('Format data tidak valid!', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
    
    return render_template('withdraw.html', existing_savers=existing_savers)
            flash('Terjadi kesalahan saat menyimpan data!', 'error')
            return render_template('add_entry.html', existing_savers=existing_savers)
    
    return render_template('add_entry.html', existing_savers=existing_savers)

@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    """Edit existing savings entry"""
    # Find entry
    entry = SavingsEntry.query.get_or_404(entry_id)
    # Get existing savers for autocomplete
    existing_savers = sorted(set(e.saver_name for e in SavingsEntry.query.all()))
    
    if request.method == 'POST':
        try:
            date_str = request.form.get('date')
            amount_str = request.form.get('amount')
            description = request.form.get('description', '').strip()
            saver_name = request.form.get('saver_name', '').strip()
            
            # Validation
            if not date_str or not amount_str or not description or not saver_name:
                flash('Semua field harus diisi!', 'error')
                return render_template('edit_entry.html', entry=entry, existing_savers=existing_savers)
            
            # Parse date
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Parse amount
            amount = float(amount_str)
            if amount <= 0:
                flash('Jumlah harus lebih besar dari 0!', 'error')
                return render_template('edit_entry.html', entry=entry, existing_savers=existing_savers)
            
            # Update entry
            entry.date = entry_date
            entry.amount = amount
            entry.description = description
            entry.saver_name = saver_name
            
            db.session.commit()
            
            flash(f'Berhasil mengubah data tabungan!', 'success')
            return redirect(url_for('index'))
            
        except ValueError:
            flash('Format data tidak valid!', 'error')
            return render_template('edit_entry.html', entry=entry, existing_savers=existing_savers)
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat mengubah data!', 'error')
            return render_template('edit_entry.html', entry=entry, existing_savers=existing_savers)
    
    return render_template('edit_entry.html', entry=entry, existing_savers=existing_savers)

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    """Delete savings entry"""
    try:
        entry = SavingsEntry.query.get_or_404(entry_id)
        db.session.delete(entry)
        db.session.commit()
        flash('Data tabungan berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat menghapus data!', 'error')
    
    return redirect(url_for('index'))

# Template filters
@app.template_filter('currency')
def currency_filter(amount):
    """Template filter to format currency"""
    return format_currency(amount)

@app.template_filter('dateformat')
def dateformat_filter(date):
    """Template filter to format date in Indonesian"""
    months = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
        5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
        9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }
    return f"{date.day} {months[date.month]} {date.year}"

# Initialize database when app starts
init_db()

# Print database location for user reference
print(f"Database location: {db_path}")
print(f"Database directory: {db_dir}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
