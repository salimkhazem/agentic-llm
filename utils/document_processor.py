import os
import uuid
import shutil
import json
from datetime import datetime
from typing import List, Dict, Optional

# Mise à jour des imports pour supporter plus de formats
from langchain_community.document_loaders import (
    PyPDFLoader, 
    TextLoader, 
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader
)

# Ajouter l'import du convertisseur PPT personnalisé
from utils.ppt_converter import PPTXTextLoader

# Reste des imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores.base import VectorStore
from langchain.schema import Document
from pydantic import BaseModel
from config import VECTOR_DB_PATH, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_API_VERSION

# Définir le chemin de stockage des documents
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
DOCUMENT_INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "document_index.json")

# Créer les répertoires s'ils n'existent pas
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

class DocumentMetadata(BaseModel):
    id: str
    filename: str
    title: str
    document_type: str
    description: str
    upload_date: str
    file_path: str
    vector_index: Optional[bool] = False

def get_document_loader(file_path: str):
    """Retourne le loader approprié en fonction du type de fichier"""
    extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if extension == '.pdf':
            return PyPDFLoader(file_path)
        elif extension == '.txt':
            return TextLoader(file_path)
        elif extension == '.docx':
            return Docx2txtLoader(file_path)
        elif extension == '.doc':
            # Nécessite unstructured[doc]
            return UnstructuredWordDocumentLoader(file_path)
        elif extension in ['.pptx', '.ppt']:
            # Utiliser notre loader personnalisé au lieu de UnstructuredPowerPointLoader
            return PPTXTextLoader(file_path)
        else:
            raise ValueError(f"Format de fichier non supporté: {extension}")
    except Exception as e:
        raise ValueError(f"Erreur lors du chargement du fichier {extension}: {str(e)}")

def process_document(file_path: str, title: str, document_type: str, description: str) -> DocumentMetadata:
    """Traite un document pour l'extraction et l'indexation"""
    # Générer un ID unique
    doc_id = str(uuid.uuid4())
    
    # Créer les métadonnées du document
    filename = os.path.basename(file_path)
    dest_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{filename}")
    
    # Copier le fichier vers le répertoire des uploads
    shutil.copy2(file_path, dest_path)
    
    # Créer l'objet de métadonnées
    doc_meta = DocumentMetadata(
        id=doc_id,
        filename=filename,
        title=title,
        document_type=document_type,
        description=description,
        upload_date=datetime.now().isoformat(),
        file_path=dest_path,
        vector_index=False
    )
    
    # Enregistrer dans l'index
    save_document_metadata(doc_meta)
    
    # Indexer le document (en mode asynchrone dans un cas réel)
    try:
        index_document(doc_meta)
    except Exception as e:
        print(f"Erreur lors de l'indexation du document {doc_id}: {str(e)}")
    
    return doc_meta

def index_document(doc_meta: DocumentMetadata) -> bool:
    """Indexe le document dans la base vectorielle"""
    try:
        # Charger le document
        loader = get_document_loader(doc_meta.file_path)
        documents = loader.load()
        
        # Découper le document en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunked_documents = text_splitter.split_documents(documents)
        
        # Ajouter des métadonnées aux chunks
        for chunk in chunked_documents:
            chunk.metadata.update({
                "doc_id": doc_meta.id,
                "title": doc_meta.title,
                "document_type": doc_meta.document_type,
                "description": doc_meta.description
            })
        
        # Créer ou mettre à jour l'index vectoriel
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            azure_deployment="text-embedding-ada-002",
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_API_VERSION
        )
        
        # Vérifier si l'index vectoriel existe déjà
        if os.path.exists(os.path.join(VECTOR_DB_PATH, "chroma.sqlite3")):
            # Ajouter à l'index existant
            vectordb = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
            vectordb.add_documents(chunked_documents)
        else:
            # Créer un nouvel index
            vectordb = Chroma.from_documents(
                documents=chunked_documents, 
                embedding=embeddings,
                persist_directory=VECTOR_DB_PATH
            )
        
        # REMARQUE : La méthode persist() n'est plus nécessaire dans les versions récentes
        # de langchain_chroma. Les modifications sont automatiquement sauvegardées.
        # Ne pas utiliser vectordb.persist() qui provoque l'erreur
        
        # Mettre à jour le statut d'indexation dans les métadonnées
        doc_meta.vector_index = True
        save_document_metadata(doc_meta)
        
        return True
    except Exception as e:
        print(f"Erreur d'indexation: {str(e)}")
        return False

def save_document_metadata(doc_meta: DocumentMetadata):
    """Sauvegarde ou met à jour les métadonnées du document dans l'index"""
    documents = []
    
    # Charger l'index existant s'il existe
    if os.path.exists(DOCUMENT_INDEX_PATH):
        with open(DOCUMENT_INDEX_PATH, 'r', encoding='utf-8') as f:
            try:
                documents = json.load(f)
            except json.JSONDecodeError:
                documents = []
    
    # Vérifier si le document existe déjà dans l'index
    updated = False
    for i, doc in enumerate(documents):
        if doc.get('id') == doc_meta.id:
            documents[i] = doc_meta.dict()
            updated = True
            break
    
    # Sinon, ajouter le nouveau document
    if not updated:
        documents.append(doc_meta.dict())
    
    # Sauvegarder l'index
    with open(DOCUMENT_INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

def get_all_documents() -> List[Dict]:
    """Récupère tous les documents de l'index"""
    if not os.path.exists(DOCUMENT_INDEX_PATH):
        return []
    
    with open(DOCUMENT_INDEX_PATH, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def get_document_by_id(doc_id: str) -> Optional[Dict]:
    """Récupère un document par son ID"""
    documents = get_all_documents()
    for doc in documents:
        if doc.get('id') == doc_id:
            return doc
    return None

def delete_document(doc_id: str) -> bool:
    """Supprime un document de l'index et du système de fichiers"""
    doc = get_document_by_id(doc_id)
    if not doc:
        return False
    
    # Supprimer le fichier
    file_path = doc.get('file_path')
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
    
    # Supprimer de l'index
    documents = get_all_documents()
    documents = [d for d in documents if d.get('id') != doc_id]
    
    with open(DOCUMENT_INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    
    # Note: Pour une application complète, il faudrait également supprimer les chunks 
    # correspondants de la base vectorielle, ce qui est plus complexe
    
    return True

def get_vectorstore() -> VectorStore:
    """Récupère la base vectorielle pour la recherche"""
    try:
        # Configurer correctement les embeddings Azure OpenAI avec les bonnes signatures de méthode
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            azure_deployment="text-embedding-ada-002",  # Nom du déploiement dans Azure
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_API_VERSION
        )
        
        # Vérifier si la base vectorielle existe
        if os.path.exists(os.path.join(VECTOR_DB_PATH, "chroma.sqlite3")):
            return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
        else:
            # Retourne une base vide si elle n'existe pas encore
            return Chroma(embedding_function=embeddings, persist_directory=VECTOR_DB_PATH)
    except Exception as e:
        print(f"Erreur lors de l'initialisation du vectorstore: {str(e)}")
        # Créer une fonction simulant un vectorstore vide
        class DummyVectorstore:
            def similarity_search_with_score(self, *args, **kwargs):
                return []
        return DummyVectorstore()

def search_documents(query: str, limit: int = 5) -> List[Dict]:
    """Recherche des documents pertinents pour une requête"""
    try:
        vectorstore = get_vectorstore()
        results = vectorstore.similarity_search_with_score(query, k=limit)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })
        
        return formatted_results
    except Exception as e:
        print(f"Erreur lors de la recherche de documents: {str(e)}")
        return []