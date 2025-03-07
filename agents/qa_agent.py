from langchain.agents import initialize_agent, AgentType, create_react_agent
from langchain.memory import ConversationBufferMemory, ConversationTokenBufferMemory
from langchain.tools import tool, BaseTool
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, Field  # Utilisation de pydantic directement
from langchain_core.runnables import RunnablePassthrough
from typing import List, Dict, Any, Optional
from utils.azure_client import get_azure_llm
from config import MODELS, SYSTEM_MESSAGES

class QAAgent:
    """Agent principal de questions-réponses qui coordonne les autres agents"""
    
    def __init__(self, gaz_expert_tools=None, veille_tools=None, visualization_tools=None):
        self.llm = get_azure_llm(deployment_name=MODELS["qa"], temperature=0.1)
        self.system_message = SYSTEM_MESSAGES["qa"]
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Collecter tous les outils disponibles et les adapter au besoin
        self.tools = []
        if gaz_expert_tools:
            # Utiliser des versions simplifiées des outils si nécessaire
            for tool in gaz_expert_tools:
                self.tools.append(tool)
        
        if veille_tools:
            for tool in veille_tools:
                self.tools.append(tool)
                
        if visualization_tools:
            # Pas d'ajout des outils de visualisation qui sont plus complexes
            pass
            
        # Ajouter l'outil de réponse directe
        self.tools.append(self._create_answer_tool())
        
    def _create_answer_tool(self):
        """Crée un outil de réponse directe"""
        @tool("answer_question", return_direct=True)
        def answer_question(query: str) -> str:
            """Répond directement à une question sans utiliser d'autres outils."""
            response = self.llm.predict(f"{self.system_message}\n\nQuestion: {query}\n\nRéponse:")
            return response
            
        return answer_question
        
    def process(self, query):
        """Traite une requête en utilisant l'agent QA"""
        if not self.tools or len(self.tools) <= 1:
            # Si aucun outil n'est disponible ou seulement l'outil de réponse, répondre directement
            return self.llm.predict(f"{self.system_message}\n\nQuestion: {query}\n\nRéponse:")
        
        try:
            # Créer un prompt personnalisé pour l'agent
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"{self.system_message}\n\nUtilisez les outils à votre disposition lorsque cela est pertinent, sinon répondez directement. Vous êtes un expert en gaz naturel et infrastructure gazière pour GRDF."),
                ("human", "{input}"),
                ("human", "Pensez étape par étape et utilisez les outils nécessaires pour répondre à cette question.")
            ])
            
            # Créer un agent plus simple avec ZERO_SHOT_REACT_DESCRIPTION
            agent_executor = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # Utilisez un agent plus simple
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=3
            )
            
            #return agent_executor.run(query)
            return agent_executor.invoke({"input": query})

            
        except Exception as e:
            print(f"Erreur lors de l'exécution de l'agent: {str(e)}")
            # En cas d'erreur, répondre directement
            return f"Je rencontre des difficultés techniques pour traiter votre demande. Je vais vous répondre directement:\n\n" + self.llm.predict(f"{self.system_message}\n\nQuestion: {query}\n\nRéponse:")
