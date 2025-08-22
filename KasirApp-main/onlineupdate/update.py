import sqlite3

# Lokasi database
db_path = "databases.db"  # ganti sesuai lokasi file

# Koneksi ke database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Update semua stok
cursor.execute("""
    UPDATE barang
    SET stok_awal = 24,
        stok_akhir = 20
""")

# Simpan perubahan
conn.commit()
conn.close()

print("Semua stok_awal diubah menjadi 24 dan stok_akhir menjadi 20.")
