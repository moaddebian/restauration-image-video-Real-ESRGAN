import cv2
import os
import numpy as np
from pathlib import Path
from PIL import Image

class DataPreprocessor:
    """Classe pour prétraiter les images et vidéos avant restauration"""
    
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_image(self, img_path):
        """Valider qu'une image peut être lue correctement"""
        try:
            img = cv2.imread(str(img_path))
            if img is None:
                return False
            return True
        except Exception as e:
            print(f"Erreur validation {img_path}: {e}")
            return False
    
    def resize_if_too_small(self, img, min_size=64):
        """Redimensionner si l'image est trop petite"""
        h, w = img.shape[:2]
        if h < min_size or w < min_size:
            scale = max(min_size/h, min_size/w)
            new_h, new_w = int(h*scale), int(w*scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        return img
    
    def normalize_image(self, img):
        """Normaliser l'image (0-255)"""
        img = np.clip(img, 0, 255)
        return img.astype(np.uint8)
    
    def preprocess_image(self, img_path, save=True):
        """Prétraiter une image"""
        if not self.validate_image(img_path):
            return None
        
        img = cv2.imread(str(img_path))
        
        # Redimensionner si nécessaire
        img = self.resize_if_too_small(img)
        
        # Normaliser
        img = self.normalize_image(img)
        
        if save:
            output_path = self.output_dir / img_path.name
            cv2.imwrite(str(output_path), img)
            return output_path
        
        return img
    
    def extract_video_frames(self, video_path, frame_rate=1):
        """Extraire les frames d'une vidéo"""
        video_name = Path(video_path).stem
        frames_dir = self.output_dir / f"{video_name}_frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * frame_rate)
        
        frame_count = 0
        saved_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frame = self.resize_if_too_small(frame)
                frame = self.normalize_image(frame)
                
                frame_path = frames_dir / f"frame_{saved_count:06d}.png"
                cv2.imwrite(str(frame_path), frame)
                saved_count += 1
            
            frame_count += 1
        
        cap.release()
        print(f"Extrait {saved_count} frames de {video_path}")
        return frames_dir
    
    def process_directory(self, extensions=['.jpg', '.jpeg', '.png', '.bmp']):
        """Traiter toutes les images d'un répertoire"""
        processed = []
        
        for ext in extensions:
            for img_path in self.input_dir.glob(f"*{ext}"):
                result = self.preprocess_image(img_path)
                if result:
                    processed.append(result)
                    print(f"Prétraité: {img_path.name}")
        
        return processed

if __name__ == "__main__":
    # Exemple d'utilisation
    preprocessor = DataPreprocessor("data/input", "data/preprocessed")
    processed_images = preprocessor.process_directory()
    print(f"Total d'images prétraitées: {len(processed_images)}")