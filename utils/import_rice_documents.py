import os
import sys
import time
from pathlib import Path
from typing import List, Tuple

# Ajouter le répertoire parent au path pour pouvoir importer correctement
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from utils.document_processor import process_document

# Charger les variables d'environnement
load_dotenv()

# Extensions de fichiers supportées
SUPPORTED_EXTENSIONS = {
    '.txt': 'texte',
    '.pdf': 'pdf',
    '.docx': 'word',
    '.doc': 'word',
    '.pptx': 'powerpoint',
    '.ppt': 'powerpoint',
    # Ajoutez d'autres extensions au besoin
}

def get_document_type(filename: str) -> str:
    """Détermine le type de document basé sur l'extension"""
    ext = Path(filename).suffix.lower()
    if ext in SUPPORTED_EXTENSIONS:
        return SUPPORTED_EXTENSIONS[ext]
    return "autre"

def find_documents(base_dir: str) -> List[Tuple[str, str]]:
    """
    Parcourt récursivement le dossier pour trouver tous les documents supportés
    Retourne une liste de tuples (chemin_fichier, type_document)
    """
    documents = []
    base_path = Path(base_dir)
    
    if not base_path.exists():
        print(f"⚠️ Le dossier {base_dir} n'existe pas!")
        return documents
    
    print(f"🔍 Recherche de documents dans {base_dir}...")
    
    # Parcourir tous les fichiers récursivement
    for file_path in base_path.glob('**/*'):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in SUPPORTED_EXTENSIONS:
                doc_type = SUPPORTED_EXTENSIONS[ext]
                documents.append((str(file_path), doc_type))
    
    return documents

def import_documents(base_dir: str, max_docs: int = None):
    """
    Importe tous les documents du dossier et ses sous-dossiers
    
    Args:
        base_dir: Chemin du dossier racine contenant les documents
        max_docs: Nombre maximum de documents à importer (None pour tous)
    """
    documents = find_documents(base_dir)
    
    if not documents:
        print("❌ Aucun document supporté trouvé dans le dossier.")
        return
    
    print(f"✅ {len(documents)} documents trouvés.")
    if max_docs and max_docs < len(documents):
        print(f"⚠️ Limitation à {max_docs} documents pour cet import.")
        documents = documents[:max_docs]
    
    # Statistiques
    success_count = 0
    error_count = 0
    skipped_count = 0
    document_types = {}
    
    # Traiter chaque document
    for i, (file_path, doc_type) in enumerate(documents, 1):
        filename = Path(file_path).name
        print(f"\n📄 [{i}/{len(documents)}] Traitement de {filename}...")
        
        try:
            # Informations de base pour le document
            title = Path(file_path).stem
            description = f"Document extrait du dossier documents_rice - Chemin: {Path(file_path).relative_to(base_dir)}"
            
            # Extension pour les statistiques
            ext = Path(file_path).suffix.lower()
            if ext not in document_types:
                document_types[ext] = 0
            document_types[ext] += 1
            
            # Traiter le document - aucune extension n'est ignorée grâce à notre PPTXTextLoader personnalisé
            doc_meta = process_document(
                file_path=file_path,
                title=title,
                document_type=doc_type,
                description=description
            )
            
            print(f"✅ Document traité avec succès! ID: {doc_meta.id}")
            success_count += 1
            
            # Petit délai pour éviter de surcharger le système
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {filename}: {str(e)}")
            error_count += 1
    
    # Afficher un résumé
    print("\n" + "="*50)
    print("RÉSUMÉ DE L'IMPORTATION")
    print("="*50)
    print(f"Documents traités avec succès: {success_count}")
    print(f"Documents ignorés: {skipped_count}")
    print(f"Erreurs: {error_count}")
    print("\nTypes de documents:")
    for ext, count in document_types.items():
        print(f"  - {ext}: {count}")
    print("="*50)

if __name__ == "__main__":
    # Obtenir les arguments en ligne de commande
    import argparse
    parser = argparse.ArgumentParser(description='Importer des documents depuis le dossier documents_rice')
    parser.add_argument('--dir', type=str, help='Chemin du dossier documents_rice', 
                       default='/Users/salimkhazem/workspace/AgenticAI/GRDF/documents_rice')
    parser.add_argument('--max', type=int, help='Nombre maximum de documents à importer', default=None)
    
    args = parser.parse_args()
    
    # Importer les documents
    import_documents(args.dir, args.max)
