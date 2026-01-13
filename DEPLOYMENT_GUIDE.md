# 🚀 Guide de Déploiement Gratuit - Nostalix AI

Guide complet pour déployer votre application **Nostalix AI** gratuitement.

## 📋 Architecture de Déploiement

Votre application a 2 parties à déployer :
1. **Frontend React** (Vite) - Interface utilisateur
2. **Backend Flask** - API REST pour la restauration d'images

## 🎯 Option Recommandée : Vercel (Frontend) + Render (Backend)

### **Frontend sur Vercel** (Gratuit, excellent pour React)

#### Avantages :
- ✅ Gratuit illimité
- ✅ Déploiement automatique depuis GitHub
- ✅ CDN global (rapide partout)
- ✅ SSL automatique
- ✅ Parfait pour React/Vite

#### Étapes :

1. **Préparer le build du frontend** :
   ```bash
   cd frontend
   npm run build
   ```
   Cela crée le dossier `frontend/dist/` avec les fichiers statiques.

2. **Créer un compte Vercel** :
   - Allez sur https://vercel.com
   - Connectez-vous avec GitHub

3. **Déployer** :
   - Cliquez sur "Add New Project"
   - Importez votre repository GitHub
   - **Root Directory** : `frontend`
   - **Build Command** : `npm run build`
   - **Output Directory** : `dist`
   - **Install Command** : `npm install`

4. **Variables d'environnement** :
   - Dans les paramètres du projet Vercel
   - Ajoutez : `VITE_API_URL=https://votre-backend.render.com/api`
   - (Remplacez par l'URL de votre backend Render)

5. **Déployer** : Vercel déploie automatiquement !

---

### **Backend sur Render** (Gratuit pour Python/Flask)

#### Avantages :
- ✅ Plan gratuit disponible
- ✅ Support Python/Flask
- ✅ Déploiement depuis GitHub
- ✅ SSL automatique
- ⚠️ Limitation : Le service se met en veille après 15 min d'inactivité (première requête peut être lente)

#### Étapes :

1. **Créer un compte Render** :
   - Allez sur https://render.com
   - Connectez-vous avec GitHub

2. **Créer un nouveau Web Service** :
   - Cliquez sur "New +" → "Web Service"
   - Connectez votre repository GitHub
   - Sélectionnez le repository `restauration-image`

3. **Configuration** :
   ```
   Name: nostalix-ai-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt && pip install -e basicsr_repo
   Start Command: python app.py
   ```

4. **Variables d'environnement** (optionnel) :
   ```
   FLASK_ENV=production
   PORT=5000
   ```

5. **Plan gratuit** :
   - Sélectionnez "Free" plan
   - ⚠️ Note : Le service se met en veille après 15 min d'inactivité

6. **Déployer** : Render déploie automatiquement !

7. **Obtenir l'URL** :
   - Une fois déployé, vous obtenez une URL comme : `https://nostalix-ai-backend.onrender.com`
   - Mettez à jour `VITE_API_URL` dans Vercel avec cette URL

---

## 🔄 Alternative : Railway (Tout-en-un)

Railway peut héberger le frontend ET le backend.

### Avantages :
- ✅ Support Python et Node.js
- ✅ Plan gratuit avec $5 de crédits/mois
- ✅ Pas de mise en veille
- ✅ Déploiement simple

### Étapes :

1. **Créer un compte** : https://railway.app

2. **Déployer le Backend** :
   - "New Project" → "Deploy from GitHub repo"
   - Sélectionnez votre repo
   - Railway détecte automatiquement Python
   - Configurez :
     ```
     Build Command: pip install -r requirements.txt && pip install -e basicsr_repo
     Start Command: python app.py
     ```

3. **Déployer le Frontend** :
   - Créez un nouveau service dans le même projet
   - Sélectionnez le dossier `frontend`
   - Railway détecte automatiquement Node.js
   - Configurez :
     ```
     Build Command: npm run build
     Start Command: npx serve -s dist
     ```

4. **Variables d'environnement** :
   - Frontend : `VITE_API_URL=https://votre-backend.railway.app/api`

---

## 🌐 Alternative : Netlify (Frontend) + Fly.io (Backend)

### Frontend sur Netlify

1. Allez sur https://netlify.com
2. "Add new site" → "Import an existing project"
3. Connectez GitHub
4. Configuration :
   - **Base directory** : `frontend`
   - **Build command** : `npm run build`
   - **Publish directory** : `frontend/dist`

### Backend sur Fly.io

1. Allez sur https://fly.io
2. Installez Fly CLI : `curl -L https://fly.io/install.sh | sh`
3. Créez un `Dockerfile` pour Flask (voir section ci-dessous)
4. Déployez : `fly deploy`

---

## 📦 Préparer le Projet pour le Déploiement

### 1. Modifier `app.py` pour la production

```python
# À la fin de app.py, remplacer par :
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### 2. Créer un `Dockerfile` (optionnel, pour Fly.io/Docker)

Créez `Dockerfile` à la racine :

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers
COPY requirements.txt .
COPY basicsr_repo/ ./basicsr_repo/
COPY src/ ./src/
COPY app.py .
COPY models/ ./models/

# Installer Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e basicsr_repo

# Exposer le port
EXPOSE 5000

# Lancer l'application
CMD ["python", "app.py"]
```

### 3. Créer `.dockerignore`

```
__pycache__/
*.pyc
*.pyo
*.pyd
venv/
env/
.venv
data/uploads/*
data/output/*
.git
.gitignore
frontend/
README.md
```

### 4. Créer `render.yaml` (pour Render)

Créez `render.yaml` à la racine :

```yaml
services:
  - type: web
    name: nostalix-ai-backend
    env: python
    buildCommand: pip install -r requirements.txt && pip install -e basicsr_repo
    startCommand: python app.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PORT
        value: 5000
```

### 5. Mettre à jour `frontend/vite.config.js` pour la production

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  }
})
```

---

## 🔧 Configuration CORS (Important !)

Votre `app.py` a déjà `CORS(app)`, mais pour la production, vous pouvez être plus spécifique :

```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://votre-frontend.vercel.app",
            "http://localhost:5173"  # Pour le dev local
        ]
    }
})
```

---

## 📝 Checklist de Déploiement

### Avant de déployer :

- [ ] Tester le build du frontend : `cd frontend && npm run build`
- [ ] Vérifier que tous les modèles sont dans `models/`
- [ ] Tester l'API localement : `python app.py`
- [ ] Vérifier les variables d'environnement
- [ ] Mettre à jour `VITE_API_URL` dans le frontend

### Après le déploiement :

- [ ] Tester l'API : `https://votre-backend.onrender.com/api/health`
- [ ] Tester le frontend : `https://votre-frontend.vercel.app`
- [ ] Vérifier que les images s'affichent
- [ ] Tester l'upload et la restauration

