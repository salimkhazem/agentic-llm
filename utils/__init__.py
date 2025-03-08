# Ce fichier permet l'importation des fonctions utilitaires comme un module Python
from .azure_client import get_azure_llm

__all__ = [
    'get_azure_llm'
]
