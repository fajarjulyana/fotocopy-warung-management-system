import sqlite3
import requests
import re
import csv
import time
from bs4 import BeautifulSoup

def clean_price(text):
    nums = re.findall(r"\d[\d.]*", text)
    return int(nums[0].replace(".", "")) if nums else None

def get_shopee_price(keyword):
    url = f"https://shopee.co.id/search?keyword={keyword}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        prices = [clean_price(tag.text) for tag in soup.find_all("span")]
        prices = [p for p in prices if p]
        return min(prices) if prices else None
    except Exception:
        return None

def get_tokopedia_price(keyword):
    url = f"https://www.tokopedia.com/search?st=product&q={keyword}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        prices = [clean_price(tag.text) for tag in soup.find_all("span")]
        prices = [p for p in prices if p]
        return min(prices) if prices else None
    except Exception:
        return None

# Koneksi database
src_conn = sqlite3.connect("kasir.db")
src_cur = src_conn.cursor()
dst_conn = sqlite3.connect("databases.db")
dst_cur = dst_conn.cursor()

# Ambil kolom sumber & data
src_cur.execute("PRAGMA table_info(barang);")
src_cols = [col[1] for col in src_cur.fetchall()]
src_cur.execute(f"SELECT {', '.join(src_cols)} FROM barang ORDER BY id ASC")
src_data = src_cur.fetchall()

# Hapus data lama
dst_cur.execute("DELETE FROM barang;")
dst_conn.commit()

# Siapkan CSV log
with open("price_log.csv", mode="w", newline="", encoding="utf-8") as csvf:
    writer = csv.writer(csvf)
    writer.writerow([
        "id", "nama", "harga_beli", "harga_default", "shopee_price", "tokopedia_price",
        "harga_akhir", "profit"
    ])

    for row in src_data:
        r = dict(zip(src_cols, row))
        try:
            harga_beli = float(r.get("harga_beli") or 0)
        except ValueError:
            harga_beli = 0

        harga_awal = harga_beli
        default_harga_jual = round(harga_awal * 1.15, 2) if harga_awal else 0
        stok_awal = stok_akhir = 0
        kode_val = r.get("id")

        nama = r.get("nama", "").strip()
        print(f"Checking online prices for: {nama} ...")

        shopee_price = get_shopee_price(nama)
        tokopedia_price = get_tokopedia_price(nama)

        if shopee_price and tokopedia_price:
            harga_akhir = min(shopee_price, tokopedia_price)
        elif shopee_price:
            harga_akhir = shopee_price
        elif tokopedia_price:
            harga_akhir = tokopedia_price
        else:
            harga_akhir = default_harga_jual

        profit = round(harga_akhir - harga_awal, 2) if harga_awal else 0

        dst_cur.execute("""
            INSERT INTO barang
            (id, kode, nama, harga_awal, harga_jual, stok_awal, stok_akhir, profit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            kode_val, kode_val, nama, harga_awal, harga_akhir, stok_awal, stok_akhir, profit
        ))

        writer.writerow([
            kode_val, nama, harga_awal, default_harga_jual,
            shopee_price or "", tokopedia_price or "",
            harga_akhir, profit
        ])

        # Agar tidak terlalu cepat
        time.sleep(1)

dst_conn.commit()
src_conn.close()
dst_conn.close()

print(f"\nSelesai! Data dipindahkan, harga diperbarui, dan log disimpan di 'price_log.csv'.")
