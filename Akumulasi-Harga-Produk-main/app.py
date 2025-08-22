import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///akumulasi_harga.db"
# SQLite doesn't need pool configuration
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    
    db.create_all()
    
    # Import routes after app is configured
    import routes  # noqa: F401

if __name__ == '__main__':
    import webbrowser
    import threading
    import time
    import platform
    import subprocess

    def open_browser():
        time.sleep(2)  # Tunggu server Flask siap
        url = "http://127.0.0.1:5005/"
        
        # Fullscreen hanya untuk Windows (bisa disesuaikan)
        if platform.system() == "Windows":
            try:
                # Gunakan start chrome dalam mode fullscreen
                subprocess.Popen([
                    "cmd", "/c",
                    'start chrome --kiosk ' + url
                ])
            except Exception as e:
                print(f"Gagal membuka browser fullscreen: {e}")
                webbrowser.open(url)
        else:
            webbrowser.open(url)

    # Jalankan fungsi open_browser di thread terpisah
    threading.Thread(target=open_browser).start()

    app.run(host='0.0.0.0', port=5005, debug=True)

  # app.run(host='0.0.0.0', port=5005, debug=True, ssl_context=('ssl_cert.pem', 'ssl_key.pem'))