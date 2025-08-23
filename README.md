
# Fajar Mandiri Store Management System

Sistem manajemen bisnis terintegrasi yang menggabungkan Point of Sale (POS), Tabungan, Service Note, Inventory Management, dan fitur bisnis lainnya dalam satu aplikasi dengan database terintegrasi.

## 🎯 Fitur Utama

### 📊 Point of Sale (POS)
- Interface kasir modern dan responsif
- Manajemen produk dengan barcode
- Perhitungan otomatis dan kembalian
- Cetak struk transaksi
- Laporan penjualan harian

### 💰 Sistem Tabungan (JagoNabung)
- Manajemen rekening tabungan nasabah
- Deposit dan penarikan dengan validasi
- Cetak rekening koran dan struk transaksi
- Dashboard monitoring tabungan
- Riwayat transaksi lengkap

### 🔧 Service Note
- Manajemen nota service/reparasi
- Invoice dan billing system
- Tracking status perbaikan
- Cetak invoice professional
- Database pelanggan service

### 📦 Inventory Management
- Manajemen stok barang realtime
- Tracking harga beli dan jual
- Perhitungan profit otomatis
- Alert stok minimum
- Riwayat pergerakan stok

### 💳 Debt Management
- Pencatatan piutang/hutang
- Tracking pembayaran cicilan
- Reminder jatuh tempo
- Laporan aging receivables

## 🚀 Teknologi

- **Backend**: Flask + SQLAlchemy
- **Database**: SQLite dengan relasi terintegrasi
- **Frontend**: Bootstrap 5 + JavaScript
- **Template Engine**: Jinja2
- **Icons**: Font Awesome 6

## 📋 Persyaratan

- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Werkzeug

## 🛠️ Instalasi

1. Clone repository:
```bash
git clone <repository-url>
cd fajar-mandiri-store
```

2. Install dependencies:
```bash
pip install flask flask-sqlalchemy werkzeug
```

3. Jalankan aplikasi:
```bash
python app.py
```

4. Akses aplikasi di: `http://localhost:5000`

## 📱 Penggunaan

### Login Default
- **Admin**: Username dan password akan dibuat saat setup pertama
- **Cashier**: Role terbatas untuk operasi kasir

### Modul Utama

#### 1. Dashboard
- Overview bisnis realtime
- Statistik penjualan hari ini
- Status inventory critical
- Summary tabungan aktif

#### 2. Point of Sale
- Scan/input barcode produk
- Keranjang belanja interaktif
- Perhitungan total dan kembalian
- Cetak struk otomatis

#### 3. Tabungan
- Registrasi nasabah baru
- Deposit dan withdraw
- Cetak rekening koran
- Monitoring saldo

#### 4. Service Note
- Buat invoice service
- Input item perbaikan
- Tracking status
- Generate PDF invoice

#### 5. Inventory
- Tambah produk baru
- Update stok dan harga
- Monitor profit margin
- Alert stok minimum

## 🗂️ Struktur Database

Database terintegrasi dengan tabel-tabel utama:
- `users` - Manajemen pengguna dan role
- `products` - Master produk dan inventory
- `sales` - Transaksi penjualan POS
- `savers` - Data nasabah tabungan
- `savings_transactions` - Transaksi tabungan
- `invoices` - Service invoices dan billing
- `debts` - Manajemen piutang/hutang

## 📄 Template Cetak

Sistem menyediakan template cetak untuk:
- Struk POS (thermal printer format)
- Rekening koran tabungan
- Invoice service professional
- Laporan inventory
- Statement piutang

## 🔐 Keamanan

- Session-based authentication
- Role-based access control (Admin/Cashier)
- Input validation dan sanitization
- Database transaction integrity

## 🌐 Deployment

Untuk deployment production di Replit:

1. Pastikan semua dependencies terinstall
2. Set environment variables jika diperlukan
3. Gunakan port 5000 (sudah dikonfigurasi)
4. Deploy menggunakan Replit Deployments

## 📞 Informasi Bisnis

**Fajar Mandiri Store**
- Alamat: Jalan Pasirwangi RT001/RW011 KEC.LEMBANG KAB.BANDUNG BARAT KODE POS 40391
- Telp: 0818-0441-1937
- Email: info@fajarmandiri.store

## 📝 Lisensi

Aplikasi ini dikembangkan untuk keperluan bisnis Fajar Mandiri Store.

## 🤝 Kontribusi

Untuk pengembangan dan maintenance aplikasi, silakan hubungi developer atau tim IT Fajar Mandiri Store.

---

*Sistem Manajemen Bisnis Terintegrasi - Fajar Mandiri Store © 2024*
