import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from database import db  # pastikan database.py berisi `db = SQLAlchemy()`

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure SQLite database (gunakan path absolut agar pasti)
db_path = os.path.join(os.getcwd(), "invoices.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Import routes setelah database setup
from routes import *

with app.app_context():
    # Jika database sudah ada, jangan create_all() untuk menghindari overwrite
    # db.create_all()  # Hapus atau komentar jika DB sudah ada

    # Logging tabel yang ada untuk debugging
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    logging.info(f"Tabel yang ada di database: {inspector.get_table_names()}")

if __name__ == '__main__':
    import webbrowser
    import threading
    import time
    import platform
    import subprocess

    def open_browser():
        time.sleep(2)  # Tunggu server Flask siap
        url = "http://127.0.0.1:5001/"
        
        # Fullscreen hanya untuk Windows (bisa disesuaikan)
        if platform.system() == "Windows":
            try:
                subprocess.Popen(["cmd", "/c", f'start chrome --kiosk {url}'])
            except Exception as e:
                print(f"Gagal membuka browser fullscreen: {e}")
                webbrowser.open(url)
        else:
            webbrowser.open(url)

    # Jalankan open_browser di thread terpisah
    threading.Thread(target=open_browser).start()

    app.run(host='0.0.0.0', port=5001, debug=True)
