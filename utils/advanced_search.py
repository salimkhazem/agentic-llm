import sys
import os
import json
from typing import List, Dict
import argparse

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from utils.document_processor import search_documents, get_all_documents

# Charger les variables d'environnement
load_dotenv()

def display_document_summary(doc_meta: Dict):
    """Affiche un résumé du document"""
    print(f"Titre: {doc_meta.get('title', 'Sans titre')}")
    print(f"Type: {doc_meta.get('document_type', 'Non spécifié')}")
    print(f"Description: {doc_meta.get('description', 'Aucune description')[:100]}...")
    print(f"Date d'ajout: {doc_meta.get('upload_date', 'Non spécifiée')}")
    print("-" * 50)

def list_all_documents():
    """Liste tous les documents dans l'index"""
    documents = get_all_documents()
    
    if not documents:
        print("Aucun document n'a été indexé.")
        return
    
    print(f"\n📚 {len(documents)} documents indexés:")
    print("="*50)
    
    # Regrouper par type de document
    docs_by_type = {}
    for doc in documents:
        doc_type = doc.get('document_type', 'Non catégorisé')
        if doc_type not in docs_by_type:
            docs_by_type[doc_type] = []
        docs_by_type[doc_type].append(doc)
    
    # Afficher par type
    for doc_type, docs in docs_by_type.items():
        print(f"\n## {doc_type.upper()} ({len(docs)} documents)")
        for i, doc in enumerate(docs, 1):
            print(f"[{i}] {doc.get('title', 'Sans titre')}")
    
    print("\n" + "="*50)

def search_knowledge_base(query: str, limit: int = 5, show_content: bool = True):
    """Recherche dans la base de connaissances"""
    print(f"\n🔍 Recherche pour: '{query}'")
    print("="*50)
    
    results = search_documents(query, limit=limit)
    
    if not results:
        print("Aucun résultat trouvé.")
        return
    
    print(f"✅ {len(results)} résultats trouvés:")
    
    for i, result in enumerate(results, 1):
        print(f"\n[RÉSULTAT {i}] Score: {result['score']:.4f}")
        print(f"Document: {result['metadata'].get('title', 'Sans titre')}")
        print(f"Type: {result['metadata'].get('document_type', 'Non spécifié')}")
        
        if show_content:
            print("\nContenu:")
            print("-" * 50)
            print(result['content'])
            print("-" * 50)
    
    print("\n" + "="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Recherche avancée dans la base de connaissances')
    parser.add_argument('--list', action='store_true', help='Lister tous les documents indexés')
    parser.add_argument('--query', type=str, help='Requête de recherche')
    parser.add_argument('--limit', type=int, default=5, help='Nombre maximum de résultats')
    parser.add_argument('--no-content', action='store_true', help='Ne pas afficher le contenu des résultats')
    
    args = parser.parse_args()
    
    if args.list:
        list_all_documents()
    
    if args.query:
        search_knowledge_base(args.query, args.limit, not args.no_content)
    
    if not args.list and not args.query:
        parser.print_help()
