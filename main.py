import cv2
import numpy as np
from pathlib import Path
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
import json

class ImageEvaluator:
    """Classe pour évaluer la qualité des images restaurées"""
    
    def __init__(self):
        self.results = {}
    
    def calculate_psnr(self, img1, img2):
        """Calculer le PSNR (Peak Signal-to-Noise Ratio)"""
        # Les images doivent avoir la même taille
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        return psnr(img1, img2, data_range=255)
    
    def calculate_ssim(self, img1, img2):
        """Calculer le SSIM (Structural Similarity Index)"""
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        # Convertir en niveaux de gris pour le calcul
        if len(img1.shape) == 3:
            img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        else:
            img1_gray = img1
            img2_gray = img2
        
        return ssim(img1_gray, img2_gray, data_range=255)
    
    def calculate_mse(self, img1, img2):
        """Calculer le MSE (Mean Squared Error)"""
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        return mean_squared_error(img1.flatten(), img2.flatten())
    
    def calculate_sharpness(self, img):
        """Calculer la netteté de l'image (variance du Laplacien)"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        return sharpness
    
    def evaluate_restoration(self, original_path, restored_path, reference_path=None):
        """
        Évaluer une image restaurée
        
        Args:
            original_path: Image originale basse résolution
            restored_path: Image restaurée
            reference_path: Image de référence haute résolution (optionnel)
        
        Returns:
            Dictionnaire des métriques
        """
        original = cv2.imread(str(original_path))
        restored = cv2.imread(str(restored_path))
        
        if original is None or restored is None:
            raise ValueError("Impossible de charger les images")
        
        metrics = {
            'original_size': original.shape[:2],
            'restored_size': restored.shape[:2],
            'scale_factor': restored.shape[0] / original.shape[0],
            'original_sharpness': self.calculate_sharpness(original),
            'restored_sharpness': self.calculate_sharpness(restored)
        }
        
        # Si une image de référence est fournie, calculer les métriques comparatives
        if reference_path:
            reference = cv2.imread(str(reference_path))
            if reference is not None:
                metrics['psnr'] = self.calculate_psnr(reference, restored)
                metrics['ssim'] = self.calculate_ssim(reference, restored)
                metrics['mse'] = self.calculate_mse(reference, restored)
        
        return metrics
    
    def evaluate_directory(self, original_dir, restored_dir, reference_dir=None, save_report=True):
        """Évaluer toutes les images d'un répertoire"""
        original_dir = Path(original_dir)
        restored_dir = Path(restored_dir)
        
        if reference_dir:
            reference_dir = Path(reference_dir)
        
        all_metrics = []
        
        for original_path in original_dir.glob("*.png"):
            # Trouver l'image restaurée correspondante
            restored_name = f"{original_path.stem}_restored{original_path.suffix}"
            restored_path = restored_dir / restored_name
            
            if not restored_path.exists():
                print(f"Image restaurée introuvable: {restored_path}")
                continue
            
            # Trouver l'image de référence si disponible
            reference_path = None
            if reference_dir:
                reference_path = reference_dir / original_path.name
                if not reference_path.exists():
                    reference_path = None
            
            try:
                metrics = self.evaluate_restoration(original_path, restored_path, reference_path)
                metrics['filename'] = original_path.name
                all_metrics.append(metrics)
                print(f"Évalué: {original_path.name}")
            except Exception as e:
                print(f"Erreur lors de l'évaluation de {original_path}: {e}")
        
        # Calculer les moyennes
        summary = self._calculate_summary(all_metrics)
        
        if save_report:
            self._save_report(all_metrics, summary)
        
        return all_metrics, summary
    
    def _calculate_summary(self, metrics_list):
        """Calculer les statistiques résumées"""
        if not metrics_list:
            return {}
        
        summary = {
            'total_images': len(metrics_list),
            'avg_scale_factor': np.mean([m['scale_factor'] for m in metrics_list]),
            'avg_original_sharpness': np.mean([m['original_sharpness'] for m in metrics_list]),
            'avg_restored_sharpness': np.mean([m['restored_sharpness'] for m in metrics_list]),
            'sharpness_improvement': 0
        }
        
        summary['sharpness_improvement'] = (
            (summary['avg_restored_sharpness'] - summary['avg_original_sharpness']) 
            / summary['avg_original_sharpness'] * 100
        )
        
        # Ajouter les métriques PSNR/SSIM si disponibles
        psnr_values = [m['psnr'] for m in metrics_list if 'psnr' in m]
        ssim_values = [m['ssim'] for m in metrics_list if 'ssim' in m]
        
        if psnr_values:
            summary['avg_psnr'] = np.mean(psnr_values)
            summary['std_psnr'] = np.std(psnr_values)
        
        if ssim_values:
            summary['avg_ssim'] = np.mean(ssim_values)
            summary['std_ssim'] = np.std(ssim_values)
        
        return summary
    
    def _save_report(self, metrics_list, summary, output_path="evaluation_report.json"):
        """Sauvegarder le rapport d'évaluation"""
        report = {
            'summary': summary,
            'detailed_metrics': metrics_list
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Rapport sauvegardé: {output_path}")
    
    def visualize_comparison(self, original_path, restored_path, reference_path=None):
        """Visualiser la comparaison entre images"""
        original = cv2.imread(str(original_path))
        restored = cv2.imread(str(restored_path))
        
        original = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        restored = cv2.cvtColor(restored, cv2.COLOR_BGR2RGB)
        
        if reference_path:
            reference = cv2.imread(str(reference_path))
            if reference is None:
                raise ValueError(f"Impossible de charger l'image de référence: {reference_path}")
            
            if len(reference.shape) == 3 and reference.shape[2] == 3:
                reference = cv2.cvtColor(reference, cv2.COLOR_BGR2RGB)
            elif len(reference.shape) == 2:
                # Image en niveaux de gris, convertir en RGB
                reference = cv2.cvtColor(reference, cv2.COLOR_GRAY2RGB)
            
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            axes[0].imshow(original)
            axes[0].set_title('Original (Basse Résolution)')
            axes[0].axis('off')
            
            axes[1].imshow(restored)
            axes[1].set_title('Restaurée')
            axes[1].axis('off')
            
            axes[2].imshow(reference)
            axes[2].set_title('Référence (Haute Résolution)')
            axes[2].axis('off')
        else:
            fig, axes = plt.subplots(1, 2, figsize=(12, 6))
            axes[0].imshow(original)
            axes[0].set_title('Original (Basse Résolution)')
            axes[0].axis('off')
            
            axes[1].imshow(restored)
            axes[1].set_title('Restaurée')
            axes[1].axis('off')
        
        plt.tight_layout()
        plt.savefig('comparison.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        print("Visualisation sauvegardée: comparison.png")

if __name__ == "__main__":
    # Exemple d'utilisation
    evaluator = ImageEvaluator()
    
    # Évaluer une image
    metrics = evaluator.evaluate_restoration(
        "data/input/image.jpg",
        "data/output/image_restored.jpg"
    )
    
    print("Métriques:", json.dumps(metrics, indent=2))
    
    # Visualiser
    evaluator.visualize_comparison(
        "data/input/image.jpg",
        "data/output/image_restored.jpg"
    )