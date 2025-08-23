# Akumulasi Harga Produk

**Sistem Kalkulasi Biaya Produksi Komprehensif**  
*by fajarmandiri.store*

## 🏢 Informasi Perusahaan

**Alamat:** Jl. Pasir Wangi, RT.01/RW.11, Gudangkahuripan, Kec. Lembang, Kabupaten Bandung Barat, Jawa Barat 40391  
**Telepon:** [0818-0441-1937](tel:081804411937)

---

## 📖 Deskripsi

Aplikasi web Flask yang dirancang khusus untuk menghitung akumulasi harga produk dengan breakdown lengkap biaya bahan, jasa, dan perawatan alat. Dilengkapi dengan sistem manajemen inventory terintegrasi dan konverter harga kemasan untuk optimasi pembelian dalam jumlah besar.

## ✨ Fitur Utama

### 🎯 **Manajemen Produk**
- ✅ Tambah produk baru dengan deskripsi lengkap
- ✅ Breakdown biaya berdasarkan kategori (Bahan, Jasa, Perawatan)
- ✅ Kalkulasi otomatis total biaya produksi
- ✅ Histori perubahan harga dan biaya

### 💰 **Konverter Harga Kemasan**
- ✅ Preset kemasan populer (RIM, Set CMYK, Box A4, Dus Tinta, Karton)
- ✅ Kalkulasi harga per satuan dari kemasan bulk
- ✅ Optimasi pembelian dalam jumlah besar
- ✅ Input manual untuk kemasan khusus

### 📦 **Manajemen Inventory**
- ✅ Tracking stok bahan dan spare part
- ✅ Notifikasi stok rendah otomatis
- ✅ Histori pergerakan stok (masuk/keluar/adjustment)
- ✅ Kategorisasi item (Material, Maintenance)
- ✅ Estimasi waktu habis stok

### 🖨️ **Laporan & Cetak**
- ✅ Cetak daftar harga produk
- ✅ Export data untuk arsip
- ✅ Laporan biaya terperinci
- ✅ Dashboard statistik visual

## 🖼️ Screenshot Aplikasi

### 1. Dashboard Utama
*Halaman utama dengan header perusahaan dan statistik produk*

![Dashboard Utama](assets/dashboard.png)

- Header informasi perusahaan yang jelas
- Statistik jumlah produk dan total biaya
- Quick access ke fitur utama
- Daftar produk terbaru

### 2. Form Tambah Produk Baru
*Interface untuk menambah produk dan biaya terkait*

![Form Tambah Produk](assets/tambah-produk.png)

- Form input data produk
- Pilihan jenis biaya (Bahan/Jasa/Perawatan)
- Konverter harga kemasan terintegrasi
- Preview kalkulasi biaya real-time

### 3. Detail Biaya Produk
*Breakdown lengkap biaya produksi per produk*

![Detail Produk](assets/detail-produk.png)

- Breakdown biaya per kategori
- Total biaya produksi
- Opsi tambah biaya baru
- Histori perubahan biaya

### 4. Konverter Harga Kemasan
*Tool untuk menghitung harga satuan dari kemasan bulk*

![Konverter Kemasan](assets/konverter-kemasan.png)

- Preset kemasan populer (RIM, CMYK, Box, dll)
- Input harga kemasan dan isi
- Kalkulasi otomatis harga per satuan
- Support untuk kemasan custom

### 5. Manajemen Inventory
*Sistem tracking stok bahan dan spare part*

![Inventory Management](assets/inventory.png)

- Daftar item inventory dengan status stok
- Indikator stok rendah (warna-warni)
- Total nilai inventory
- Quick action untuk update stok

### 6. Form Tambah Item Inventory
*Interface untuk menambah item baru ke inventory*

![Form Inventory](assets/form-inventory.png)

- Form lengkap data item
- Kategorisasi material/maintenance
- Setting minimum stok
- Input supplier dan lokasi

### 7. Cetak Daftar Harga
*Output print-ready untuk daftar harga produk*

![Print Price List](assets/print-price.png)

- Format professional siap cetak
- Header perusahaan lengkap
- Daftar produk dengan harga
- Timestamp pencetakan

## 🚀 Teknologi

### Backend
- **Flask** - Web framework Python
- **SQLAlchemy** - Database ORM
- **SQLite** - Database engine
- **Gunicorn** - WSGI server

### Frontend
- **Bootstrap 5** - UI framework dengan dark theme
- **Font Awesome** - Icon library
- **Jinja2** - Template engine
- **Responsive Design** - Mobile-friendly

### Database
- **SQLite** dengan struktur relasional
- **Automatic backup** dan rollback support
- **Foreign key constraints** untuk integritas data

## 📋 Instalasi

### Prasyarat
- Python 3.8+
- pip package manager

### Langkah Instalasi

1. **Clone repository**
   ```bash
   git clone https://github.com/fajarjulyana/Akumulasi-Harga-Produk.git
   cd akumulasi-harga-produk
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi**
   ```bash
   python main.py
   ```

4. **Akses aplikasi**
   - Buka browser ke `http://localhost:5005`
   - Atau gunakan `http://0.0.0.0:5005` untuk akses network

## 🔧 Konfigurasi

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///akumulasi_harga.db

# Security
SESSION_SECRET=your-secret-key-here

# Debug (development only)
FLASK_DEBUG=1
```

### Port Configuration
Aplikasi berjalan di port **5005** secara default. Untuk production, gunakan reverse proxy seperti Nginx.

## 📝 Penggunaan

### 1. Tambah Produk Baru
1. Klik "Buat Produk Baru" di dashboard
2. Isi nama dan deskripsi produk
3. Pilih jenis biaya yang akan ditambahkan
4. Gunakan konverter kemasan jika diperlukan
5. Simpan produk

### 2. Kelola Inventory
1. Akses menu "Inventory" 
2. Tambah item baru dengan tombol "Tambah Item"
3. Set minimum stok untuk notifikasi otomatis
4. Update stok melalui form "Update Stok"

### 3. Cetak Laporan
1. Pilih produk yang akan dicetak
2. Klik "Cetak Daftar Harga"
3. Gunakan Ctrl+P untuk print

## 🎨 Dark Theme

Aplikasi menggunakan **Bootstrap Dark Theme** yang konsisten dengan:
- 🌙 Background gelap untuk kenyamanan mata
- 🎯 Kontras tinggi untuk readability
- 📱 Responsive di semua device
- ⚡ Loading cepat dengan optimasi CSS

## 📞 Support

Untuk pertanyaan atau support teknis:

📧 **Email:** info@fajarmandiri.store  
📱 **WhatsApp:** [0818-0441-1937](https://wa.me/6281804411937)  
🌐 **Website:** [fajarmandiri.store](https://fajarmandiri.store)

## 📄 Lisensi

© 2025 fajarmandiri.store. All rights reserved.

---

**Dikembangkan dengan ❤️ untuk optimasi bisnis percetakan dan production**
