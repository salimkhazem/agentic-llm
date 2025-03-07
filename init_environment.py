import os
import sys
import shutil
from pathlib import Path

def setup_environment():
    """Initialise l'environnement de travail pour le projet GRDF"""
    base_dir = Path(__file__).parent.absolute()
    
    # Créer les répertoires nécessaires
    directories = ['uploads', 'vectordb', 'static/css', 'static/js', 'templates']
    
    for directory in directories:
        dir_path = base_dir / directory
        if not dir_path.exists():
            print(f"Création du répertoire: {directory}")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    # Vérifier l'existence du fichier .env
    env_file = base_dir / ".env"
    env_example = base_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("Création du fichier .env depuis .env.example")
        shutil.copy(env_example, env_file)
        print("⚠️ N'oubliez pas de mettre à jour vos clés API dans le fichier .env")
    
    # Vérifier l'existence du répertoire utils
    utils_dir = base_dir / "utils"
    if not utils_dir.exists():
        print("⚠️ Le répertoire utils n'existe pas. Certains imports pourraient échouer.")
    
    # Création d'un fichier __init__.py dans le répertoire utils s'il n'existe pas
    utils_init = utils_dir / "__init__.py"
    if not utils_init.exists() and utils_dir.exists():
        print("Création du fichier utils/__init__.py")
        with open(utils_init, "w") as f:
            f.write("# Fichier d'initialisation pour le module utils\n")
    
    print("\n✅ Environnement initialisé avec succès!")
    print("\nÉtapes suivantes:")
    print("1. Mettez à jour vos clés API dans le fichier .env")
    print("2. Exécutez 'pip install -r requirements.txt' pour installer les dépendances")
    print("3. Exécutez 'python utils/add_sample_doc.py' pour créer un document d'exemple")
    print("4. Exécutez 'python test_agents.py --agent documents' pour tester la recherche de documents")

if __name__ == "__main__":
    setup_environment()
