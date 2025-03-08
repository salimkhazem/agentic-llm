from dotenv import load_dotenv
import argparse
import json
import time
import traceback
import sys

# Charger les variables d'environnement avant d'importer les modules qui en dépendent
load_dotenv()

from agents.gaz_expert import GazExpertAgent
from agents.veille_agent import VeilleAgent
from agents.visualization_agent import VisualizationAgent
from agents.qa_agent import QAAgent
from agents.orchestrator import run_agent_workflow
from utils.document_processor import search_documents

def extract_content(response):
    """Extrait le contenu d'une réponse, qu'elle soit une chaîne ou un objet AIMessage"""
    if hasattr(response, 'content'):
        return response.content
    return str(response)

def test_gaz_expert(query):
    """Tester l'agent expert en gaz"""
    print("\n📊 TEST AGENT EXPERT EN GAZ")
    print("-" * 50)
    print(f"📝 Question: {query}")
    print("-" * 50)
    
    agent = GazExpertAgent()
    start_time = time.time()
    response = agent.process(query)
    end_time = time.time()
    
    response_content = extract_content(response)
    
    print(f"⏱️  Temps de réponse: {end_time - start_time:.2f} secondes")
    print("-" * 50)
    print(f"🔍 Réponse:\n{response_content}")
    print("-" * 50)
    
    # Tester les outils spécifiques
    print("\n🛠️  Test des outils spécifiques:")
    tools = agent.get_tools()
    tool_names = [tool.name for tool in tools]
    print(f"Outils disponibles: {tool_names}")
    
    # Tester un outil spécifique
    try:
        if "securite_gaz_info" in tool_names:
            securite_tool = next(t for t in tools if t.name == "securite_gaz_info")
            print("\n🔒 Test de l'outil securite_gaz_info:")
            security_query = "Quels sont les principaux risques liés au gaz domestique?"
            print(f"Question: {security_query}")
            security_response = securite_tool.func(security_query)
            security_content = extract_content(security_response)
            print(f"Réponse: {security_content[:200]}...")
    except Exception as e:
        print(f"Erreur lors du test de l'outil: {str(e)}")
        traceback.print_exc()

def test_veille_agent(query):
    """Tester l'agent de veille"""
    print("\n📰 TEST AGENT DE VEILLE")
    print("-" * 50)
    print(f"📝 Question: {query}")
    print("-" * 50)
    
    agent = VeilleAgent()
    start_time = time.time()
    response = agent.process(query)
    end_time = time.time()
    
    response_content = extract_content(response)
    
    print(f"⏱️  Temps de réponse: {end_time - start_time:.2f} secondes")
    print("-" * 50)
    print(f"🔍 Réponse:\n{response_content}")
    print("-" * 50)
    
    # Tester les outils spécifiques
    print("\n🛠️  Test des outils spécifiques:")
    tools = agent.get_tools()
    tool_names = [tool.name for tool in tools]
    print(f"Outils disponibles: {tool_names}")
    
    # Tester un outil spécifique
    try:
        if "veille_concurrentielle" in tool_names:
            veille_tool = next(t for t in tools if t.name == "veille_concurrentielle")
            print("\n🏢 Test de l'outil veille_concurrentielle:")
            veille_query = "Quels sont les principaux concurrents de GRDF?"
            print(f"Question: {veille_query}")
            veille_response = veille_tool.func(veille_query)
            veille_content = extract_content(veille_response)
            print(f"Réponse: {veille_content[:200]}...")
    except Exception as e:
        print(f"Erreur lors du test de l'outil: {str(e)}")
        traceback.print_exc()

def test_visualization_agent(query, data):
    """Tester l'agent de visualisation"""
    print("\n📈 TEST AGENT DE VISUALISATION")
    print("-" * 50)
    print(f"📝 Demande: {query}")
    print(f"📋 Données: {data}")
    print("-" * 50)
    
    agent = VisualizationAgent()
    start_time = time.time()
    response = agent.process(query, data)
    end_time = time.time()
    
    response_content = extract_content(response)
    
    print(f"⏱️  Temps de réponse: {end_time - start_time:.2f} secondes")
    print("-" * 50)
    print(f"🔍 Réponse:\n{response_content}")
    print("-" * 50)
    
    # Tester les outils spécifiques
    print("\n🛠️  Test des outils spécifiques:")
    tools = agent.get_tools()
    tool_names = [tool.name for tool in tools]
    print(f"Outils disponibles: {tool_names}")
    
    # Tester un outil spécifique
    try:
        if "create_chart" in tool_names:
            chart_tool = next(t for t in tools if t.name == "create_chart")
            print("\n📊 Test de l'outil create_chart:")
            chart_input = "Créer un graphique de consommation mensuelle|||Janvier: 120, Février: 110, Mars: 95"
            print(f"Entrée: {chart_input}")
            chart_response = chart_tool.func(chart_input)
            chart_content = extract_content(chart_response)
            print(f"Réponse: {chart_content[:200]}...")
    except Exception as e:
        print(f"Erreur lors du test de l'outil: {str(e)}")
        traceback.print_exc()

