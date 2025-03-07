from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from typing import Dict, Any
from langchain_community.utilities.serpapi import SerpAPIWrapper
from utils.azure_client import get_azure_llm
from config import MODELS, SYSTEM_MESSAGES, SERPER_API_KEY, SERP_MAX_RESULTS

class VeilleAgent:
    """Agent de veille stratégique et technologique"""
    
    def __init__(self):
        self.llm = get_azure_llm(deployment_name=MODELS["veille"], temperature=0.3)
        self.system_message = SYSTEM_MESSAGES["veille"]
        
        # Initialiser l'outil de recherche web si la clé API est disponible
        self.search_tool = None
        if SERPER_API_KEY:
            self.search_tool = SerpAPIWrapper(serpapi_api_key=SERPER_API_KEY)
        
        # Initialiser le prompt en utilisant PromptTemplate
        self.prompt = PromptTemplate(
            template="""
            {system_message}
            
            Demande de veille: {query}
            
            {search_results}
            
            Basé sur ces informations et ta connaissance du secteur gazier, fournis une analyse structurée.
            """,
            input_variables=["query", "search_results"],
            partial_variables={"system_message": self.system_message}
        )
        
        # Créer la chaîne avec RunnablePassthrough
        self.chain = RunnablePassthrough.assign(
            response=lambda x: self.llm.invoke(
                self.prompt.format(
                    query=x["query"],
                    search_results=x["search_results"]
                )
            )
        ) | (lambda x: x["response"])
    
    def _perform_search(self, query):
        """Effectue une recherche web sur le sujet demandé"""
        if not self.search_tool:
            return "Aucune recherche web disponible: clé API de recherche non configurée."
            
        try:
            results = self.search_tool.run(f"GRDF {query}")
            return str(results)
        except Exception as e:
            return f"Erreur lors de la recherche: {str(e)}"
    
    # Définition des méthodes d'outil sans décorateur
    def veille_concurrentielle(self, query: str) -> str:
        """Outil pour effectuer une veille concurrentielle dans le secteur du gaz"""
        search_results = self._perform_search(f"concurrents GRDF {query}")
        return self.chain.invoke({"query": query, "search_results": search_results})
    
    def veille_technologique(self, query: str) -> str:
        """Outil pour effectuer une veille technologique liée au gaz"""
        search_results = self._perform_search(f"innovations technologiques gaz {query}")
        return self.chain.invoke({"query": query, "search_results": search_results})
    
    def veille_reglementaire(self, query: str) -> str:
        """Outil pour effectuer une veille réglementaire dans le secteur du gaz"""
        search_results = self._perform_search(f"réglementation gaz France {query}")
        return self.chain.invoke({"query": query, "search_results": search_results})
    
    def get_tools(self):
        """Retourne les outils disponibles pour cet agent"""
        # Créer des outils avec la classe Tool
        tools = [
            Tool(
                func=self.veille_concurrentielle,
                name="veille_concurrentielle",
                description="Permet d'effectuer une veille concurrentielle dans le secteur du gaz"
            ),
            Tool(
                func=self.veille_technologique,
                name="veille_technologique",
                description="Permet d'effectuer une veille technologique liée au gaz"
            ),
            Tool(
                func=self.veille_reglementaire,
                name="veille_reglementaire",
                description="Permet d'effectuer une veille réglementaire dans le secteur du gaz"
            )
        ]
        return tools
    
    def process(self, query):
        """Traite directement une requête avec l'agent de veille"""
        search_results = self._perform_search(query)
        return self.chain.invoke({"query": query, "search_results": search_results})
