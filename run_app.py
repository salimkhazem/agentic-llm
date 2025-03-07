#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import subprocess
import argparse
import sys

# Charger les variables d'environnement
load_dotenv()

def check_environment():
    """Vérifie que l'environnement est correctement configuré"""
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_DEPLOYMENT_NAME",
        "AZURE_API_VERSION"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Variables d'environnement manquantes : {', '.join(missing_vars)}")
        print("Veuillez configurer ces variables dans le fichier .env")
        return False
    return True

def init_environment():
    """Initialise l'environnement : dossiers, fichiers de config, etc."""
    dirs_to_create = ["uploads", "vectordb", "static", "logs"]
    for dir_name in dirs_to_create:
        os.makedirs(dir_name, exist_ok=True)
    
    # Vérifier que le fichier .env existe
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        print("⚠️ Fichier .env non trouvé. Création à partir de .env.example...")
        with open(".env.example", "r") as src, open(".env", "w") as dest:
            dest.write(src.read())
        print("✅ Fichier .env créé. Veuillez modifier les clés API si nécessaire.")
    
    # Installer les dépendances si nécessaire
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Installation des dépendances réussie.")
    except subprocess.CalledProcessError:
        print("⚠️ Erreur lors de l'installation des dépendances.")

def run_api():
    """Lance l'API FastAPI"""
    try:
        print("🚀 Démarrage de l'API...")
        subprocess.run(["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n👋 API arrêtée.")

def run_tests():
    """Lance les tests du système multi-agent"""
    try:
        subprocess.run([sys.executable, "test_system.py"])
    except KeyboardInterrupt:
        print("\n👋 Tests arrêtés.")

def main():
    parser = argparse.ArgumentParser(description="Interface pour le système multi-agent GRDF")
    parser.add_argument("action", choices=["api", "tests", "init"], 
                        help="Action à effectuer: api (lancer l'API), tests (lancer les tests), init (initialiser l'environnement)")
    args = parser.parse_args()
    
    if args.action == "init":
        init_environment()
    elif args.action == "api":
        if check_environment():
            run_api()
    elif args.action == "tests":
        if check_environment():
            run_tests()

if __name__ == "__main__":
    main()
