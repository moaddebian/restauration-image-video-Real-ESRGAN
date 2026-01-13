#!/usr/bin/env python
"""Script simple pour installer Real-ESRGAN"""
import subprocess
import sys
import os

# Forcer l'affichage immédiat
sys.stdout.flush()
sys.stderr.flush()

print("=" * 60)
print("Installation Real-ESRGAN")
print("=" * 60)
print(f"Python: {sys.executable}")
print(f"PWD: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'N/A')}")
print(f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'N/A')}")
sys.stdout.flush()

# Méthode 1: git+https
print("\n[1/2] Tentative installation via git+https...")
try:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "git+https://github.com/xinntao/Real-ESRGAN.git"],
        check=True,
        capture_output=False
    )
    # Vérifier
    import realesrgan
    from realesrgan import RealESRGANer
    print("✅ Real-ESRGAN installé via git!")
    sys.exit(0)
except Exception as e:
    print(f"❌ Échec: {e}")

# Méthode 2: ZIP
print("\n[2/2] Tentative installation via ZIP...")
import urllib.request
import zipfile
import tempfile
import shutil

temp_dir = None
try:
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "Real-ESRGAN.zip")
    
    # Télécharger
    print("Téléchargement ZIP...")
    try:
        urllib.request.urlretrieve("https://github.com/xinntao/Real-ESRGAN/archive/main.zip", zip_path)
    except:
        urllib.request.urlretrieve("https://github.com/xinntao/Real-ESRGAN/archive/master.zip", zip_path)
    
    # Extraire
    print("Extraction...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(temp_dir)
    
    # Trouver et installer
    for d in os.listdir(temp_dir):
        if "Real-ESRGAN" in d:
            realesrgan_dir = os.path.join(temp_dir, d)
            print(f"Installation depuis: {realesrgan_dir}")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", realesrgan_dir],
                check=True
            )
            break
    
    # Vérifier
    import realesrgan
    from realesrgan import RealESRGANer
    print("✅ Real-ESRGAN installé via ZIP!")
    
    if temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Échec installation ZIP: {e}")
    if temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)
    sys.exit(1)
