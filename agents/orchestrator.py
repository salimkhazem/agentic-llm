from langgraph.graph import StateGraph  # Correction de l'importation
from langgraph.graph.graph import END  # Correction de l'importation
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from utils.azure_client import get_azure_llm
from agents.gaz_expert import GazExpertAgent
from agents.veille_agent import VeilleAgent
from agents.visualization_agent import VisualizationAgent
from agents.qa_agent import QAAgent
from config import MODELS
import traceback
from typing import Dict, Any, TypedDict, Literal

# Définir la structure d'état du graphe
class AgentState(TypedDict):
    query: str
    agent_path: str
    response: str

def create_router_chain():
    """Crée une chaîne LLM pour router les requêtes vers le bon agent"""
    llm = get_azure_llm(deployment_name=MODELS["qa"], temperature=0.0)
    
    router_template = """
    Tu es un système intelligent de routage de requêtes pour GRDF.
    Ta mission est d'analyser la requête utilisateur et de déterminer quel agent spécialisé est le mieux placé pour y répondre.

    Les agents disponibles sont:
    1. "expert_gaz": Expert en gaz et infrastructures gazières (distribution, sécurité, réglementations, technologies liées au gaz)
    2. "veille": Agent de veille stratégique (concurrence, tendances du marché, évolutions technologiques et réglementaires)
    3. "visualisation": Agent spécialisé en visualisations et présentations de données
    4. "qa": Agent généraliste de questions-réponses quand la requête ne correspond pas clairement à un autre agent

    Analyse attentivement la requête suivante et réponds uniquement avec le nom de l'agent que tu recommandes (expert_gaz, veille, visualisation ou qa):
    
    Requête: {query}
    """
    
    prompt = PromptTemplate(
        template=router_template,
        input_variables=["query"]
    )
    
    # Utiliser RunnablePassthrough au lieu de LLMChain
    return prompt | llm

def setup_agent_graph():
    """Configure le graphe des agents avec Langgraph"""
    try:
        # Créer les instances d'agents
        gaz_expert = GazExpertAgent()
        veille_agent = VeilleAgent()
        visualization_agent = VisualizationAgent()
        
        # Obtenir les outils (liste vide si erreur)
        try:
            gaz_expert_tools = gaz_expert.get_tools()
        except Exception as e:
            print(f"Erreur lors de l'initialisation des outils de l'expert gaz: {str(e)}")
            gaz_expert_tools = []
            
        try:
            veille_tools = veille_agent.get_tools()
        except Exception as e:
            print(f"Erreur lors de l'initialisation des outils de veille: {str(e)}")
            veille_tools = []
            
        try:
            visualization_tools = visualization_agent.get_tools()
        except Exception as e:
            print(f"Erreur lors de l'initialisation des outils de visualisation: {str(e)}")
            visualization_tools = []
        
        qa_agent = QAAgent(
            gaz_expert_tools=gaz_expert_tools, 
            veille_tools=veille_tools, 
            visualization_tools=visualization_tools
        )
        
        # Créer le routeur
        router_chain = create_router_chain()
        
        # Définir l'état initial - correction pour utiliser la syntaxe actuelle
        workflow = StateGraph(AgentState)
        
        # Wrapper pour sécuriser les appels aux agents
        def safe_process(agent, query):
            try:
                response = agent.process(query)
                if hasattr(response, 'content'):
                    return response.content
                return str(response)
            except Exception as e:
                traceback.print_exc()
                return f"Erreur lors du traitement par l'agent: {str(e)}"
        
        # Ajouter les nœuds d'agents sécurisés
        workflow.add_node("router", lambda state: {"agent_path": router_chain.invoke(state["query"]).content})
        workflow.add_node("expert_gaz", lambda state: {"response": safe_process(gaz_expert, state["query"])})
        workflow.add_node("veille", lambda state: {"response": safe_process(veille_agent, state["query"])})
        workflow.add_node("visualisation", lambda state: {"response": safe_process(visualization_agent, state["query"])})
        workflow.add_node("qa", lambda state: {"response": safe_process(qa_agent, state["query"])})
        
        # Configurer le flux
        workflow.set_entry_point("router")
        
        # Fonction de routage conditionnelle - version corrigée pour les versions récentes de langgraph
        def route_based_on_agent_path(state):
            agent_path = state["agent_path"].strip().lower()
            
            # Mapper le chemin de l'agent à la destination correspondante
            route_map = {
                "expert_gaz": "expert_gaz",
                "veille": "veille", 
                "visualisation": "visualisation",
                "visualization": "visualisation",
                "qa": "qa",
                "q&a": "qa",
                "question": "qa",
            }
            
            # Retourner la destination mappée ou qa par défaut
            return route_map.get(agent_path, "qa")
        
        # Ajouter les conditions de routage avec la syntaxe mise à jour
        workflow.add_conditional_edges("router", route_based_on_agent_path, {
            "expert_gaz": "expert_gaz",
            "veille": "veille",
            "visualisation": "visualisation",
            "qa": "qa"
        })
        
        # Tous les agents vont vers la fin
        for agent in ["expert_gaz", "veille", "visualisation", "qa"]:
            workflow.add_edge(agent, END)
        
        # Compiler le graphe
        return workflow.compile()
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Erreur lors de l'initialisation du graphe d'agents: {str(e)}")

# Initialiser le graphe d'agents
AGENT_GRAPH = None

def run_agent_workflow(query):
    """Exécute le workflow d'agents pour traiter une requête"""
    global AGENT_GRAPH
    
    try:
        if AGENT_GRAPH is None:
            AGENT_GRAPH = setup_agent_graph()
        
        # Exécuter le graphe avec la requête utilisateur
        result = AGENT_GRAPH.invoke({"query": query, "agent_path": "", "response": ""})
        return result["response"]
    except Exception as e:
        traceback.print_exc()
        # Fallback en cas d'échec du graphe d'agents
        llm = get_azure_llm(deployment_name=MODELS["qa"], temperature=0.1)
        fallback_response = llm.invoke(f"Tu es un assistant pour GRDF qui répond aux questions sur le gaz. Question: {query}").content
        return f"[FALLBACK] {fallback_response}"
