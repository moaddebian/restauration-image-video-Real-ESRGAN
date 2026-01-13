#!/usr/bin/env python3
"""
Script d'installation de Real-ESRGAN pour le déploiement
Gère plusieurs méthodes d'installation en cas d'échec
"""
import subprocess
import sys
import os
import urllib.request
import zipfile
import tempfile
import shutil

def run_command(cmd, description):
    """Exécuter une commande et retourner True si succès"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} - Succès!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Échec")
        if e.stderr:
            print(f"Erreur: {e.stderr}")
        return False

def install_via_git():
    """Essayer d'installer via git+https"""
    return run_command(
        "pip install git+https://github.com/xinntao/Real-ESRGAN.git",
        "Installation via git+https"
    )

def install_via_zip():
    """Télécharger et installer depuis l'archive ZIP"""
    print("🔄 Installation via archive ZIP...")
    try:
        # Créer un répertoire temporaire
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "Real-ESRGAN.zip")
        
        # Télécharger l'archive
        print("📥 Téléchargement de l'archive ZIP...")
        urllib.request.urlretrieve(
            "https://github.com/xinntao/Real-ESRGAN/archive/master.zip",
            zip_path
        )
        
        # Extraire
        print("📦 Extraction de l'archive...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            extract_dir = os.path.join(temp_dir, "extracted")
            zip_ref.extractall(extract_dir)
        
        # Trouver le dossier Real-ESRGAN
        realesrgan_dir = os.path.join(extract_dir, "Real-ESRGAN-master")
        if not os.path.exists(realesrgan_dir):
            # Essayer avec un autre nom possible
            dirs = [d for d in os.listdir(extract_dir) if 'realesrgan' in d.lower()]
            if dirs:
                realesrgan_dir = os.path.join(extract_dir, dirs[0])
        
        # Installer
        print("📦 Installation depuis le dossier extrait...")
        result = run_command(
            f"pip install -e {realesrgan_dir}",
            "Installation depuis ZIP"
        )
        
        # Nettoyer
        shutil.rmtree(temp_dir, ignore_errors=True)
        return result
        
    except Exception as e:
        print(f"❌ Erreur lors de l'installation via ZIP: {e}")
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
        return False

def main():
    print("=" * 60)
    print("🔧 Installation de Real-ESRGAN")
    print("=" * 60)
    
    # Méthode 1: git+https (le plus rapide si git est disponible)
    if install_via_git():
        print("\n✅ Real-ESRGAN installé avec succès via git+https!")
        sys.exit(0)
    
    print("\n⚠️  Installation via git échouée, tentative avec ZIP...")
    
    # Méthode 2: Archive ZIP (ne nécessite pas git)
    if install_via_zip():
        print("\n✅ Real-ESRGAN installé avec succès via ZIP!")
        sys.exit(0)
    
    print("\n❌ Toutes les méthodes d'installation ont échoué!")
    print("Vérifiez votre connexion internet et les permissions d'écriture.")
    sys.exit(1)

if __name__ == "__main__":
    main()
