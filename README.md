# 🎨 Application de Restauration d'Images

Application web complète pour restaurer et améliorer la qualité d'images en utilisant Real-ESRGAN avec une interface moderne et une API REST.

## ✨ Fonctionnalités

- 🌐 **Interface Web Moderne** : Interface utilisateur intuitive et responsive
- 🔌 **API REST** : API complète pour intégration mobile/web
- 🚀 **Support GPU** : Détection automatique et utilisation du GPU (CUDA)
- 📸 **Multi-modèles** : Support de 4 modèles différents (général, anime, x2, x4)
- 📱 **Responsive** : Compatible mobile, tablette et desktop
- ⚡ **Temps réel** : Feedback en temps réel pendant le traitement

## 🛠️ Installation

### Prérequis

- Python 3.8+
- GPU NVIDIA avec CUDA (optionnel mais recommandé)
- Pilotes NVIDIA à jour

### Étapes d'installation

1. **Cloner le repository**
   ```bash
   git clone <votre-repo>
   cd restauration-image
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Installer Real-ESRGAN et BasicSR**
   ```bash
   # Installer BasicSR
   pip install -e basicsr_repo
   
   # Installer Real-ESRGAN (si nécessaire)
   # git clone https://github.com/xinntao/Real-ESRGAN.git
   # cd Real-ESRGAN
   # pip install -e .
   ```

5. **Installer PyTorch avec CUDA** (pour support GPU)
   ```bash
   # CUDA 11.8 (recommandé)
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   
   # OU CUDA 12.1
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```

## 🚀 Utilisation

### Lancer l'application web

```bash
python app.py
```

L'application sera accessible à :
- **Interface web** : http://localhost:5000
- **API** : http://localhost:5000/api/

### Utilisation de l'interface web

1. Ouvrez http://localhost:5000 dans votre navigateur
2. Glissez-déposez ou sélectionnez une image
3. Choisissez le modèle et le facteur d'échelle
4. Cliquez sur "Restaurer l'image"
5. Téléchargez le résultat

## 📡 API REST

### Endpoints disponibles

#### `GET /api/health`
Vérifier l'état de l'API et la disponibilité du GPU

**Réponse :**
```json
{
  "status": "ok",
  "gpu_available": true,
  "gpu_info": {
    "name": "NVIDIA GeForce RTX 5060",
    "memory": 16.0
  },
  "models": ["RealESRGAN_x4plus", ...]
}
```

#### `GET /api/models`
Obtenir la liste des modèles disponibles

#### `POST /api/restore`
Restaurer une image

**Paramètres (multipart/form-data) :**
- `image` (file) : Fichier image à restaurer
- `model` (string, optionnel) : Nom du modèle (défaut: RealESRGAN_x4plus)
- `outscale` (int, optionnel) : Facteur d'échelle (défaut: 4)

**Réponse :**
```json
{
  "success": true,
  "job_id": "uuid",
  "input_file": "filename",
  "output_file": "filename",
  "original_size": {"width": 1920, "height": 1080},
  "restored_size": {"width": 7680, "height": 4320},
  "model_used": "RealESRGAN_x4plus",
  "scale": 4,
  "download_url": "/api/download/filename",
  "preview_url": "/api/preview/filename"
}
```

#### `GET /api/download/<filename>`
Télécharger une image restaurée

#### `GET /api/preview/<filename>`
Aperçu d'une image restaurée

#### `GET /api/job/<job_id>`
Obtenir le statut d'un job

### Exemple d'utilisation de l'API

#### Avec cURL
```bash
curl -X POST http://localhost:5000/api/restore \
  -F "image=@path/to/image.jpg" \
  -F "model=RealESRGAN_x4plus" \
  -F "outscale=4"
```

#### Avec Python
```python
import requests

url = "http://localhost:5000/api/restore"
files = {'image': open('image.jpg', 'rb')}
data = {'model': 'RealESRGAN_x4plus', 'outscale': 4}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Image restaurée: {result['preview_url']}")
```

#### Avec JavaScript (fetch)
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('model', 'RealESRGAN_x4plus');
formData.append('outscale', 4);

fetch('http://localhost:5000/api/restore', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Résultat:', data);
    // Afficher l'image: data.preview_url
});
```

## 🎯 Modèles disponibles

1. **RealESRGAN_x4plus** : Modèle général pour photos et images réelles (x4)
2. **RealESRGAN_x4plus_anime_6B** : Optimisé pour images anime/manga (x4)
3. **RealESRNet_x4plus** : Version alternative ESRNet (x4)
4. **RealESRGAN_x2plus** : Agrandissement x2 (plus rapide)

## 📁 Structure du projet

```
restauration-image/
├── app.py                 # Serveur Flask principal
├── templates/
│   └── index.html         # Interface web
├── static/
│   ├── css/
│   │   └── style.css      # Styles
│   └── js/
│       └── app.js         # JavaScript
├── src/
│   └── restore.py         # Module de restauration
├── data/
│   ├── uploads/           # Images uploadées
│   └── output/            # Images restaurées
├── models/                # Modèles pré-entraînés
└── requirements.txt       # Dépendances
```

## 🔧 Configuration

### Variables d'environnement (optionnel)

Créez un fichier `.env` :
```env
FLASK_ENV=development
FLASK_DEBUG=True
MAX_UPLOAD_SIZE=52428800  # 50MB
```

### Port personnalisé

Modifiez la dernière ligne de `app.py` :
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Port 8080
```

## 🐛 Dépannage

### GPU non détecté

1. Vérifiez que PyTorch avec CUDA est installé :
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. Vérifiez les pilotes NVIDIA :
   ```bash
   nvidia-smi
   ```

3. Réinstallez PyTorch avec CUDA si nécessaire

### Erreur de mémoire GPU

L'application basculera automatiquement en mode "tile" pour économiser la mémoire. Si le problème persiste, utilisez le modèle x2plus qui nécessite moins de mémoire.

## 📝 Licence

Ce projet utilise Real-ESRGAN qui est sous licence BSD.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📧 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.
