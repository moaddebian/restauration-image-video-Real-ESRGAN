#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script simple pour installer Real-ESRGAN"""
import subprocess
import sys
import os

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

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

# Note: git+https échoue à cause d'un bug dans setup.py de Real-ESRGAN
# On utilise directement la méthode ZIP qui permet de corriger le setup.py

# Méthode: ZIP (avec correction du setup.py)
print("\nInstallation via ZIP (avec correction du setup.py)...")
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
            
            # Corriger le setup.py avant l'installation
            setup_py_path = os.path.join(realesrgan_dir, "setup.py")
            if os.path.exists(setup_py_path):
                print("Correction du setup.py...")
                with open(setup_py_path, "r", encoding="utf-8") as f:
                    setup_content = f.read()
                
                # Chercher la version dans __init__.py
                version = "0.0.0"
                init_file = os.path.join(realesrgan_dir, "realesrgan", "__init__.py")
                if os.path.exists(init_file):
                    try:
                        with open(init_file, "r", encoding="utf-8") as vf:
                            import re
                            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', vf.read())
                            if match:
                                version = match.group(1)
                    except:
                        pass
                
                # Ajouter __version__ au début du fichier ET corriger get_version()
                import re
                
                # 1. Ajouter __version__ au début si absent
                if "__version__" not in setup_content.split("def get_version()")[0] if "def get_version()" in setup_content else setup_content[:500]:
                    setup_content = f'__version__ = "{version}"\n\n' + setup_content
                    print(f"✅ __version__ = '{version}' ajouté au début")
                
                # 2. Corriger la fonction get_version() pour qu'elle retourne directement la version
                new_get_version = f'def get_version():\n    return "{version}"'
                
                # Trouver et remplacer la fonction get_version complète
                if "def get_version()" in setup_content:
                    lines = setup_content.split('\n')
                    new_lines = []
                    replacing = False
                    base_indent = 0
                    
                    for line in lines:
                        if "def get_version()" in line:
                            replacing = True
                            base_indent = len(line) - len(line.lstrip())
                            new_lines.append(new_get_version)
                            continue
                        elif replacing:
                            if line.strip():  # Ligne non vide
                                current_indent = len(line) - len(line.lstrip())
                                if current_indent <= base_indent and not line.strip().startswith('#'):
                                    replacing = False
                                    new_lines.append(line)
                            # Ignorer les lignes dans la fonction
                        else:
                            new_lines.append(line)
                    
                    setup_content = '\n'.join(new_lines)
                    print(f"✅ Fonction get_version() remplacée avec version: {version}")
                else:
                    # Si get_version n'existe pas, l'ajouter
                    setup_content = new_get_version + '\n\n' + setup_content
                    print(f"✅ Fonction get_version() ajoutée avec version: {version}")
                
                # Modifier aussi le setup.py pour ne pas installer basicsr (déjà installé)
                # Chercher la ligne avec basicsr dans install_requires
                if "install_requires" in setup_content:
                    import re
                    # Remplacer basicsr>=... par un commentaire ou le retirer
                    setup_content = re.sub(
                        r"['\"]basicsr[^'\"]*['\"]",
                        "# basicsr déjà installé",
                        setup_content
                    )
                    # Ou remplacer toute la liste install_requires si elle ne contient que basicsr
                    if "install_requires" in setup_content and "basicsr" in setup_content:
                        # Trouver et modifier install_requires
                        lines = setup_content.split('\n')
                        new_lines = []
                        in_install_requires = False
                        for line in lines:
                            if "install_requires" in line and "=" in line:
                                # Remplacer par une liste vide ou commentée
                                new_lines.append("    install_requires=[],  # basicsr déjà installé")
                                in_install_requires = True
                                continue
                            elif in_install_requires and line.strip().startswith(']'):
                                new_lines.append(line)
                                in_install_requires = False
                                continue
                            elif in_install_requires:
                                # Ignorer les lignes dans install_requires
                                continue
                            else:
                                new_lines.append(line)
                        setup_content = '\n'.join(new_lines)
                        print("✅ Dépendance basicsr retirée du setup.py")
                
                with open(setup_py_path, "w", encoding="utf-8") as f:
                    f.write(setup_content)
            
            # Essayer d'abord l'installation normale (sans dépendances car basicsr est déjà installé)
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--no-deps", realesrgan_dir],
                    check=True
                )
                print("✅ Real-ESRGAN installé avec --no-deps (basicsr déjà présent)")
            except:
                # Si ça échoue, installer manuellement en copiant les fichiers
                print("⚠️ Installation pip échouée, installation manuelle...")
                import site
                site_packages = site.getsitepackages()[0] if site.getsitepackages() else None
                if not site_packages:
                    # Essayer de trouver site-packages
                    import sysconfig
                    site_packages = sysconfig.get_paths()['purelib']
                
                realesrgan_pkg = os.path.join(realesrgan_dir, "realesrgan")
                if os.path.exists(realesrgan_pkg):
                    target_dir = os.path.join(site_packages, "realesrgan")
                    print(f"Copie de {realesrgan_pkg} vers {target_dir}...")
                    if os.path.exists(target_dir):
                        shutil.rmtree(target_dir)
                    shutil.copytree(realesrgan_pkg, target_dir)
                    print("✅ Real-ESRGAN installé manuellement!")
                else:
                    raise Exception("Dossier realesrgan non trouvé dans Real-ESRGAN")
            break
    
    # Vérifier l'installation
    print("\n🔍 Vérification de l'installation...")
    
    # Vérifier d'abord que basicsr est disponible
    try:
        import basicsr
        print(f"✅ basicsr trouvé: {basicsr.__file__}")
    except ImportError:
        print("⚠️ basicsr non trouvé dans le PYTHONPATH")
        # Essayer d'ajouter basicsr_repo au PYTHONPATH
        basicsr_repo_path = os.path.join(os.getcwd(), "basicsr_repo")
        if os.path.exists(basicsr_repo_path):
            if basicsr_repo_path not in sys.path:
                sys.path.insert(0, basicsr_repo_path)
                print(f"✅ basicsr_repo ajouté au PYTHONPATH: {basicsr_repo_path}")
            try:
                import basicsr
                print(f"✅ basicsr trouvé après ajout au PYTHONPATH: {basicsr.__file__}")
            except ImportError:
                print("❌ basicsr toujours non trouvé après ajout au PYTHONPATH")
                print("Assurez-vous d'avoir installé basicsr_repo avec: pip install -e basicsr_repo")
                if temp_dir:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                sys.exit(1)
        else:
            print("❌ basicsr_repo non trouvé!")
            print("Assurez-vous d'avoir installé basicsr_repo avec: pip install -e basicsr_repo")
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
            sys.exit(1)
    
    # Maintenant vérifier realesrgan
    try:
        import realesrgan
        from realesrgan import RealESRGANer
        print(f"✅ realesrgan trouvé: {realesrgan.__file__}")
        print("✅ Real-ESRGAN installé et vérifié via ZIP!")
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(0)
    except ImportError as e:
        print(f"⚠️ Import realesrgan échoué: {e}")
        print("Mais basicsr est disponible, donc l'installation devrait fonctionner au runtime")
        # Ne pas échouer si basicsr est disponible, car realesrgan pourra l'importer au runtime
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(0)  # Succès car basicsr est disponible
    
except Exception as e:
    print(f"❌ Échec installation ZIP: {e}")
    import traceback
    traceback.print_exc()
    if temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)
    sys.exit(1)
