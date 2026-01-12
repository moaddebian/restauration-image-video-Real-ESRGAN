"""
Application web pour la restauration d'images avec Real-ESRGAN
API REST + Interface web
"""
import os
import uuid
import torch
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import cv2

from src.restore import ImageRestorer

# Configuration
app = Flask(__name__)
CORS(app)  # Permet les requêtes depuis n'importe quelle origine (pour mobile/web)

# Dossiers
UPLOAD_FOLDER = Path('data/uploads')
OUTPUT_FOLDER = Path('data/output')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

# Créer les dossiers si nécessaire
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Modèles disponibles
AVAILABLE_MODELS = {
    'RealESRGAN_x4plus': {
        'name': 'RealESRGAN_x4plus',
        'description': 'Modèle général (photos, images réelles)',
        'scale': 4
    },
    'RealESRGAN_x4plus_anime_6B': {
        'name': 'RealESRGAN_x4plus_anime_6B',
        'description': 'Optimisé pour images anime/manga',
        'scale': 4
    },
    'RealESRNet_x4plus': {
        'name': 'RealESRNet_x4plus',
        'description': 'Version alternative (ESRNet)',
        'scale': 4
    },
    'RealESRGAN_x2plus': {
        'name': 'RealESRGAN_x2plus',
        'description': 'Agrandissement x2 (plus rapide)',
        'scale': 2
    }
}

# Instance globale du restaurateur (chargée à la demande)
restorer_cache = {}


def allowed_file(filename):
    """Vérifier si le fichier est autorisé"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_gpu():
    """
    Détecter automatiquement un GPU NVIDIA disponible
    Retourne (gpu_id, gpu_info) ou (None, None) si aucun GPU
    """
    if not torch.cuda.is_available():
        return None, None
    
    try:
        # Vérifier le nombre de GPU disponibles
        num_gpus = torch.cuda.device_count()
        if num_gpus == 0:
            return None, None
        
        # Utiliser le premier GPU disponible
        gpu_id = 0
        gpu_name = torch.cuda.get_device_name(gpu_id)
        gpu_props = torch.cuda.get_device_properties(gpu_id)
        
        # Vérifier que c'est un GPU NVIDIA (contient généralement "NVIDIA" ou "GeForce" ou "RTX" etc.)
        gpu_info = {
            'id': gpu_id,
            'name': gpu_name,
            'memory_gb': gpu_props.total_memory / 1024**3,
            'compute_capability': f"{gpu_props.major}.{gpu_props.minor}"
        }
        
        return gpu_id, gpu_info
    except Exception as e:
        print(f"⚠️  Erreur lors de la détection GPU: {e}")
        return None, None


def get_restorer(model_name='RealESRGAN_x4plus'):
    """Obtenir ou créer une instance de restaurateur"""
    if model_name not in restorer_cache:
        # Détecter GPU automatiquement (toute GPU NVIDIA)
        gpu_id, gpu_info = detect_gpu()
        
        if gpu_id is not None and gpu_info is not None:
            print(f"✓ GPU NVIDIA détecté: {gpu_info['name']} ({gpu_info['memory_gb']:.1f} GB)")
        else:
            print("ℹ️  Aucun GPU détecté, utilisation du CPU")
        
        restorer_cache[model_name] = ImageRestorer(model_name=model_name, gpu_id=gpu_id)
    return restorer_cache[model_name]


@app.route('/')
def index():
    """Redirection vers le frontend React"""
    # Le frontend React sera servi par Vite en développement
    # En production, servez les fichiers statiques du build React
    return jsonify({
        'message': 'API REST pour la restauration d\'images',
        'frontend': 'http://localhost:5173',
        'api_docs': '/api/health'
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifier l'état de l'API"""
    gpu_id, gpu_info = detect_gpu()
    gpu_available = gpu_id is not None
    
    return jsonify({
        'status': 'ok',
        'gpu_available': gpu_available,
        'gpu_info': gpu_info,
        'device': 'cuda' if gpu_available else 'cpu',
        'models': list(AVAILABLE_MODELS.keys())
    })


@app.route('/api/models', methods=['GET'])
def get_models():
    """Obtenir la liste des modèles disponibles"""
    return jsonify({
        'models': AVAILABLE_MODELS
    })


