import sqlite3
import pandas as pd

# File database
src_db = "databases.db"
dest_db = "integrated_business_app.db"

# Koneksi ke database
src_conn = sqlite3.connect(src_db)
dest_conn = sqlite3.connect(dest_db)

# Ambil data dari tabel barang (source)
barang_data = pd.read_sql("SELECT * FROM barang;", src_conn)

# Mapping kolom barang -> products
mapped_data = pd.DataFrame({
    "id": barang_data["id"],
    "name": barang_data["nama"],
    "description": None,
    "created_at": None,
    "updated_at": None,
    "barcode": barang_data["kode"],
    "qr_code": None,
    "purchase_price": barang_data["harga_awal"],
    "selling_price": barang_data["harga_jual"],
    "initial_stock": barang_data["stok_awal"],
    "current_stock": barang_data["stok_akhir"],
    "profit": barang_data["profit"],
    "category": "Lainnya",
    "brand": None,
    "supplier": None,
    "minimum_stock": 5,
    "maximum_stock": 1000,
    "unit": "pcs",
    "weight": 0,
    "dimensions": None,
    "expiry_date": None,
    "total_sold": 0,
    "total_revenue": 0,
    "is_active": 1
})

# Simpan ke tabel products (append agar tidak hapus data lama)
mapped_data.to_sql("products", dest_conn, if_exists="append", index=False)

# Verifikasi jumlah data
total = pd.read_sql("SELECT COUNT(*) as total FROM products;", dest_conn)
print("Total produk sekarang:", total["total"].iloc[0])

# Tutup koneksi
src_conn.close()
dest_conn.close()
