import sys
from cx_Freeze import setup, Executable

# Dependencies
build_options = {
    "packages": [
        "flask", 
        "flask_sqlalchemy", 
        "sqlalchemy", 
        "werkzeug", 
        "jinja2",
        "logging",
        "datetime",
        "pathlib"
    ],
    "include_files": [
        "templates/",
        "static/",
        ("static/images/icon.svg", "icon.svg")
    ],
    "excludes": [
        "tkinter",
        "unittest", 
        "pydoc_data",
        "xml"
    ]
}

# Executable configuration
executables = [
    Executable(
        "main.py",
        target_name="FajarMandiriStore.exe",
        base="Win32GUI" if sys.platform == "win32" else None,
        icon="static/images/icon.ico" if sys.platform == "win32" else None
    )
]

setup(
    name="Fajar Mandiri Store Tabungan",
    version="1.0.0",
    description="Fajar Mandiri Store Tabungan - Aplikasi Tabungan Toko",
    author="Fajar Mandiri Store",
    options={"build_exe": build_options},
    executables=executables
)