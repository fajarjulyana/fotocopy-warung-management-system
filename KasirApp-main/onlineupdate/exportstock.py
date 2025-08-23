import sqlite3
import math

# Fungsi pembulatan ke atas ke kelipatan 500
def bulatkan_ke_atas_500(n):
    return math.ceil(n / 500) * 500

# Path database
src_db = "kasir.db"       # database sumber
dst_db = "databases.db"   # database tujuan

# Koneksi ke kedua database
src_conn = sqlite3.connect(src_db)
src_cur = src_conn.cursor()

dst_conn = sqlite3.connect(dst_db)
dst_cur = dst_conn.cursor()

# Ambil struktur kolom sumber
src_cur.execute("PRAGMA table_info(barang);")
src_columns = [col[1] for col in src_cur.fetchall()]
print("Kolom sumber:", src_columns)

# Ambil semua data dari sumber, urutkan berdasarkan id terkecil
src_cur.execute(f"SELECT {', '.join(src_columns)} FROM barang ORDER BY id ASC")
src_data = src_cur.fetchall()

# Hapus data lama di tujuan
dst_cur.execute("DELETE FROM barang;")
dst_conn.commit()

# Masukkan data ke tujuan sesuai mapping
for row in src_data:
    row_dict = dict(zip(src_columns, row))

    # id dan kode sama
    id_val = str(row_dict.get('id') or "")
    kode_val = id_val  # kode sama seperti id

    # Lewati jika id atau kode kurang dari 5 digit
    if len(id_val) < 5 or len(str(kode_val)) < 5:
        continue

    # Konversi harga_beli ke float
    try:
        harga_beli = float(row_dict.get('harga_beli') or 0)
    except ValueError:
        harga_beli = 0

    harga_awal = harga_beli

    # Harga jual = harga beli + 16%, lalu dibulatkan ke atas kelipatan 500
    if harga_beli:
        harga_jual = bulatkan_ke_atas_500(harga_beli * 1.16)
    else:
        harga_jual = 0

    stok_awal = 12  # 1 lusin
    stok_akhir = 0
    profit = harga_jual - harga_awal if harga_awal else 0

    # Insert ke tabel tujuan
    dst_cur.execute("""
        INSERT INTO barang (id, kode, nama, harga_awal, harga_jual, stok_awal, stok_akhir, profit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_val,
        kode_val,
        row_dict.get('nama'),
        harga_awal,
        harga_jual,
        stok_awal,
        stok_akhir,
        profit
    ))

dst_conn.commit()

# Cek 5 data pertama di tujuan
dst_cur.execute("SELECT * FROM barang ORDER BY id ASC LIMIT 5")
print("\nContoh data setelah import:")
for row in dst_cur.fetchall():
    print(row)

print(f"\n{len(src_data)} baris berhasil dipindahkan dan diperbarui (setelah filter).")

# Tutup koneksi
src_conn.close()
dst_conn.close()
