# FJ Service Center - Invoice Management System

Sistem manajemen invoice untuk FJ Service Center yang menangani service komputer, laptop, dan handphone.

## Fitur Utama
- ✅ Membuat dan mengelola invoice service
- ✅ Database SQLite untuk penyimpanan data
- ✅ Generate PDF invoice dengan format profesional
- ✅ Tracking data customer
- ✅ Interface bahasa Indonesia
- ✅ Tabel invoice dengan 10 baris (sesuai permintaan)
- ✅ Port 5001 dengan Chrome auto-launch

## Cara Menjalankan

### Di Replit
```bash
# Menggunakan workflow otomatis (recommended)
# Tekan tombol "Run" di Replit

# Atau manual:
python start_app.py
```

### Di Windows (Local)
```bash
# Untuk Windows dengan encoding fix:
python start_windows.py

# Atau menggunakan batch file:
launch_chrome.bat
```

### Manual Chrome Launch
Jika Chrome tidak terbuka otomatis, buka manual:
```
http://localhost:5001
```

## Struktur Database
- **Invoice**: Data utama invoice dengan customer info
- **ServiceItem**: Item-item service dalam setiap invoice

## File Penting
- `app.py` - Aplikasi Flask utama
- `database.py` - Model database SQLite
- `models.py` - Business logic dan InvoiceManager
- `pdf_generator.py` - Generate PDF invoice
- `chrome_launcher.py` - Auto-launch Chrome (dengan fix encoding)
- `start_windows.py` - Startup script khusus Windows

## Troubleshooting

### Error Encoding di Windows
Jika muncul error `UnicodeEncodeError`, gunakan:
```bash
python start_windows.py
```

### Chrome Tidak Terbuka
1. Pastikan Chrome terinstall
2. Buka manual: http://localhost:5001
3. Reset flag Chrome: `python chrome_launcher.py --reset`

### Port Sudah Digunakan
```bash
# Kill process di port 5001
taskkill /f /im python.exe
# Lalu jalankan ulang
```

## Update Terbaru
- ✅ Fixed Unicode encoding error untuk Windows
- ✅ Port berubah dari 5000 ke 5001
- ✅ Invoice table dari 20 baris menjadi 10 baris
- ✅ Migrasi dari JSON ke SQLite database
- ✅ Chrome auto-launch dengan flag one-time