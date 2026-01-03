"""
Script pour comparer visuellement l'image originale et restaurée
Version améliorée avec gestion automatique des chemins
"""

import cv2
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os

def find_project_root():
    """Trouver la racine du projet automatiquement"""
    current = Path(__file__).resolve().parent
    
    # Chercher le dossier 'data' en remontant dans l'arborescence
    for _ in range(5):  # Limite à 5 niveaux de remontée
        if (current / "data").exists():
            return current
        if current.parent == current:  # Racine du système atteinte
            break
        current = current.parent
    
    # Si on ne trouve pas, retourner le répertoire courant
    return Path.cwd()

def compare_images(original_path, restored_path, output_dir=None):
    """Afficher une comparaison côte à côte"""
    
    # Charger les images
    original = cv2.imread(str(original_path))
    restored = cv2.imread(str(restored_path))
    
    if original is None:
        print(f"❌ Impossible de charger : {original_path}")
        return False
    
    if restored is None:
        print(f"❌ Impossible de charger : {restored_path}")
        return False
    
    # Convertir BGR vers RGB pour matplotlib
    original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    restored_rgb = cv2.cvtColor(restored, cv2.COLOR_BGR2RGB)
    
    # Créer la figure de comparaison
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    # Image originale
    axes[0].imshow(original_rgb)
    axes[0].set_title(f'Original\n{original.shape[1]}x{original.shape[0]} pixels', 
                      fontsize=12, fontweight='bold')
    axes[0].axis('off')
    
    # Image restaurée
    axes[1].imshow(restored_rgb)
    axes[1].set_title(f'Restaurée (Real-ESRGAN)\n{restored.shape[1]}x{restored.shape[0]} pixels', 
                      fontsize=12, fontweight='bold')
    axes[1].axis('off')
    
    # Calculer le facteur d'agrandissement
    scale_factor = restored.shape[0] / original.shape[0]
    
    plt.suptitle(f'Comparaison - Facteur d\'agrandissement: {scale_factor:.1f}x', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    
    # Déterminer le dossier de sortie
    if output_dir is None:
        # Utiliser le répertoire courant par défaut
        output_file = Path('comparison_result.png')
    else:
        # Créer le dossier s'il n'existe pas
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / 'comparison_result.png'
    
    # Sauvegarder
    plt.savefig(str(output_file), dpi=150, bbox_inches='tight')
    print(f"✓ Comparaison sauvegardée : {output_file}")
    
    # Afficher
    plt.show()
    
    # Afficher les statistiques
    print("\n📊 Statistiques :")
    print(f"  Original     : {original.shape[1]:4d} x {original.shape[0]:4d} pixels")
    print(f"  Restaurée    : {restored.shape[1]:4d} x {restored.shape[0]:4d} pixels")
    print(f"  Agrandissement : {scale_factor:.2f}x")
    print(f"  Taille fichier original  : {Path(original_path).stat().st_size / 1024:.1f} KB")
    print(f"  Taille fichier restauré  : {Path(restored_path).stat().st_size / 1024:.1f} KB")
    
    return True

def main():
    print("=" * 60)
    print("  COMPARAISON D'IMAGES - AVANT/APRÈS")
    print("=" * 60)
    
    # Trouver la racine du projet
    project_root = find_project_root()
    print(f"\n📁 Racine du projet : {project_root}")
    
    # Définir les chemins
    input_dir = project_root / "data" / "input"
    output_dir = project_root / "data" / "output"
    comparaison_dir = project_root / "data" / "comparaison"
    
    # Vérifier que les dossiers existent
    if not input_dir.exists():
        print(f"\n❌ Le dossier {input_dir} n'existe pas!")
        print(f"   Chemin absolu : {input_dir.absolute()}")
        print("\n💡 Assurez-vous de :")
        print(f"   1. Être dans le bon projet")
        print(f"   2. Avoir créé le dossier data/input/")
        return False
    
    if not output_dir.exists():
        print(f"\n❌ Le dossier {output_dir} n'existe pas!")
        print(f"   Création du dossier...")
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Créer le dossier comparaison s'il n'existe pas
    comparaison_dir.mkdir(parents=True, exist_ok=True)
    
    # Trouver les images dans input
    input_images = list(input_dir.glob("*.png")) + list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.jpeg"))
    
    if not input_images:
        print(f"\n❌ Aucune image trouvée dans {input_dir}")
        print(f"   Chemin absolu : {input_dir.absolute()}")
        print("\n💡 Fichiers présents dans le dossier :")
        all_files = list(input_dir.glob("*"))
        if all_files:
            for f in all_files:
                print(f"   - {f.name}")
        else:
            print("   (dossier vide)")
        print("\n   Placez une image (.png, .jpg, .jpeg) dans ce dossier.")
        return False
    
    print(f"\n🔍 Images trouvées dans {input_dir.name} :")
    for i, img in enumerate(input_images, 1):
        print(f"  {i}. {img.name}")
    
    # Si une seule image, l'utiliser automatiquement
    if len(input_images) == 1:
        original_path = input_images[0]
        print(f"\n✓ Utilisation de : {original_path.name}")
    else:
        # Demander à l'utilisateur de choisir
        try:
            choice = int(input(f"\nChoisissez une image (1-{len(input_images)}) : "))
            original_path = input_images[choice - 1]
        except (ValueError, IndexError):
            print("❌ Choix invalide")
            return False
    
    # Chercher l'image restaurée correspondante
    restored_name = f"{original_path.stem}_restored{original_path.suffix}"
    restored_path = output_dir / restored_name
    
    if not restored_path.exists():
        print(f"\n❌ Image restaurée non trouvée : {restored_path}")
        print(f"   Chemin absolu : {restored_path.absolute()}")
        print("\n💡 Vous devez d'abord restaurer l'image avec :")
        print(f"   python test_image.py")
        print(f"   ou")
        print(f"   python -m src.restore")
        return False
    
    print(f"✓ Image restaurée trouvée : {restored_path.name}")
    
    # Comparer
    print("\n🔄 Génération de la comparaison...")
    return compare_images(original_path, restored_path, output_dir=comparaison_dir)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)