---

## ⚠️ Limitations des Plans Gratuits

### Render (Backend) :
- ⚠️ Mise en veille après 15 min d'inactivité
- ⚠️ Première requête peut prendre 30-60 secondes
- ✅ Solution : Utiliser un service de "ping" pour garder le service actif

### Vercel (Frontend) :
- ✅ Aucune limitation majeure
- ✅ Parfait pour React

### Railway :
- ⚠️ $5 de crédits gratuits/mois (suffisant pour un petit projet)
- ✅ Pas de mise en veille

---

## 🎯 Recommandation Finale

**Pour commencer rapidement** :
1. **Frontend** : Vercel (gratuit, excellent)
2. **Backend** : Render (gratuit, facile)

**Pour une meilleure performance** :
1. **Frontend** : Vercel
2. **Backend** : Railway (pas de mise en veille)

---

## 🆘 Dépannage

### Le backend ne répond pas
- Vérifiez les logs sur Render/Railway
- Vérifiez que le port est bien configuré (variable `PORT`)
- Vérifiez que CORS est bien configuré

### Le frontend ne peut pas joindre l'API
- Vérifiez `VITE_API_URL` dans Vercel
- Vérifiez que l'URL du backend est correcte
- Vérifiez CORS dans `app.py`

### Les images ne s'affichent pas
- Vérifiez que les URLs sont complètes (avec `https://`)
- Vérifiez que le proxy Vite est bien configuré

---

## 📚 Ressources

- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)

Bon déploiement ! 🚀
