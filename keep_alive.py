import requests
import time
import os

# URL de votre backend Render
BACKEND_URL = os.environ.get('BACKEND_URL', 'https://votre-backend.onrender.com')

def ping_backend():
    """Ping le backend pour le garder actif"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        if response.status_code == 200:
            print(f"[OK] Backend actif - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print(f"[WARNING] Backend répond mais avec code {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERREUR] Impossible de contacter le backend: {e}")
        return False

if __name__ == '__main__':
    # Ping toutes les 10 minutes (Render se met en veille après 15 min)
    while True:
        ping_backend()
        time.sleep(600)  # 10 minutes
