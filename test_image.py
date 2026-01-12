"""Script de test pour restaurer une image avec Real-ESRGAN"""
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

def main():
    # Chemin de l'image d'entrée
    input_image = "data/input/3.jpg"
    output_image = "data/output/test-gan_restored.jpg"
    
    # Vérifier que l'image existe
    if not Path(input_image).exists():
        print(f"Erreur: L'image {input_image} n'existe pas!")
        return
    
    # Créer le dossier de sortie s'il n'existe pas
    Path("data/output").mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Test de restauration d'image avec Real-ESRGAN")
    print("=" * 60)
    print(f"Image d'entrée: {input_image}")
    print(f"Image de sortie: {output_image}")
    
    try:
        # Sélectionner le modèle
        selected_model = select_model()
        
        # Vérifier la disponibilité du GPU
        print("\n" + "=" * 60)
        print("VÉRIFICATION DU GPU")
        print("=" * 60)
        
        # Vérifications détaillées du GPU
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA disponible dans PyTorch: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            gpu_id = 0  # Utiliser le premier GPU
            device_name = torch.cuda.get_device_name(gpu_id)
            device_props = torch.cuda.get_device_properties(gpu_id)
            total_memory = device_props.total_memory / 1024**3
            cuda_version = torch.version.cuda
            print(f"✓ GPU détecté: {device_name}")
            print(f"  ID du GPU: {gpu_id}")
            print(f"  Mémoire GPU totale: {total_memory:.2f} GB")
            print(f"  Version CUDA: {cuda_version}")
            print(f"  Compute Capability: {device_props.major}.{device_props.minor}")
            
            # Vérifier la mémoire disponible
            torch.cuda.empty_cache()
            allocated = torch.cuda.memory_allocated(gpu_id) / 1024**3
            reserved = torch.cuda.memory_reserved(gpu_id) / 1024**3
            free = total_memory - reserved
            print(f"  Mémoire libre: {free:.2f} GB")
            
            # Test rapide pour vérifier que le GPU fonctionne
            try:
                test_tensor = torch.randn(1, 1, 10, 10).cuda(gpu_id)
                del test_tensor
                torch.cuda.empty_cache()
                print(f"✓ Test GPU réussi - Le GPU est opérationnel")
            except Exception as e:
                print(f"⚠️  Avertissement: Erreur lors du test GPU: {e}")
                print("   Le traitement continuera mais pourrait être plus lent")
        else:
            gpu_id = None
            print("❌ Aucun GPU détecté")
            print("   Raisons possibles:")
            print("   - Pilotes NVIDIA non installés")
            print("   - PyTorch compilé sans support CUDA")
            print("   - GPU non compatible")
            print("   → Utilisation du CPU (plus lent)")
        
        # Initialiser le restaurateur
        print("\n" + "=" * 60)
        print("CHARGEMENT DU MODÈLE")
        print("=" * 60)
        print(f"Chargement du modèle {selected_model}...")
        restorer = ImageRestorer(model_name=selected_model, gpu_id=gpu_id)
        print()
        
        # Restaurer l'image
        print("=" * 60)
        print("RESTAURATION DE L'IMAGE")
        print("=" * 60)
        print("Restauration de l'image en cours...")
        result_path = restorer.restore_image(
            input_image, 
            output_image, 
            outscale=4
        )
        
        print()
        print("=" * 60)
        print("RESTAURATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 60)
        print(f"Image sauvegardée: {result_path}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nErreur lors de la restauration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

