FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système pour OpenCV et Git
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .
COPY basicsr_repo/ ./basicsr_repo/

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e basicsr_repo

# Copier et exécuter le script d'installation de Real-ESRGAN
COPY install_realesrgan.py .
RUN python install_realesrgan.py

# Copier le code de l'application
COPY src/ ./src/
COPY app.py .
COPY models/ ./models/ 2>/dev/null || mkdir -p models

# Créer les dossiers nécessaires
RUN mkdir -p data/uploads data/output

# Exposer le port
EXPOSE 5000

# Variables d'environnement
ENV FLASK_ENV=production
ENV PORT=5000

# Lancer l'application
CMD ["python", "app.py"]