def test_qa_agent(query):
    """Tester l'agent QA"""
    print("\n❓ TEST AGENT QA")
    print("-" * 50)
    print(f"📝 Question: {query}")
    print("-" * 50)
    
    # Créer des instances des autres agents pour leurs outils
    gaz_expert = GazExpertAgent()
    veille_agent = VeilleAgent()
    visualization_agent = VisualizationAgent()
    
    agent = QAAgent(
        gaz_expert_tools=gaz_expert.get_tools(),
        veille_tools=veille_agent.get_tools(),
        visualization_tools=visualization_agent.get_tools()
    )
    
    start_time = time.time()
    response = agent.process(query)
    end_time = time.time()
    
    print(f"⏱️  Temps de réponse: {end_time - start_time:.2f} secondes")
    print("-" * 50)
    print(f"🔍 Réponse:\n{response}")
    print("-" * 50)

def test_document_retrieval(query):
    """Tester la récupération de documents pertinents"""
    print("\n📚 TEST DE RÉCUPÉRATION DE DOCUMENTS")
    print("-" * 50)
    print(f"📝 Requête: {query}")
    print("-" * 50)
    
    try:
        # Capture les erreurs de manière plus détaillée
        docs = search_documents(query, limit=3)
        
        if not docs:
            print("❌ Aucun document pertinent trouvé.")
        else:
            print(f"✅ {len(docs)} documents trouvés:")
            for i, doc in enumerate(docs, 1):
                print(f"\n📄 Document {i}:")
                print(f"Score de pertinence: {doc['score']:.4f}")
                print(f"Métadonnées: {json.dumps(doc['metadata'], indent=2)}")
                print(f"Contenu: {doc['content'][:200]}...")
    except Exception as e:
        print(f"❌ Erreur lors de la recherche de documents: {str(e)}")
        traceback.print_exc(file=sys.stderr)
    
    print("-" * 50)

def test_orchestrator(query):
    """Tester l'orchestrateur d'agents"""
    print("\n🔄 TEST ORCHESTRATEUR")
    print("-" * 50)
    print(f"📝 Question: {query}")
    print("-" * 50)
    
    start_time = time.time()
    response = run_agent_workflow(query)
    end_time = time.time()
    
    print(f"⏱️  Temps de réponse: {end_time - start_time:.2f} secondes")
    print("-" * 50)
    print(f"🔍 Réponse:\n{response}")
    print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description='Tester les agents GRDF individuellement')
    parser.add_argument('--agent', choices=['gaz', 'veille', 'viz', 'qa', 'documents', 'orchestrator', 'all'], 
                        help='Agent à tester', required=True)
    parser.add_argument('--query', type=str, help='Question à poser', 
                        default="Quelles sont les principales normes de sécurité pour les installations de gaz domestiques?")
    parser.add_argument('--data', type=str, help='Données pour l\'agent de visualisation',
                        default="Consommation en kWh par mois: Janvier: 120, Février: 110, Mars: 95, Avril: 85, Mai: 75")
    
    args = parser.parse_args()
    
    if args.agent == 'gaz' or args.agent == 'all':
        test_gaz_expert(args.query)
        
    if args.agent == 'veille' or args.agent == 'all':
        test_veille_agent(args.query)
        
    if args.agent == 'viz' or args.agent == 'all':
        test_visualization_agent(args.query, args.data)
        
    if args.agent == 'qa' or args.agent == 'all':
        test_qa_agent(args.query)
        
    if args.agent == 'documents' or args.agent == 'all':
        test_document_retrieval(args.query)
        
    if args.agent == 'orchestrator' or args.agent == 'all':
        test_orchestrator(args.query)

if __name__ == "__main__":
    main()
