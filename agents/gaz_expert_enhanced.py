from langchain.agents import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from utils.azure_client import get_azure_llm
from utils.document_processor import search_documents
from config import MODELS, SYSTEM_MESSAGES
from typing import List, Dict

class EnhancedGazExpertAgent:
    """Version améliorée de l'agent expert en gaz utilisant la base documentaire"""
    
    def __init__(self):
        self.llm = get_azure_llm(deployment_name=MODELS["gaz_expert"], temperature=0.1)
        self.system_message = SYSTEM_MESSAGES["gaz_expert"]
        
        # Initialiser la chaîne principale avec RAG (Retrieval Augmented Generation)
        self.prompt = PromptTemplate(
            template="""
            {system_message}
            
            Voici une question ou une demande concernant le gaz ou l'infrastructure gazière: {query}
            
            Documents pertinents trouvés dans notre base de connaissances:
            {context}
            
            Fournissez une réponse détaillée et technique basée sur votre expertise et les documents fournis.
            Si les documents ne contiennent pas d'informations pertinentes, basez-vous sur vos connaissances générales.
            """,
            input_variables=["query", "context"],
            partial_variables={"system_message": self.system_message}
        )
        
        # Chaîne simple sans recherche documentaire
        self.simple_prompt = PromptTemplate(
            template="""
            {system_message}
            
            Voici une question ou une demande concernant le gaz ou l'infrastructure gazière: {query}
            
            Fournissez une réponse détaillée et technique basée sur votre expertise.
            """,
            input_variables=["query"],
            partial_variables={"system_message": self.system_message}
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.simple_chain = LLMChain(llm=self.llm, prompt=self.simple_prompt)
    
    def _format_context(self, documents: List[Dict]) -> str:
        """Formate les documents pour la présentation dans le prompt"""
        if not documents:
            return "Aucun document pertinent trouvé."
        
        context = []
        for i, doc in enumerate(documents, start=1):
            content = doc["content"]
            metadata = doc["metadata"]
            title = metadata.get("title", "Document sans titre")
            doc_type = metadata.get("document_type", "Type inconnu")
            
            context.append(f"Document {i} ({doc_type}): {title}\n{content}\n")
        
        return "\n".join(context)
    
    @tool
    def distribution_gaz_info(self, query):
        """Outil permettant d'obtenir des informations sur la distribution du gaz"""
        # Rechercher des documents pertinents
        docs = search_documents(f"distribution gaz {query}", limit=3)
        context = self._format_context(docs)
        
        # Exécuter la chaîne avec les documents récupérés
        return self.chain.run(query=query, context=context)
    
    @tool
    def securite_gaz_info(self, query):
        """Outil permettant d'obtenir des informations sur la sécurité liée au gaz"""
        docs = search_documents(f"sécurité gaz {query}", limit=3)
        context = self._format_context(docs)
        
        return self.chain.run(query=f"Concernant la sécurité gazière: {query}", context=context)
    
    @tool
    def reglementation_gaz_info(self, query):
        """Outil permettant d'obtenir des informations sur les réglementations du gaz"""
        docs = search_documents(f"réglementation gaz {query}", limit=3)
        context = self._format_context(docs)
        
        return self.chain.run(query=f"Concernant la réglementation gazière: {query}", context=context)
    
    def get_tools(self):
        """Retourne les outils disponibles pour cet agent"""
        return [
            self.distribution_gaz_info,
            self.securite_gaz_info,
            self.reglementation_gaz_info
        ]
    
    def process(self, query):
        """Traite directement une requête avec l'agent expert en gaz"""
        # Rechercher des documents pertinents
        docs = search_documents(query, limit=3)
        
        # Si des documents sont trouvés, utiliser la chaîne avec RAG
        if docs:
            context = self._format_context(docs)
            return self.chain.run(query=query, context=context)
        
        # Sinon, utiliser la chaîne simple
        return self.simple_chain.run(query=query)
