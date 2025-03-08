from langchain_openai import AzureChatOpenAI
import os
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_API_VERSION

def get_azure_llm(deployment_name, temperature=0.0):
    """
    Crée et retourne une instance d'AzureChatOpenAI configurée
    
    Args:
        deployment_name: Nom du déploiement Azure OpenAI à utiliser
        temperature: Température pour la génération (0.0 à 1.0)
        
    Returns:
        Instance AzureChatOpenAI
    """
    return AzureChatOpenAI(
        azure_deployment=deployment_name,
        openai_api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        temperature=temperature
    )
