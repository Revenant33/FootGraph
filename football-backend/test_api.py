# test_api.py
"""
Script de test pour l'API Football Analytics
Exécuter après avoir lancé le serveur : python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Affiche une réponse formatée"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data[:3] if isinstance(data, list) else data, indent=2, ensure_ascii=False))
        if isinstance(data, list) and len(data) > 3:
            print(f"... et {len(data) - 3} autres résultats")
        print("✅ Succès")
    else:
        print(f"❌ Erreur {response.status_code}: {response.text}")

def test_api():
    """Test des principaux endpoints"""
    
    print("🚀 Début des tests de l'API Football Analytics\n")
    
    # 1. Test de santé
    print_response(
        "1. Health Check",
        requests.get(f"{BASE_URL}/health")
    )
    
    # 2. Top buteurs
    print_response(
        "2. Top 5 buteurs",
        requests.get(f"{BASE_URL}/api/home/top-scorers?limit=5")
    )
    
    print(f"\n{'='*60}")
    print("✨ Tests terminés !")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur : Impossible de se connecter au serveur")
        print("Assurez-vous que le serveur FastAPI est lancé sur http://localhost:8000")
        print("Commande : python app/main.py ou uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Erreur inattendue : {e}")