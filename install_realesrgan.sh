#!/bin/bash
set -e

echo "=== Installation Real-ESRGAN ==="
echo "PWD: $(pwd)"
echo "Python: $(which python3)"

# Méthode 1: Essayer git+https
echo "Tentative 1: Installation via git+https..."
if pip install git+https://github.com/xinntao/Real-ESRGAN.git 2>&1; then
    echo "✅ Installation via git réussie!"
    python3 -c "import realesrgan; from realesrgan import RealESRGANer; print('✅ Vérification OK')" && exit 0
fi

echo "❌ Installation via git échouée, tentative avec ZIP..."

# Méthode 2: Installation via ZIP
echo "Tentative 2: Installation via ZIP..."
python3 << 'PYTHON_SCRIPT'
import urllib.request
import zipfile
import tempfile
import shutil
import subprocess
import os
import sys

try:
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, 'Real-ESRGAN.zip')
    
    print('📥 Téléchargement ZIP (main)...')
    try:
        urllib.request.urlretrieve('https://github.com/xinntao/Real-ESRGAN/archive/main.zip', zip_path)
    except:
        print('📥 Téléchargement ZIP (master)...')
        urllib.request.urlretrieve('https://github.com/xinntao/Real-ESRGAN/archive/master.zip', zip_path)
    
    print('📦 Extraction...')
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(temp_dir)
    
    print('🔍 Recherche du dossier Real-ESRGAN...')
    for d in os.listdir(temp_dir):
        if 'Real-ESRGAN' in d:
            realesrgan_dir = os.path.join(temp_dir, d)
            print(f'✅ Dossier trouvé: {realesrgan_dir}')
            print('📦 Installation...')
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-e', realesrgan_dir])
            break
    else:
        raise Exception('Dossier Real-ESRGAN non trouvé')
    
    shutil.rmtree(temp_dir)
    print('✅ Installation depuis ZIP réussie!')
    
    # Vérification
    import realesrgan
    from realesrgan import RealESRGANer
    print('✅ Vérification OK!')
    
except Exception as e:
    print(f'❌ Erreur: {e}')
    if 'temp_dir' in locals():
        shutil.rmtree(temp_dir, ignore_errors=True)
    sys.exit(1)
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    echo "✅ Real-ESRGAN installé avec succès!"
    exit 0
else
    echo "❌ Échec de l'installation"
    exit 1
fi
