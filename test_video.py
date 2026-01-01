"""Script de test pour restaurer une vidéo avec Real-ESRGAN"""
import sys
import torch
from pathlib import Path
from src.restore import ImageRestorer

def select_model():
    """Demander à l'utilisateur de choisir un modèle"""
    models = {
        '1': {
            'name': 'RealESRGAN_x4plus',
            'description': 'RealESRGAN_x4plus.pth - Modèle général (photos, images réelles)'
        },
        '2': {
            'name': 'RealESRGAN_x4plus_anime_6B',
            'description': 'RealESRGAN_x4plus_anime_6B.pth - Optimisé pour images anime/manga'
        },
        '3': {
            'name': 'RealESRNet_x4plus',
            'description': 'RealESRNet_x4plus.pth - Version alternative (ESRNet)'
        },
        '4': {
            'name': 'RealESRGAN_x2plus',
            'description': 'RealESRGAN_x2plus.pth - Agrandissement x2 (plus rapide)'
        }
    }
    
    print("\n" + "=" * 60)
    print("SÉLECTION DU MODÈLE")
    print("=" * 60)
    print("\nModèles disponibles :\n")
    for key, model_info in models.items():
        print(f"  {key}. {model_info['description']}")
    
    while True:
        choice = input("\nChoisissez un modèle (1-4) : ").strip()
        if choice in models:
            selected_model = models[choice]['name']
            print(f"\n✓ Modèle sélectionné : {models[choice]['description']}")
            return selected_model
        else:
            print("❌ Choix invalide. Veuillez entrer 1, 2, 3 ou 4.")

def select_video(input_dir):
    """Trouver et sélectionner une vidéo dans le dossier d'entrée"""
    input_dir = Path(input_dir)
    
    if not input_dir.exists():
        print(f"❌ Le dossier {input_dir} n'existe pas!")
        return None
    
    # Formats vidéo supportés
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(list(input_dir.glob(f"*{ext}")))
        video_files.extend(list(input_dir.glob(f"*{ext.upper()}")))
    
    if not video_files:
        print(f"\n❌ Aucune vidéo trouvée dans {input_dir}")
        print(f"   Formats supportés: {', '.join(video_extensions)}")
        print(f"\n💡 Placez une vidéo dans le dossier: {input_dir.absolute()}")
        return None
    
    print("\n" + "=" * 60)
    print("SÉLECTION DE LA VIDÉO")
    print("=" * 60)
    print(f"\nVidéos trouvées dans {input_dir.name} :\n")
    
    for i, video in enumerate(video_files, 1):
        size_mb = video.stat().st_size / (1024 * 1024)
        print(f"  {i}. {video.name} ({size_mb:.2f} MB)")
    
    if len(video_files) == 1:
        selected_video = video_files[0]
        print(f"\n✓ Utilisation de : {selected_video.name}")
        return selected_video
    else:
        while True:
            try:
                choice = int(input(f"\nChoisissez une vidéo (1-{len(video_files)}) : "))
                if 1 <= choice <= len(video_files):
                    selected_video = video_files[choice - 1]
                    print(f"\n✓ Vidéo sélectionnée : {selected_video.name}")
                    return selected_video
                else:
                    print(f"❌ Choix invalide. Veuillez entrer un nombre entre 1 et {len(video_files)}.")
            except ValueError:
                print("❌ Veuillez entrer un nombre valide.")

def get_video_info(video_path):
    """Obtenir les informations sur la vidéo"""
    import cv2
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        return None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    cap.release()
    
    return {
        'fps': fps,
        'width': width,
        'height': height,
        'total_frames': total_frames,
        'duration': duration
    }

def main():
    # Dossiers
    input_dir = "data/input"
    output_dir = "data/output"
    
    # Créer les dossiers s'ils n'existent pas
    Path(input_dir).mkdir(parents=True, exist_ok=True)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Test de restauration de vidéo avec Real-ESRGAN")
    print("=" * 60)
    print(f"Dossier d'entrée: {input_dir}")
    print(f"Dossier de sortie: {output_dir}")
    
    try:
        # Sélectionner la vidéo
        video_path = select_video(input_dir)
        if video_path is None:
            return
        
        # Afficher les informations de la vidéo
        print("\n" + "=" * 60)
        print("INFORMATIONS SUR LA VIDÉO")
        print("=" * 60)
        video_info = get_video_info(video_path)
        if video_info:
            print(f"Résolution: {video_info['width']}x{video_info['height']}")
            print(f"FPS: {video_info['fps']:.2f}")
            print(f"Nombre de frames: {video_info['total_frames']}")
            print(f"Durée: {video_info['duration']:.2f} secondes")
            print(f"\n⚠️  ATTENTION: La restauration peut prendre beaucoup de temps!")
            print(f"   Temps estimé: ~{video_info['total_frames'] * 0.5 / 60:.1f} minutes (sur CPU)")
        else:
            print("❌ Impossible de lire les informations de la vidéo")
            return
        
        # Sélectionner le modèle
        selected_model = select_model()
        
        # Vérifier la disponibilité du GPU
        print("\n" + "=" * 60)
        print("VÉRIFICATION DU GPU")
        print("=" * 60)
        if torch.cuda.is_available():
            gpu_id = 0  # Utiliser le premier GPU
            print(f"GPU détecté: {torch.cuda.get_device_name(gpu_id)}")
            print(f"Mémoire GPU disponible: {torch.cuda.get_device_properties(gpu_id).total_memory / 1024**3:.2f} GB")
        else:
            gpu_id = None
            print("Aucun GPU détecté, utilisation du CPU")
            print("⚠️  Le traitement sera plus lent sur CPU")
        
        # Initialiser le restaurateur
        print("\n" + "=" * 60)
        print("CHARGEMENT DU MODÈLE")
        print("=" * 60)
        print(f"Chargement du modèle {selected_model}...")
        restorer = ImageRestorer(model_name=selected_model, gpu_id=gpu_id)
        print()
        
        # Préparer le chemin de sortie
        output_path = Path(output_dir) / f"{video_path.stem}_restored{video_path.suffix}"
        
        # Restaurer la vidéo
        print("=" * 60)
        print("RESTAURATION DE LA VIDÉO")
        print("=" * 60)
        print(f"Vidéo d'entrée: {video_path.name}")
        print(f"Vidéo de sortie: {output_path.name}")
        print("\n⚠️  Le traitement peut prendre beaucoup de temps...")
        print("    La progression sera affichée toutes les 10 frames.\n")
        
        result_path = restorer.restore_video(
            video_path,
            output_path,
            fps=video_info['fps'] if video_info else None
        )
        
        print()
        print("=" * 60)
        print("RESTAURATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 60)
        print(f"Vidéo sauvegardée: {result_path}")
        size_mb = Path(result_path).stat().st_size / (1024 * 1024)
        print(f"Taille du fichier: {size_mb:.2f} MB")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n❌ Traitement interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur lors de la restauration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

