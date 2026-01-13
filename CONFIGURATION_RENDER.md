# 🔧 Configuration Render - Guide Complet

Guide pour vérifier et configurer le buildCommand sur Render.

## 📋 Méthode 1 : Vérifier que Render utilise `render.yaml`

### Étape 1 : Vérifier que `render.yaml` est dans le repo

1. **Vérifiez sur GitHub** que le fichier `render.yaml` est bien présent à la racine du projet
2. **Vérifiez que le fichier est commité** :
   ```bash
   git status
   git log --oneline render.yaml
   ```

### Étape 2 : Vérifier dans l'interface Render

1. **Connectez-vous à Render** : https://render.com
2. **Allez dans votre service** : Cliquez sur votre service `nostalix-ai-backend`
3. **Onglet "Settings"** (Paramètres)
4. **Section "Build & Deploy"** :
   - Si vous voyez "**Using render.yaml**" ou "**Auto-detected from render.yaml**" → ✅ Render utilise le fichier
   - Si vous voyez un champ "**Build Command**" avec du texte → ⚠️ Render n'utilise PAS le fichier, il utilise la configuration manuelle

---

## 🛠️ Méthode 2 : Configurer le buildCommand manuellement

Si Render n'utilise pas `render.yaml`, configurez manuellement :

### Étape 1 : Accéder aux paramètres

1. **Connectez-vous à Render** : https://render.com
2. **Cliquez sur votre service** : `nostalix-ai-backend`
3. **Cliquez sur "Settings"** (Paramètres) dans le menu de gauche

### Étape 2 : Configurer le Build Command

1. **Descendez jusqu'à la section "Build & Deploy"**
2. **Trouvez le champ "Build Command"**
3. **Collez cette commande** :

```bash
pip install --upgrade pip setuptools wheel &&
pip install -r requirements.txt &&
pip install -e basicsr_repo &&
echo "=== Installation Real-ESRGAN ===" &&
(pip install git+https://github.com/xinntao/Real-ESRGAN.git 2>&1 || python setup_realesrgan.py) &&
echo "=== Vérification ===" &&
python -c "import realesrgan; from realesrgan import RealESRGANer; print('✅ Real-ESRGAN OK')" &&
echo "=== Build terminé ==="
```

### Étape 3 : Configurer le Start Command

1. **Trouvez le champ "Start Command"**
2. **Assurez-vous qu'il contient** :
   ```
   python app.py
   ```

### Étape 4 : Vérifier les autres paramètres

1. **Environment** : Doit être "Python 3"
2. **Root Directory** : Laissez vide (ou `/` si nécessaire)
3. **Plan** : "Free"

### Étape 5 : Sauvegarder et redéployer

1. **Cliquez sur "Save Changes"** en bas de la page
2. **Allez dans l'onglet "Events"** ou "Logs"
3. **Cliquez sur "Manual Deploy"** → "Deploy latest commit"
4. **Attendez le déploiement** (5-10 minutes)

---

## 🔍 Méthode 3 : Forcer Render à utiliser `render.yaml`

Si vous voulez que Render utilise automatiquement `render.yaml` :

### Option A : Créer un nouveau service

1. **Supprimez l'ancien service** (ou gardez-le pour référence)
2. **Créez un nouveau service** :
   - "New +" → "Web Service"
   - Connectez votre repo GitHub
   - Render devrait **automatiquement détecter** `render.yaml`
   - Si c'est le cas, vous verrez "Auto-detected from render.yaml"

### Option B : Modifier le service existant

1. **Allez dans Settings** de votre service
2. **Section "Build & Deploy"**
3. **Cherchez "Configuration Source"** ou "Config File"
4. **Sélectionnez "render.yaml"** si disponible
5. **Sauvegardez**

---

## ✅ Vérification après configuration

### Vérifier les logs de build

1. **Allez dans l'onglet "Logs"** de votre service
2. **Sélectionnez "Build Logs"** (pas "Runtime Logs")
3. **Recherchez ces messages** :
   - `=== Installation Real-ESRGAN ===`
   - `✅ Real-ESRGAN OK`
   - `=== Build terminé ===`

### Si vous ne voyez pas ces messages

- ⚠️ Le buildCommand ne s'exécute pas correctement
- ⚠️ Vérifiez qu'il n'y a pas d'erreur avant cette étape
- ⚠️ Vérifiez que tous les fichiers nécessaires sont présents (`setup_realesrgan.py`)

---

## 🐛 Dépannage

### Problème : "Build Command not found"

**Solution** : Vérifiez que le buildCommand est bien collé dans le champ (pas de saut de ligne manquant)

### Problème : "Script setup_realesrgan.py not found"

**Solution** : 
1. Vérifiez que `setup_realesrgan.py` est dans le repo
2. Vérifiez qu'il est commité et poussé sur GitHub
3. Vérifiez qu'il est à la racine du projet

### Problème : "ModuleNotFoundError: No module named 'realesrgan'"

**Solution** :
1. Vérifiez les logs de build pour voir si l'installation a réussi
2. Si l'installation échoue, vérifiez que git est disponible
3. Si git n'est pas disponible, le script `setup_realesrgan.py` devrait utiliser la méthode ZIP

---

## 📝 Checklist finale

Avant de redéployer, vérifiez :

- [ ] `render.yaml` est à la racine du projet
- [ ] `setup_realesrgan.py` est à la racine du projet
- [ ] Les deux fichiers sont commités et poussés sur GitHub
- [ ] Le buildCommand est configuré (manuellement ou via render.yaml)
- [ ] Le startCommand est `python app.py`
- [ ] L'environnement est "Python 3"

---

## 🎯 Commandes Git pour vérifier

```bash
# Vérifier que les fichiers sont présents
ls -la render.yaml setup_realesrgan.py

# Vérifier qu'ils sont commités
git status

# Vérifier qu'ils sont poussés
git log --oneline render.yaml setup_realesrgan.py

# Si nécessaire, commit et push
git add render.yaml setup_realesrgan.py
git commit -m "Add Real-ESRGAN installation configuration"
git push
```

---

## 💡 Astuce

**Pour voir tous les logs de build** :
1. Allez dans "Logs" → "Build Logs"
2. Faites défiler jusqu'au début
3. Recherchez "=== Installation Real-ESRGAN ==="
4. Si vous ne le voyez pas, le buildCommand ne s'exécute pas ou échoue avant

**Pour forcer un nouveau build** :
1. Allez dans "Events"
2. Cliquez sur "Manual Deploy"
3. Sélectionnez "Deploy latest commit"
