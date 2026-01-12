# 🚀 Déploiement Rapide - Nostalix AI

Guide rapide pour déployer en 10 minutes !

## 📦 Option 1 : Vercel + Render (Recommandé)

### Étape 1 : Déployer le Backend (Render)

1. **Allez sur** https://render.com
2. **Créez un compte** (gratuit avec GitHub)
3. **New +** → **Web Service**
4. **Connectez votre repo GitHub**
5. **Configuration** :
   ```
   Name: nostalix-ai-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt && pip install -e basicsr_repo
   Start Command: python app.py
   Plan: Free
   ```
6. **Cliquez sur "Create Web Service"**
7. **Attendez le déploiement** (5-10 minutes)
8. **Copiez l'URL** : `https://nostalix-ai-backend.onrender.com`

### Étape 2 : Déployer le Frontend (Vercel)

1. **Allez sur** https://vercel.com
2. **Créez un compte** (gratuit avec GitHub)
3. **Add New Project**
4. **Importez votre repo GitHub**
5. **Configuration** :
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```
6. **Environment Variables** :
   ```
   VITE_API_URL = https://nostalix-ai-backend.onrender.com/api
   ```
   (Remplacez par votre URL Render)
7. **Deploy** → C'est fait !

### ✅ Résultat

- Frontend : `https://votre-projet.vercel.app`
- Backend : `https://nostalix-ai-backend.onrender.com`

---

## 🔧 Garder le Backend Actif (Optionnel)

Le plan gratuit de Render met le service en veille après 15 min d'inactivité.

**Solution gratuite** : Utilisez [UptimeRobot](https://uptimerobot.com)
1. Créez un compte gratuit
2. Ajoutez un "HTTP(s) Monitor"
3. URL : `https://votre-backend.onrender.com/api/health`
4. Intervalle : 5 minutes
5. Le service restera actif !

---

## 📝 Checklist Avant Déploiement

- [ ] Tous les modèles sont dans `models/` (RealESRGAN_x4plus.pth, etc.)
- [ ] Le build frontend fonctionne : `cd frontend && npm run build`
- [ ] L'API fonctionne localement : `python app.py`
- [ ] Le code est poussé sur GitHub

---

## 🎯 URLs Finales

Après déploiement, vous aurez :
- **Frontend** : `https://votre-projet.vercel.app`
- **Backend API** : `https://votre-backend.onrender.com/api`

Partagez l'URL du frontend avec vos utilisateurs ! 🎉
