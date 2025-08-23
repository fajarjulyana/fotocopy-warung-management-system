# Aplikasi Kasir Flask + SQLite

Aplikasi kasir berbasis **Flask** dan **SQLite** untuk mengelola barang, transaksi, dan stok secara mudah.  
Dilengkapi dengan fitur **login admin/kasir**, **keranjang belanja**, **pencetakan struk**, serta **stok awal yang dapat diubah** saat edit item.

## ✨ Fitur Utama
- **Manajemen Barang**: Tambah, edit, hapus barang.
- **Keranjang Belanja**: Pilih barang, atur jumlah, dan simpan ke transaksi.
- **Cetak Struk**: Print struk langsung dari aplikasi.
- **Sistem Login**: Admin dan Kasir dengan hak akses berbeda.
- **Stok Awal Dapat Diubah**: Saat edit item, stok awal bisa diatur ulang.
- **Preview & Download Kode Barang**: Lihat kode barang dalam bentuk QR dan unduh.

## 🖼️ Screenshot

| Dashboard Admin | Home Aplikasi | Menu Kasir |
|-----------------|---------------|------------|
| ![Dashboard Admin](capture/dashboard-admin.PNG) | ![Home Aplikasi](capture/homeapp.PNG) | ![Menu Kasir](capture/menu-kasir.PNG) |

## 🛠️ Instalasi
1. **Clone repository**
   ```bash
   git clone https://github.com/username/aplikasi-kasir.git
   cd aplikasi-kasir

2. **Buat virtual environment & aktifkan**

   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux / Mac
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi**

   ```bash
   flask run
   ```

   Buka browser: `http://127.0.0.1:5000`

## 📂 Struktur Folder

```
aplikasi-kasir/
│── app.py               # Main aplikasi Flask
│── templates/           # HTML templates (Jinja2)
│── static/              # CSS, JS, dan assets
│── database.db          # Database SQLite
│── requirements.txt     # List library Python
│── README.md            # Dokumentasi
│── LICENSE              # Lisensi MIT
```

## 🔄 Changelog

### v1.2.0 (14 Agustus 2025)

* ✨ **Fitur Baru**: Stok awal dapat diubah saat edit item.
* ➕ Tambah tombol **Preview & Download Kode Barang** di halaman edit item.
* 🛠️ Perbaikan minor pada tampilan form edit.

### v1.1.0 (12 Agustus 2025)

* ✨ Penambahan fitur cetak struk transaksi.
* 🛠️ Optimisasi query SQL untuk kecepatan akses.

### v1.0.0 (10 Agustus 2025)

* Rilis awal aplikasi kasir.
* Fitur login, tambah/edit barang, keranjang belanja.

## 👤 Pemilik & Pembuat

**Fajar Julyana**

## 📜 Lisensi

Proyek ini dilisensikan di bawah **[MIT License](LICENSE)**.
