# hooks/hook-pyzbar.py
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

# Collect all dynamic libraries (DLLs) from pyzbar
binaries = collect_dynamic_libs('pyzbar')

# Also collect any data files
datas = collect_data_files('pyzbar')