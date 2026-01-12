import cv2
import torch
import os
from pathlib import Path
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact
import numpy as np

class ImageRestorer:
    """Classe pour restaurer les images avec Real-ESRGAN"""
    
    def __init__(self, model_name='RealESRGAN_x4plus', gpu_id=None):
        """
        Initialiser le restaurateur
        
        Args:
            model_name: Nom du modèle ('RealESRGAN_x4plus', 'RealESRNet_x4plus', 
                       'RealESRGAN_x4plus_anime_6B', 'RealESRGAN_x2plus')
            gpu_id: ID du GPU (None = détection auto, 0+ = GPU spécifique, -1 = forcer CPU)
        """
        self.model_name = model_name
        
        # Détection automatique du GPU si gpu_id n'est pas spécifié
        if gpu_id is None:
            # Essayer de détecter automatiquement un GPU NVIDIA
            if torch.cuda.is_available():
                try:
                    num_gpus = torch.cuda.device_count()
                    if num_gpus > 0:
                        gpu_id = 0  # Utiliser le premier GPU disponible
                        gpu_name = torch.cuda.get_device_name(gpu_id)
                        print(f"✓ GPU NVIDIA détecté: {gpu_name} (ID: {gpu_id})")
                    else:
                        gpu_id = None
                        print("ℹ️  Aucun GPU détecté, utilisation du CPU")
                except Exception as e:
                    print(f"⚠️  Erreur lors de la détection GPU: {e}")
                    print("   → Utilisation du CPU")
                    gpu_id = None
            else:
                gpu_id = None
                print("ℹ️  CUDA non disponible, utilisation du CPU")
        elif gpu_id == -1:
            # Forcer l'utilisation du CPU
            gpu_id = None
            print("ℹ️  Mode CPU forcé")
        
        # Définir le device
        if gpu_id is not None and torch.cuda.is_available():
            try:
                # Vérifier que le GPU est accessible
                torch.cuda.set_device(gpu_id)
                test_tensor = torch.zeros(1).cuda(gpu_id)
                del test_tensor
                torch.cuda.empty_cache()
                
                self.device = torch.device(f'cuda:{gpu_id}')
                self.gpu_id = gpu_id
            except Exception as e:
                print(f"⚠️  Erreur d'accès au GPU {gpu_id}: {e}")
                print("   → Basculement vers CPU")
                self.device = torch.device('cpu')
                self.gpu_id = None
        else:
            self.device = torch.device('cpu')
            self.gpu_id = None
        
        self.upsampler = None
        self.model_path = None
        self.model = None
        self.netscale = 4
        self._load_model()
    
    def _load_model(self):
        """Charger le modèle Real-ESRGAN"""
        # URLs des modèles pré-entraînés
        model_urls = {
            'RealESRGAN_x4plus': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
            'RealESRNet_x4plus': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth',
            'RealESRGAN_x4plus_anime_6B': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth',
            'RealESRGAN_x2plus': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth',
        }
        
        self.model_path = f'models/{self.model_name}.pth'
        
        # Configurer le modèle selon le type
        if 'anime' in self.model_name:
            self.model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, 
                          num_block=6, num_grow_ch=32, scale=4)
            self.netscale = 4
        elif 'x2' in self.model_name:
            self.model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, 
                          num_block=23, num_grow_ch=32, scale=2)
            self.netscale = 2
        else:
            self.model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, 
                          num_block=23, num_grow_ch=32, scale=4)
            self.netscale = 4
        
        # Déplacer le modèle sur le device approprié
        self.model = self.model.to(self.device)
        
        # Télécharger le modèle s'il n'existe pas
        if not os.path.exists(self.model_path):
            os.makedirs('models', exist_ok=True)
            if self.model_name in model_urls:
                print(f"Téléchargement du modèle {self.model_name}...")
                self.model_path = load_file_from_url(
                    url=model_urls[self.model_name],
                    model_dir='models',
                    progress=True,
                    file_name=f'{self.model_name}.pth'
                )
                print("Téléchargement terminé!")
            else:
                raise ValueError(f"Modèle {self.model_name} non reconnu. Modèles disponibles: {list(model_urls.keys())}")
        
        # Initialiser l'upsampler
        use_half = False if self.device.type == 'cpu' else True
        
        self.upsampler = RealESRGANer(
            scale=self.netscale,
            model_path=self.model_path,
            model=self.model,
            tile=0,  # 0 = pas de tiling, augmenter si manque de mémoire
            tile_pad=10,
            pre_pad=0,
            half=use_half,
            device=self.device
        )
        
        # Vérifier que le modèle est bien sur le bon device
        device_info = str(self.device)
        if self.device.type == 'cuda':
            device_info += f" ({torch.cuda.get_device_name(self.gpu_id)})"
        
        print(f"✓ Modèle {self.model_name} chargé sur {device_info}")
        
        # Vérification supplémentaire pour GPU
        if self.device.type == 'cuda':
            try:
                # Vérifier que le modèle est bien sur GPU
                if hasattr(self.model, 'parameters'):
                    first_param = next(self.model.parameters())
                    if first_param.device.type == 'cuda':
                        print(f"✓ Modèle confirmé sur GPU {self.gpu_id}")
                    else:
                        print(f"⚠️  Attention: Le modèle semble être sur {first_param.device}, pas sur GPU")
            except Exception as e:
                print(f"⚠️  Impossible de vérifier l'emplacement du modèle: {e}")
    
    def restore_image(self, img_path, output_path=None, outscale=4):
        """
        Restaurer une image
        
        Args:
            img_path: Chemin de l'image d'entrée
            output_path: Chemin de sortie (None = auto)
            outscale: Facteur d'agrandissement final
        
        Returns:
            Chemin de l'image restaurée
        """
        # Lire l'image
        img = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
        
        if img is None:
            raise ValueError(f"Impossible de lire l'image: {img_path}")
        
        # Restaurer
        if self.upsampler is None:
            raise RuntimeError("L'upsampler n'est pas initialisé correctement.")
        try:
            output, _ = self.upsampler.enhance(img, outscale=outscale)
        except AttributeError as e:
            raise RuntimeError("L'upsampler ne possède pas la méthode 'enhance'. Vérifiez l'initialisation du modèle.") from e
        except RuntimeError as e:
            error_msg = str(e)
            if "not enough memory" in error_msg.lower() or "out of memory" in error_msg.lower():
                print(f"Erreur de mémoire détectée, passage en mode tile...")
                # Recrée l'upsampler avec tile pour éviter l'erreur de mémoire
                # Utiliser un tile plus petit pour CPU
                tile_size = 200 if self.device == torch.device('cpu') else 400
                self.upsampler = RealESRGANer(
                    scale=self.netscale,
                    model_path=self.model_path,
                    model=self.model,
                    tile=tile_size,  # passage en mode tile pour économiser la mémoire
                    tile_pad=10,
                    pre_pad=0,
                    half=False if self.device == torch.device('cpu') else True,
                    device=self.device
                )
                print(f"Mode tile activé (tile={tile_size}) pour économiser la mémoire")
                output, _ = self.upsampler.enhance(img, outscale=outscale)
            else:
                # Si ce n'est pas une erreur de mémoire, relancer l'erreur
                raise
        
        # Sauvegarder
        if output_path is None:
            path = Path(img_path)
            output_path = path.parent / f"{path.stem}_restored{path.suffix}"
        
        cv2.imwrite(str(output_path), output)
        print(f"Image restaurée: {output_path}")
        
        return output_path
    
    def restore_directory(self, input_dir, output_dir, extensions=['.jpg', '.jpeg', '.png', '.bmp']):
        """Restaurer toutes les images d'un répertoire"""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        restored = []
        
        for ext in extensions:
            for img_path in input_dir.glob(f"*{ext}"):
                try:
                    output_path = output_dir / f"{img_path.stem}_restored{img_path.suffix}"
                    result = self.restore_image(img_path, output_path)
                    restored.append(result)
                except Exception as e:
                    print(f"Erreur lors de la restauration de {img_path}: {e}")
        
        return restored
    
    def restore_video(self, video_path, output_path=None, fps=None):
        """Restaurer une vidéo frame par frame"""
        cap = cv2.VideoCapture(str(video_path))
        
        # Obtenir les propriétés de la vidéo
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps is None:
            fps = original_fps
        
        # Préparer l'output
        if output_path is None:
            path = Path(video_path)
            output_path = path.parent / f"{path.stem}_restored{path.suffix}"
        
        # Restaurer la première frame pour obtenir les nouvelles dimensions
        ret, first_frame = cap.read()
        if not ret:
            raise ValueError("Impossible de lire la vidéo")
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        if self.upsampler is None or not hasattr(self.upsampler, "enhance"):
            raise AttributeError("L'attribut 'upsampler' n'est pas défini ou ne possède pas la méthode 'enhance'.")
        
        restored_first, _ = self.upsampler.enhance(first_frame, outscale=4)
        new_height, new_width = restored_first.shape[:2]
        # Créer le writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # type: ignore[attr-defined]
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (new_width, new_height))

        # Traiter frame par frame
        frame_count = 0
        import time
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            restored_frame, _ = self.upsampler.enhance(frame, outscale=4)
            out.write(restored_frame)
            
            frame_count += 1
            if frame_count % 10 == 0 or frame_count == total_frames:
                elapsed_time = time.time() - start_time
                progress = (frame_count / total_frames) * 100
                fps_processing = frame_count / elapsed_time if elapsed_time > 0 else 0
                remaining_frames = total_frames - frame_count
                eta_seconds = remaining_frames / fps_processing if fps_processing > 0 else 0
                eta_minutes = eta_seconds / 60
                
                print(f"Progression: {frame_count}/{total_frames} frames ({progress:.1f}%) | "
                      f"Vitesse: {fps_processing:.2f} fps | "
                      f"Temps restant: ~{eta_minutes:.1f} min")
        
        elapsed_time = time.time() - start_time
        cap.release()
        out.release()
        
        print(f"\n✓ Vidéo restaurée: {output_path}")
        print(f"  Temps total: {elapsed_time/60:.2f} minutes")
        print(f"  Vitesse moyenne: {total_frames/elapsed_time:.2f} fps")
        return output_path

if __name__ == "__main__":
    # Exemple d'utilisation
    restorer = ImageRestorer(model_name='RealESRGAN_x4plus')
    
    # Restaurer une image
    restorer.restore_image("data/input/image.jpg", "data/output/image_restored.jpg")
    
    # Restaurer un répertoire
    # restorer.restore_directory("data/input", "data/output")