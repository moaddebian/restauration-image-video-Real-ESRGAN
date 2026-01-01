# 🖼️ Projet de Restauration d'Images et Vidéos avec Real-ESRGAN

Un projet Python complet pour restaurer et améliorer la qualité d'images et de vidéos en utilisant les modèles Real-ESRGAN pré-entraînés.

## 📋 Table des matières

- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Modèles disponibles](#modèles-disponibles)
- [Exemples](#exemples)
- [Dépendances](#dépendances)
- [Contributions](#contributions)
- [Licence](#licence)

## 🎯 Description

Ce projet permet de restaurer et d'améliorer la qualité d'images et de vidéos en utilisant l'intelligence artificielle. Il utilise les modèles Real-ESRGAN pour :

- **Agrandir les images** jusqu'à 4x leur taille originale
- **Améliorer la qualité** en réduisant le bruit et en améliorant les détails
- **Restaurer les images anciennes** ou de faible qualité
- **Traiter les vidéos** frame par frame
- **Comparer visuellement** les résultats avant/après

## ✨ Fonctionnalités

### 🖼️ Restauration d'images
- Support de multiples formats (JPG, PNG, JPEG, BMP)
- Choix interactif du modèle selon le type d'image
- Traitement par lot (toutes les images d'un dossier)
- Gestion automatique de la mémoire (mode tile)

### 🎬 Restauration de vidéos
- Support de multiples formats vidéo (MP4, AVI, MOV, MKV, etc.)
- Traitement frame par frame
- Suivi de progression en temps réel
- Préservation du framerate original

### 📊 Comparaison et évaluation
- Comparaison visuelle avant/après
- Calcul de métriques (PSNR, SSIM, MSE)
- Génération de rapports d'évaluation
- Visualisation des résultats

### 🔧 Prétraitement
- Validation des images
- Redimensionnement automatique
- Normalisation des valeurs
- Extraction de frames vidéo

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)
- Git (pour cloner le repository)

### Étapes d'installation

1. **Cloner le repository**
   ```bash
   git clone https://github.com/moaddebian/restauration-image-Real-ESRGAN.git
   cd restauration-image
   ```

2. **Créer un environnement virtuel (recommandé)**
   ```bash
   python -m venv venv
   
   # Sur Windows
   venv\Scripts\activate
   
   # Sur Linux/Mac
   source venv/bin/activate
   ```

3. **Installer les dépendances de base**
   ```bash
   pip install -r requirements.txt
   ```

4. **Installer BasicSR et Real-ESRGAN**
   
   Le package BasicSR est déjà inclus dans le projet dans le dossier `basicsr_repo` :
   
   ```bash
   pip install -e basicsr_repo
   ```
   
   **Note** : Real-ESRGAN doit être installé séparément :
   ```bash
   git clone https://github.com/xinntao/Real-ESRGAN.git
   cd Real-ESRGAN
   pip install -e .
   cd ..
   ```
   
5. **Télécharger les modèles (automatique)**
   
   Les modèles seront téléchargés automatiquement lors de la première utilisation depuis GitHub. Ils seront sauvegardés dans le dossier `models/`.

## 📖 Utilisation

### Restauration d'une image

```bash
python test_image.py
```

Le script vous demandera de :
1. Choisir un modèle (1-4)
2. L'image sera restaurée automatiquement

**Image d'entrée** : `data/input/`  
**Image de sortie** : `data/output/`

### Restauration d'une vidéo

```bash
python test_video.py
```

Le script vous demandera de :
1. Choisir une vidéo dans `data/input/`
2. Choisir un modèle (1-4)
3. La vidéo sera restaurée frame par frame

**Vidéo d'entrée** : `data/input/`  
**Vidéo de sortie** : `data/output/`

### Comparaison d'images

```bash
python -m src.compare
# ou
python src/compare.py
```

Génère une comparaison visuelle avant/après et la sauvegarde dans `data/comparaison/`

### Utilisation programmatique

```python
from src.restore import ImageRestorer

# Créer un restaurateur
restorer = ImageRestorer(
    model_name='RealESRGAN_x4plus_anime_6B',  # Modèle anime
    gpu_id=0  # Utiliser GPU (None pour CPU)
)

# Restaurer une image
restorer.restore_image(
    "data/input/image.jpg",
    "data/output/image_restored.jpg",
    outscale=4
)

# Restaurer toutes les images d'un dossier
restorer.restore_directory("data/input", "data/output")

# Restaurer une vidéo
restorer.restore_video("data/input/video.mp4", "data/output/video_restored.mp4")
```

## 📁 Structure du projet

```
restauration-image/
├── data/                    # Dossier de données
│   ├── input/              # Images/vidéos d'entrée
│   ├── output/            # Images/vidéos restaurées
│   ├── preprocessed/       # Images prétraitées (optionnel)
│   └── comparaison/        # Résultats de comparaison
│
├── models/                 # Modèles pré-entraînés Real-ESRGAN
│   ├── RealESRGAN_x4plus.pth
│   ├── RealESRGAN_x4plus_anime_6B.pth
│   ├── RealESRNet_x4plus.pth
│   └── RealESRGAN_x2plus.pth
│
├── src/                    # Code source
│   ├── restore.py         # Classe principale de restauration
│   ├── compare.py         # Comparaison visuelle
│   └── preprocess.py      # Prétraitement des images
│
├── basicsr_repo/          # Repository BasicSR (dépendance)
│
├── test_image.py          # Script de test pour images
├── test_video.py          # Script de test pour vidéos
├── main.py                # Évaluation et métriques
├── requirements.txt   # Dépendances Python
├── README.md              # Ce fichier
└── pyrightconfig.json     # Configuration Pyright (optionnel)
```

## 🤖 Modèles disponibles

Le projet supporte 4 modèles Real-ESRGAN :

1. **RealESRGAN_x4plus** (64 MB)
   - Modèle général pour photos et images réelles
   - Agrandissement : 4x
   - Recommandé pour : photos, images naturelles

2. **RealESRGAN_x4plus_anime_6B** (17 MB)
   - Optimisé pour images anime/manga
   - Agrandissement : 4x
   - Recommandé pour : anime, manga, illustrations

3. **RealESRNet_x4plus** (64 MB)
   - Version alternative (ESRNet)
   - Agrandissement : 4x
   - Recommandé pour : alternative au modèle principal

4. **RealESRGAN_x2plus** (64 MB)
   - Agrandissement : 2x (plus rapide)
   - Recommandé pour : traitement rapide, moins de mémoire

## 💻 Exemples

### Exemple 1 : Restaurer une photo

```bash
# Placer votre image dans data/input/
python test_image.py
# Choisir le modèle 1 (RealESRGAN_x4plus)
# L'image restaurée sera dans data/output/
```

### Exemple 2 : Restaurer une image anime

```bash
python test_image.py
# Choisir le modèle 2 (RealESRGAN_x4plus_anime_6B)
```

### Exemple 3 : Traitement par lot

```python
from src.restore import ImageRestorer

restorer = ImageRestorer(model_name='RealESRGAN_x4plus')
restorer.restore_directory("data/input", "data/output")
```

## 🔧 Dépendances

Les principales dépendances sont listées dans `requirements.txt`. Principales bibliothèques :

- **PyTorch** : Framework de deep learning
- **OpenCV** : Traitement d'images
- **Real-ESRGAN** : Modèles de restauration
- **BasicSR** : Bibliothèque de super-résolution
- **NumPy** : Calculs numériques
- **Matplotlib** : Visualisation
- **scikit-image** : Métriques d'évaluation

Voir `requirements.txt` pour la liste complète.

## ⚙️ Configuration

### Utilisation du GPU

Le projet détecte automatiquement les GPU NVIDIA (CUDA). Pour utiliser le GPU :

1. Installer PyTorch avec support CUDA
2. Le script utilisera automatiquement le GPU s'il est disponible

**Note** : Les GPU Intel ne sont pas supportés (CUDA est exclusif à NVIDIA).

### Gestion de la mémoire

Si vous rencontrez des erreurs de mémoire :

- Le script passe automatiquement en mode "tile" (traitement par morceaux)
- Utilisez le modèle x2 (`RealESRGAN_x2plus`) pour économiser la mémoire
- Réduisez la taille des images d'entrée

## 🐛 Dépannage

### Erreur : "Aucun GPU détecté"
- Normal si vous n'avez pas de GPU NVIDIA
- Le traitement se fera sur CPU (plus lent mais fonctionnel)

### Erreur : "Not enough memory"
- Le script passe automatiquement en mode tile
- Si cela persiste, utilisez le modèle x2 ou réduisez la taille des images

### Erreur : "Modèle non trouvé"
- Les modèles sont téléchargés automatiquement lors de la première utilisation
- Vérifiez votre connexion internet
- Les modèles sont téléchargés depuis GitHub et sauvegardés dans `models/`

## 📝 Notes

- Les modèles sont téléchargés automatiquement depuis GitHub lors de la première utilisation
- Le traitement peut prendre du temps, surtout sur CPU
- Les vidéos longues peuvent prendre plusieurs heures à traiter
- Les résultats sont sauvegardés automatiquement

## 🤝 Contributions

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet utilise les modèles Real-ESRGAN qui sont sous licence BSD. 
## 🙏 Remerciements

- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) - Modèles de restauration
- [BasicSR](https://github.com/xinntao/BasicSR) - Bibliothèque de super-résolution
- Tous les contributeurs open-source

## 📧 Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue sur GitHub.

**Repository** : [https://github.com/moaddebian/restauration-image-Real-ESRGAN](https://github.com/moaddebian/restauration-image-Real-ESRGAN)

---

⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile !

