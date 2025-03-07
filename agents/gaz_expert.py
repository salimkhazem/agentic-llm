from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from typing import Dict, Any
from utils.azure_client import get_azure_llm
from config import MODELS, SYSTEM_MESSAGES

class GazExpertAgent:
    """Agent expert en gaz et infrastructure gazière"""
    
    def __init__(self):
        self.llm = get_azure_llm(deployment_name=MODELS["gaz_expert"], temperature=0.1)
        self.system_message = SYSTEM_MESSAGES["gaz_expert"]
        
        # Initialiser le prompt
        self.prompt = PromptTemplate(
            template="""
            {system_message}
            
            Voici une question ou une demande concernant le gaz ou l'infrastructure gazière: {query}
            
            Fournissez une réponse détaillée et technique basée sur votre expertise.
            """,
            input_variables=["query"],
            partial_variables={"system_message": self.system_message}
        )
        
        # Créer une chaîne avec runnable sequence au lieu de LLMChain
        self.chain = self.prompt | self.llm
    
    # Définition des méthodes d'outil sans décorateur
    def distribution_gaz_info(self, query: str) -> str:
        """Outil permettant d'obtenir des informations sur la distribution du gaz"""
        return self.chain.invoke({"query": query})
    
    def securite_gaz_info(self, query: str) -> str:
        """Outil permettant d'obtenir des informations sur la sécurité liée au gaz"""
        return self.chain.invoke({"query": f"Concernant la sécurité gazière: {query}"})
    
    def reglementation_gaz_info(self, query: str) -> str:
        """Outil permettant d'obtenir des informations sur les réglementations du gaz"""
        return self.chain.invoke({"query": f"Concernant la réglementation gazière: {query}"})
    
    def get_tools(self):
        """Retourne les outils disponibles pour cet agent"""
        # Créer des outils en utilisant la classe Tool
        tools = [
            Tool(
                func=self.distribution_gaz_info,
                name="distribution_gaz_info",
                description="Permet d'obtenir des informations sur la distribution du gaz"
            ),
            Tool(
                func=self.securite_gaz_info,
                name="securite_gaz_info",
                description="Permet d'obtenir des informations sur la sécurité liée au gaz"
            ),
            Tool(
                func=self.reglementation_gaz_info,
                name="reglementation_gaz_info",
                description="Permet d'obtenir des informations sur les réglementations du gaz"
            )
        ]
        return tools
    
    def process(self, query):
        """Traite directement une requête avec l'agent expert en gaz"""
        return self.chain.invoke({"query": query})
