
# Fajar Mandiri Store Management System

Sistem manajemen bisnis terintegrasi yang menggabungkan Point of Sale (POS), Tabungan, Service Note, Inventory Management, dan fitur bisnis lainnya dalam satu aplikasi dengan database terintegrasi.

## 🎯 Fitur Utama

### 📊 Point of Sale (POS)
- Interface kasir modern dan responsif dengan barcode scanner
- Manajemen produk dengan ID maksimal 50 karakter alphanumeric
- Perhitungan profit otomatis dengan formula: BT = SA + Pembelian - SK
- Cetak struk transaksi thermal printer format
- Laporan penjualan realtime dengan analisis margin

### 💰 Sistem Tabungan (JagoNabung)
- Manajemen rekening tabungan nasabah dengan validasi saldo
- Deposit dan penarikan dengan tracking balance history
- Cetak rekening koran dan struk transaksi format bank ATM
- Dashboard monitoring tabungan dengan statistik lengkap
- Riwayat transaksi detail dengan search functionality

### 🔧 Service Note & Invoice System
- Manajemen nota service/reparasi dengan tracking status
- Invoice dan billing system professional
- Multi-item service dengan perhitungan tax otomatis
- Cetak invoice PDF format bisnis profesional
- Database pelanggan service terintegrasi

### 📦 Inventory Management
- Manajemen stok barang realtime dengan alert minimum stock
- Tracking harga beli, jual, dan stok tambahan
- Perhitungan profit otomatis: Profit = (HJ - HB) × BT
- Multi-category product management dengan barcode/QR code
- Riwayat pergerakan stok dengan audit trail

### 💳 Customer Debt Management
- Pencatatan piutang/hutang pelanggan dengan due date
- Tracking pembayaran cicilan dengan history payment
- Reminder jatuh tempo dengan status overdue
- Laporan aging receivables dan customer analysis

### ⚙️ Business Settings Integration
- Pengaturan informasi bisnis terpusat (nama, alamat, kontak)
- Integrasi otomatis dengan semua struk, receipt, dan report
- Customizable business branding di semua dokumen
- Copyright dan website information management

## 🚀 Teknologi

- **Backend**: Flask 2.x + SQLAlchemy dengan relational database
- **Database**: SQLite dengan foreign key constraints dan migrations
- **Frontend**: Bootstrap 5.3 + JavaScript ES6 + Font Awesome 6
- **PDF Generation**: ReportLab untuk professional document output
- **Barcode/QR**: Python-barcode + qrcode libraries
- **Authentication**: Session-based dengan role management

## 📋 Persyaratan Sistem

- Python 3.8+ dengan pip package manager
- Flask dan Flask-SQLAlchemy untuk web framework
- Werkzeug untuk security dan utilities
- ReportLab untuk PDF generation (optional)
- Python-barcode dan qrcode untuk code generation (optional)

## 🛠️ Instalasi & Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd fajar-mandiri-store
```

### 2. Install Dependencies
```bash
pip install flask flask-sqlalchemy werkzeug
# Optional untuk fitur lengkap:
pip install reportlab python-barcode[images] qrcode[pil]
```

### 3. Jalankan Aplikasi
```bash
python app.py
```

### 4. Akses Aplikasi
- URL: `http://localhost:5000`
- Admin Default: username `admin`, password `admin123`
- Port 5000 sudah dikonfigurasi untuk Replit deployment

## 📱 Penggunaan Detail

### Login & Role Management
- **Admin**: Full access ke semua fitur termasuk settings dan reports
- **Manager**: Access ke inventory, products, dan basic operations
- **Cashier**: Terbatas ke POS, savings, dan customer operations

### Dashboard Utama
- Overview bisnis realtime dengan statistik hari ini
- Quick access ke semua modul utama
- Monitoring stok kritis dan debt overdue
- Performance metrics dan profit analysis

### Modul POS (Point of Sale)
1. **Product Search**: Scan barcode atau search manual
2. **Shopping Cart**: Add/remove items dengan quantity control
3. **Payment Process**: Input payment dengan change calculation
4. **Receipt Print**: Generate thermal printer format PDF
5. **Transaction History**: Track semua penjualan dengan profit

### Modul Tabungan
1. **Registrasi Nasabah**: Input data lengkap nasabah baru
2. **Deposit/Withdraw**: Validasi saldo dan update balance
3. **Statement**: Generate rekening koran PDF format bank
4. **Receipt**: Print struk format ATM untuk setiap transaksi
5. **Search & Filter**: Cari nasabah dan filter transaksi

