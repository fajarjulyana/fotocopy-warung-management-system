from app import app

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