# Fajar Mandiri Store Tabungan

Aplikasi Tabungan Fajar Mandiri Store dengan Flask untuk tracking tabungan multi-penabung dalam Rupiah Indonesia.

## Fitur

- 📝 **Multi-Penabung**: Support untuk beberapa penabung sekaligus
- 💰 **Format Rupiah**: Otomatis format mata uang Indonesia
- 📊 **Statistik Real-time**: Total tabungan, jumlah entri, rata-rata per penabung
- 🔍 **Filter & Search**: Cari berdasarkan deskripsi, tanggal, dan nama penabung
- 📱 **Responsive UI**: Desain modern dengan Bootstrap 5
- 🗄️ **Database SQLite**: Penyimpanan permanen dengan lokasi eksternal
- 🎨 **Custom Icon**: Icon aplikasi custom berupa ayam jago low-poly untuk web dan executable

## Struktur Database

Database SQLite disimpan di lokasi eksternal: `../SavingsTrackerData/savings_tracker.db`

### Tabel: savings_entries
- `id` - Primary key (integer)
- `date` - Tanggal tabungan (date)
- `amount` - Jumlah tabungan (float)
- `description` - Deskripsi tabungan (text)
- `saver_name` - Nama penabung (varchar 100)
- `created_at` - Timestamp pembuatan (datetime)

## Instalasi Dependencies

```bash
pip install flask flask-sqlalchemy gunicorn
```

## Menjalankan Aplikasi

### Development Mode
```bash
python app.py
```

### Production Mode
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Kompilasi ke .EXE

### Menggunakan PyInstaller

1. Install dependencies:
```bash
pip install pyinstaller pillow
```

2. Menggunakan spec file (Recommended):
```bash
pyinstaller savings_tracker.spec
```

3. Manual command dengan icon:
```bash
pyinstaller --onefile --windowed --name="FajarMandiriStore" --icon="static/images/icon.ico" --add-data "templates;templates" --add-data "static;static" --hidden-import flask --hidden-import flask_sqlalchemy --hidden-import sqlalchemy --hidden-import werkzeug main.py
```

### Menggunakan cx_Freeze

1. Install cx_Freeze:
```bash
pip install cx_Freeze
```

2. Buat file `setup.py`:
```python
import sys
from cx_Freeze import setup, Executable

build_options = {
    "packages": ["flask", "flask_sqlalchemy", "sqlalchemy", "werkzeug"],
    "include_files": ["templates/", "static/"],
    "excludes": []
}

setup(
    name="SavingsTracker",
    version="1.0",
    description="Personal Savings Tracker",
    options={"build_exe": build_options},
    executables=[Executable("main.py", target_name="SavingsTracker.exe", base="Win32GUI")]
)
```

3. Build:
```bash
python setup.py build
```

## File Structure

```
SavingsTracker/
├── app.py                    # Main Flask application
├── main.py                   # Entry point for server
├── setup.py                  # cx_Freeze setup script
├── savings_tracker.spec      # PyInstaller spec file
├── templates/                # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── add_entry.html
│   └── edit_entry.html
├── static/                   # CSS, JS, assets
│   ├── css/style.css
│   ├── js/app.js
│   └── images/
│       ├── icon.svg         # SVG ayam jago icon
│       ├── icon.ico         # Windows ICO ayam jago icon  
│       └── favicon.ico      # Browser favicon
├── replit.md                # Project documentation
└── README.md                # This file

External:
../SavingsTrackerData/
└── savings_tracker.db       # SQLite database
```

## Database Location Logic

Aplikasi otomatis mendeteksi lokasi database:

- **Development**: Menggunakan folder di atas direktori project
- **PyInstaller .exe**: Menggunakan folder di atas executable
- **Portable**: Database akan dibuat otomatis jika tidak ada

## Browser Setup

Setelah menjalankan aplikasi, buka browser ke:
```
http://localhost:5000
```

## Teknologi

- **Backend**: Flask + SQLAlchemy
- **Database**: SQLite3
- **Frontend**: HTML5, Bootstrap 5, Font Awesome 6
- **JavaScript**: Vanilla JS dengan fitur modern
- **Styling**: CSS3 dengan gradient dan animasi

## Kompabilitas

- Python 3.7+
- Windows (untuk .exe)
- Linux/macOS (untuk development)
- Semua browser modern

## Dukungan

Database akan otomatis dimigrate jika ada perubahan struktur. Aplikasi akan membuat folder `SavingsTrackerData` secara otomatis jika belum ada.