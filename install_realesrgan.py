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
    print(f"   Commande: {cmd}")
    try:
        # Ne pas capturer la sortie pour voir les logs en temps réel
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True,
            text=True
        )
        print(f"✅ {description} - Succès!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Échec (code: {e.returncode})")
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
        
        # Télécharger l'archive (essayer main d'abord, puis master)
        print("📥 Téléchargement de l'archive ZIP...")
        zip_urls = [
            "https://github.com/xinntao/Real-ESRGAN/archive/main.zip",
            "https://github.com/xinntao/Real-ESRGAN/archive/master.zip"
        ]
        
        downloaded = False
        for zip_url in zip_urls:
            try:
                print(f"   Tentative: {zip_url}")
                urllib.request.urlretrieve(zip_url, zip_path)
                downloaded = True
                break
            except Exception as e:
                print(f"   Échec: {e}")
                continue
        
        if not downloaded:
            raise Exception("Impossible de télécharger l'archive ZIP")
        
        # Extraire
        print("📦 Extraction de l'archive...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            extract_dir = os.path.join(temp_dir, "extracted")
            zip_ref.extractall(extract_dir)
        
        # Trouver le dossier Real-ESRGAN (peut être Real-ESRGAN-main ou Real-ESRGAN-master)
        possible_names = ["Real-ESRGAN-main", "Real-ESRGAN-master"]
        realesrgan_dir = None
        for name in possible_names:
            candidate = os.path.join(extract_dir, name)
            if os.path.exists(candidate):
                realesrgan_dir = candidate
                break
        
        if not realesrgan_dir:
            # Chercher n'importe quel dossier contenant "realesrgan"
            dirs = [d for d in os.listdir(extract_dir) if 'realesrgan' in d.lower()]
            if dirs:
                realesrgan_dir = os.path.join(extract_dir, dirs[0])
            else:
                raise Exception(f"Dossier Real-ESRGAN non trouvé dans {extract_dir}")
        
        print(f"✅ Dossier trouvé: {realesrgan_dir}")
        
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

def verify_installation():
    """Vérifier que realesrgan est bien installé"""
    print("\n🔍 Vérification de l'installation...")
    try:
        import realesrgan
        print(f"✅ Module realesrgan trouvé: {realesrgan.__file__}")
        from realesrgan import RealESRGANer
        print("✅ Classe RealESRGANer importée avec succès!")
        return True
    except ImportError as e:
        print(f"❌ Échec de l'import: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 Installation de Real-ESRGAN")
    print("=" * 60)
    print(f"📁 Répertoire de travail: {os.getcwd()}")
    print(f"🐍 Python: {sys.executable}")
    print(f"📦 Version pip:")
    subprocess.run(["pip", "--version"], check=False)
    
    # Méthode 1: git+https (le plus rapide si git est disponible)
    if install_via_git():
        if verify_installation():
            print("\n✅ Real-ESRGAN installé et vérifié avec succès via git+https!")
            sys.exit(0)
        else:
            print("\n⚠️  Installation via git réussie mais vérification échouée, tentative avec ZIP...")
    
    print("\n⚠️  Installation via git échouée, tentative avec ZIP...")
    
    # Méthode 2: Archive ZIP (ne nécessite pas git)
    if install_via_zip():
        if verify_installation():
            print("\n✅ Real-ESRGAN installé et vérifié avec succès via ZIP!")
            sys.exit(0)
        else:
            print("\n⚠️  Installation via ZIP réussie mais vérification échouée!")
    
    print("\n❌ Toutes les méthodes d'installation ont échoué!")
    print("Vérifiez votre connexion internet et les permissions d'écriture.")
    print("\n🔍 Tentative d'import pour diagnostic:")
    try:
        import realesrgan
        print(f"Module trouvé à: {realesrgan.__file__}")
    except Exception as e:
        print(f"Erreur: {e}")
    sys.exit(1)

if __name__ == "__main__":
    main()
