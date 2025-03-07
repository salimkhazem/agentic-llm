from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from typing import Dict, Any
from utils.azure_client import get_azure_llm
from config import MODELS, SYSTEM_MESSAGES

class VisualizationAgent:
    """Agent spécialisé dans la création de visualisations et de rapports"""
    
    def __init__(self):
        self.llm = get_azure_llm(deployment_name=MODELS["visualization"], temperature=0.2)
        self.system_message = SYSTEM_MESSAGES["visualization"]
        
        # Initialiser le prompt
        self.prompt = PromptTemplate(
            template="""
            {system_message}
            
            Demande de visualisation: {query}
            
            Données à visualiser ou informations à présenter: {data}
            
            Fournis des instructions détaillées pour créer la visualisation ou le document demandé.
            """,
            input_variables=["query", "data"],
            partial_variables={"system_message": self.system_message}
        )
        
        # Créer la chaîne avec RunnablePassthrough
        self.chain = RunnablePassthrough.assign(
            response=lambda x: self.llm.invoke(
                self.prompt.format(
                    query=x["query"],
                    data=x["data"]
                )
            )
        ) | (lambda x: x["response"])
    
    # Définition des méthodes d'outil sans décorateur
    def create_chart(self, query_and_data: str) -> str:
        """Outil pour créer des instructions détaillées de graphiques ou charts."""
        parts = query_and_data.split("|||")
        if len(parts) != 2:
            return "Format incorrect. Utiliser 'demande||| données'"
        
        query, data = parts
        return self.chain.invoke({"query": query, "data": data})
    
    def create_excel(self, query_and_data: str) -> str:
        """Outil pour créer des instructions détaillées pour des tableaux Excel."""
        parts = query_and_data.split("|||")
        if len(parts) != 2:
            return "Format incorrect. Utiliser 'demande||| données'"
        
        query, data = parts
        return self.chain.invoke({"query": f"Créer un tableau Excel pour {query}", "data": data})
    
    def create_report(self, query_and_data: str) -> str:
        """Outil pour créer des instructions détaillées pour des rapports."""
        parts = query_and_data.split("|||")
        if len(parts) != 2:
            return "Format incorrect. Utiliser 'demande||| données'"
        
        query, data = parts
        return self.chain.invoke({"query": f"Créer un rapport pour {query}", "data": data})
    
    def get_tools(self):
        """Retourne les outils disponibles pour cet agent"""
        # Créer des outils avec la classe Tool
        tools = [
            Tool(
                func=self.create_chart,
                name="create_chart",
                description="Crée des instructions détaillées pour des graphiques (format: 'demande||| données')"
            ),
            Tool(
                func=self.create_excel,
                name="create_excel",
                description="Crée des instructions détaillées pour des tableaux Excel (format: 'demande||| données')"
            ),
            Tool(
                func=self.create_report,
                name="create_report",
                description="Crée des instructions détaillées pour des rapports (format: 'demande||| données')"
            )
        ]
        return tools
    
    def process(self, query, data="Aucune donnée fournie"):
        """Traite directement une requête avec l'agent de visualisation"""
        return self.chain.invoke({"query": query, "data": data})