@app.route('/api/restore', methods=['POST'])
def restore_image():
    """
    API endpoint pour restaurer une image
    Accepte: multipart/form-data avec 'image' et 'model' (optionnel)
    """
    try:
        # Vérifier qu'un fichier a été envoyé
        if 'image' not in request.files:
            return jsonify({'error': 'Aucune image fournie'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Format de fichier non supporté'}), 400
        
        # Obtenir le modèle (par défaut: RealESRGAN_x4plus)
        model_name = request.form.get('model', 'RealESRGAN_x4plus')
        if model_name not in AVAILABLE_MODELS:
            return jsonify({'error': f'Modèle {model_name} non disponible'}), 400
        
        # Obtenir le facteur d'échelle (par défaut: 4)
        try:
            outscale = int(request.form.get('outscale', 4))
        except ValueError:
            outscale = 4
        # Sauvegarder le fichier uploadé
        if file.filename is None:
            return jsonify({'error': 'Nom de fichier invalide'}), 400
        filename = secure_filename(file.filename or "")
        if not filename:
            return jsonify({'error': 'Nom de fichier sécurisé invalide'}), 400
        unique_id = str(uuid.uuid4())
        if '.' not in filename:
            return jsonify({'error': 'Extension de fichier manquante'}), 400
        file_ext = filename.rsplit('.', 1)[1].lower()
        input_filename = f"{unique_id}_input.{file_ext}"
        input_path = Path(app.config['UPLOAD_FOLDER']) / input_filename
        
        file.save(str(input_path))
        
        # Générer le nom de sortie
        output_filename = f"{unique_id}_restored.jpg"
        output_path = OUTPUT_FOLDER / output_filename
        
        # Restaurer l'image
        restorer = get_restorer(model_name)
        result_path = restorer.restore_image(
            str(input_path),
            str(output_path),
            outscale=outscale
        )
        
        # Obtenir les informations sur les images
        original_img = cv2.imread(str(input_path))
        restored_img = cv2.imread(str(result_path))
        
        original_size = original_img.shape[:2] if original_img is not None else (0, 0)
        restored_size = restored_img.shape[:2] if restored_img is not None else (0, 0)
        
        # Retourner la réponse
        return jsonify({
            'success': True,
            'job_id': unique_id,
            'input_file': input_filename,
            'output_file': output_filename,
            'original_size': {'width': original_size[1], 'height': original_size[0]},
            'restored_size': {'width': restored_size[1], 'height': restored_size[0]},
            'model_used': model_name,
            'scale': outscale,
            'download_url': f'/api/download/{output_filename}',
            'preview_url': f'/api/preview/{output_filename}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Télécharger un fichier restauré"""
    file_path = OUTPUT_FOLDER / secure_filename(filename)
    if file_path.exists():
        return send_file(str(file_path), as_attachment=True)
    return jsonify({'error': 'Fichier non trouvé'}), 404


@app.route('/api/preview/<filename>', methods=['GET'])
def preview_file(filename):
    """Aperçu d'une image restaurée"""
    file_path = OUTPUT_FOLDER / secure_filename(filename)
    if file_path.exists():
        return send_file(str(file_path), mimetype='image/jpeg')
    return jsonify({'error': 'Fichier non trouvé'}), 404


@app.route('/api/job/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Obtenir le statut d'un job (pour polling)"""
    # Chercher les fichiers associés
    input_files = list(UPLOAD_FOLDER.glob(f"{job_id}_*"))
    output_files = list(OUTPUT_FOLDER.glob(f"{job_id}_*"))
    
    status = 'processing'
    if output_files:
        status = 'completed'
    elif not input_files:
        status = 'not_found'
    
    return jsonify({
        'job_id': job_id,
        'status': status,
        'has_output': len(output_files) > 0
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Application de restauration d'images")
    print("=" * 60)
    
    # Détection automatique du GPU
    gpu_id, gpu_info = detect_gpu()
    
    if gpu_id is not None and gpu_info is not None:
        print(f"✓ GPU NVIDIA détecté et activé")
        print(f"  Nom: {gpu_info.get('name', 'Inconnu')}")
        print(f"  Mémoire: {gpu_info.get('memory_gb', 0):.1f} GB")
        print(f"  Compute Capability: {gpu_info.get('compute_capability', 'Inconnu')}")
        print(f"  Device: cuda:{gpu_id}")
    else:
        print("ℹ️  Aucun GPU NVIDIA détecté")
        print("  → Utilisation du CPU")
        if torch.cuda.is_available():
            print("  ⚠️  PyTorch avec CUDA installé mais GPU non accessible")
            print("     Vérifiez les pilotes NVIDIA: nvidia-smi")
    
    print("=" * 60)
    print("\nDémarrage du serveur...")
    print("Interface web: http://localhost:5000")
    print("API: http://localhost:5000/api/")
    print("\nAppuyez sur Ctrl+C pour arrêter\n")
    
    # Configuration pour production/développement
    import sys
    import os
    
    # Port depuis variable d'environnement (pour déploiement) ou 5000 par défaut
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    # Désactiver le reloader sur Windows et en production
    use_reloader = debug and sys.platform != 'win32'
    
    app.run(
        debug=debug, 
        host='0.0.0.0', 
        port=port,
        use_reloader=use_reloader,
        use_debugger=debug
    )