### Modul Inventory
1. **Product Management**: CRUD products dengan 50-char ID support
2. **Stock Control**: Real-time stock update dengan minimum alert
3. **Profit Calculation**: Otomatis hitung profit per item dan total
4. **Barcode/QR Generation**: Generate codes untuk setiap produk
5. **Category Management**: Organize products by category dan brand

## 🗂️ Struktur Database Terintegrasi

### Core Tables
- `users` - User management dengan role-based access
- `business_settings` - Centralized business information
- `products` - Master produk dengan full specifications
- `inventory_items` - Stock tracking dan inventory control

### Transaction Tables
- `cashier_transactions` - POS sales dengan item details
- `savings_transactions` - Tabungan deposit/withdraw history
- `invoices` - Service invoices dengan multi-item support
- `customer_debts` - Debt tracking dengan payment history

### Relationship & Constraints
- Foreign key relationships untuk data integrity
- Cascade delete untuk related records
- Index optimization untuk fast queries
- Migration support untuk schema updates

## 📄 Document Templates

### Struk & Receipt Format
- **POS Receipt**: Thermal printer 58mm format
- **Savings Receipt**: ATM bank receipt style
- **Invoice**: Professional business invoice A4
- **Statement**: Bank account statement format

### Business Integration
- Semua dokumen otomatis menggunakan business settings
- Konsisten branding di seluruh sistem
- Customizable header/footer information
- Multi-language support (Indonesian primary)

## 🔐 Keamanan & Validasi

### Authentication
- Session-based login dengan secure cookies
- Password hashing menggunakan Werkzeug
- Role-based access control (RBAC)
- Automatic session timeout untuk security

### Data Validation
- Input sanitization untuk prevent SQL injection
- Form validation dengan error handling
- File upload restrictions dan size limits
- Business logic validation di model layer

### Database Security
- Transaction integrity dengan rollback support
- Foreign key constraints enforcement
- Regular backup recommendations
- Migration version control

## 🌐 Deployment di Replit

### Production Setup
1. **Environment Variables**: Set untuk production mode
2. **Database**: SQLite sudah ready untuk small-medium business
3. **Static Files**: Bootstrap & assets served efficiently
4. **Port Configuration**: Port 5000 auto-forwarding ke 80/443
5. **Domain**: Custom domain support via Replit deployments

### Performance Optimization
- Database indexing untuk fast queries
- Lazy loading untuk large datasets
- Caching untuk frequently accessed data
- Optimized PDF generation

## 📊 Reporting & Analytics

### Built-in Reports
- **Sales Report**: Daily/monthly revenue dan profit analysis
- **Inventory Report**: Stock levels, turnover, dan reorder points
- **Customer Report**: Debt aging, payment history, top customers
- **Business Summary**: Comprehensive business performance

### Export Options
- **PDF**: Professional formatted reports
- **Print**: Direct printer support untuk receipts
- **Filter**: Date range, category, customer filtering
- **Search**: Advanced search across all modules

## 📞 Business Information

**Fajar Mandiri Fotocopy**
- **Alamat**: KP Jl. Pasir Wangi, RT.01/RW.11, Gudangkahuripan, Kec. Lembang, Kab. Bandung Barat, Jawa Barat 40391
- **Telepon**: (+62) 81804411937
- **Website**: fajarmandiri.store
- **Email**: info@fajarmandiri.store

## 🔧 Maintenance & Support

### Database Backup
- Automatic backup pada setiap migration
- Manual backup tools tersedia
- Restore functionality untuk recovery

### System Updates
- Version control untuk code changes
- Migration scripts untuk database updates
- Configuration management via admin panel

### Troubleshooting
- Comprehensive error logging
- Debug mode untuk development
- Performance monitoring tools

## 📝 License & Terms

Aplikasi ini dikembangkan khusus untuk keperluan bisnis Fajar Mandiri Store dengan full customization dan business logic sesuai kebutuhan operasional.

## 🤝 Development & Contribution

Untuk pengembangan fitur baru, maintenance, atau technical support, silakan hubungi tim development atau IT support Fajar Mandiri Store.

### Feature Requests
- Product enhancement suggestions
- Integration dengan system external
- Custom reporting requirements
- Performance optimization needs

---

*Integrated Business Management System - Fajar Mandiri Store © 2025*
*Powered by Flask + SQLAlchemy + Bootstrap 5*
