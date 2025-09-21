import PyInstaller.__main__
import os
import shutil
import sys
import platform
import subprocess
import argparse
import importlib

def check_database_setup():
    """Check if database is properly set up"""
    print("Checking database setup...")
    
    # Check if config file exists
    if not os.path.exists('config.ini'):
        print("❌ config.ini not found. Run setup_database.py first.")
        return False
    
    # Test database connection
    try:
        from database import test_connection
        return test_connection()
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    
    required = [
        'mysql.connector', 'reportlab', 'PIL', 'tkinter', 
        'tkcalendar', 'cv2', 'pyzbar'
    ]
    
    missing = []
    for package in required:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError:
            missing.append(package)
            print(f"✗ {package}")
    
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install them with: pip install mysql-connector-python reportlab pillow tkcalendar opencv-python pyzbar")
        return False
    
    print("All dependencies found!")
    return True

def get_target_os():
    """Get target OS from user input or detect current OS"""
    parser = argparse.ArgumentParser(description='Build BillingSoftware for different platforms')
    parser.add_argument('--os', choices=['windows', 'linux', 'current', 'all'], 
                       default='current', help='Target operating system')
    parser.add_argument('--skip-deps', action='store_true', 
                       help='Skip dependency check')
    parser.add_argument('--skip-db-check', action='store_true',
                       help='Skip database setup check')
    args = parser.parse_args()
    
    if args.os == 'current':
        current_os = platform.system().lower()
        if current_os == 'windows':
            return 'windows', args.skip_deps, args.skip_db_check
        elif current_os == 'linux':
            return 'linux', args.skip_deps, args.skip_db_check
        else:
            return 'other', args.skip_deps, args.skip_db_check
    elif args.os == 'all':
        return 'all', args.skip_deps, args.skip_db_check
    else:
        return args.os, args.skip_deps, args.skip_db_check

def build_windows(skip_deps=False, skip_db_check=False):
    """Build Windows executable"""
    print("Building Windows executable...")
    
    if not skip_deps and not check_dependencies():
        print("Dependency check failed. Use --skip-deps to build anyway.")
        return False
    
    if not skip_db_check and not check_database_setup():
        print("Database setup check failed. Use --skip-db-check to build anyway.")
        return False
    
    # Clean up previous builds
    for dir_path in ['dist', 'build', '__pycache__']:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
    
    # Define the build options
    options = [
        'main.py',
        '--name=BillingSoftware',
        '--onefile',
        '--windowed',
        '--add-data=license.key:.',
        '--add-data=config.ini:.',
        '--add-data=database.py:.',
    ]
    
    # Add additional data files if they exist
    additional_files = ['settings.ini', 'requirements.txt', 'README.md']
    for file in additional_files:
        if os.path.exists(file):
            options.append(f'--add-data={file}:.')
    
    # Add hidden imports
    hidden_imports = [
        'mysql.connector', 'reportlab', 'reportlab.pdfbase.ttfonts', 
        'reportlab.lib', 'reportlab.platypus', 'pyzbar', 'PIL', 
        'tkinter', 'tkcalendar', 'uuid', 'hashlib', 'json', 'os', 
        'sys', 'datetime', 'tempfile', 'tkinter.filedialog', 
        'tkinter.messagebox', 'tkinter.simpledialog', 'tkinter.scrolledtext', 
        'tkinter.ttk', 'cv2', 'pyzbar.pyzbar', 'mysql.connector.connection',
        'mysql.connector.pooling', 'mysql.connector.cursor', 'mysql.connector.errors',
        'mysql.connector.locales', 'configparser'
    ]
    
    for imp in hidden_imports:
        options.append(f'--hidden-import={imp}')
    
    print("Building with options:", ' '.join(options))
    
    try:
        PyInstaller.__main__.run(options)
        
        # Copy necessary files to dist directory
        if os.path.exists('dist'):
            files_to_copy = ['license.key', 'config.ini', 'database.py']
            for file in files_to_copy:
                if os.path.exists(file):
                    shutil.copy(file, 'dist')
        
        print("Windows build completed!")
        
        # Check if executable was created
        exe_path = os.path.join('dist', 'BillingSoftware.exe')
        
        if os.path.exists(exe_path):
            print(f"✓ Executable created at: {exe_path}")
            print(f"✓ Size: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
            
            # Create a batch file for easy execution
            with open(os.path.join('dist', 'run.bat'), 'w') as f:
                f.write("@echo off\n")
                f.write("echo Starting BillingSoftware...\n")
                f.write("BillingSoftware.exe\n")
                f.write("pause\n")
            
            return True
        else:
            print("✗ Executable not found.")
            return False
        
    except Exception as e:
        print(f"✗ Error during Windows build: {e}")
        return False

# [Rest of the build functions remain similar but with skip_db_check parameter added]

def main():
    target_os, skip_deps, skip_db_check = get_target_os()
    
    if target_os == 'windows':
        build_windows(skip_deps, skip_db_check)
    # [Other OS build calls would go here]

if __name__ == '__main__':
    main()