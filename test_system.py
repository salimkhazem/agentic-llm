import os
import sys
import time
import argparse
import json
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

# Charger les variables d'environnement
load_dotenv()

# Importer les modules du système multi-agent
from agents.orchestrator import run_agent_workflow, setup_agent_graph
from agents.gaz_expert import GazExpertAgent
from agents.veille_agent import VeilleAgent
from agents.visualization_agent import VisualizationAgent
from agents.qa_agent import QAAgent
from utils.document_processor import search_documents

# Configuration de l'affichage
console = Console()

def test_document_search(query, limit=3):
    """Recherche des documents pertinents pour une requête"""
    console.print(Panel.fit(
        f"[bold]Recherche de documents pour:[/bold] {query}",
        title="📚 Base de connaissances",
        border_style="blue"
    ))

    start_time = time.time()
    results = search_documents(query, limit=limit)
    duration = time.time() - start_time
    
    if not results:
        console.print("[yellow]Aucun document pertinent trouvé dans la base de connaissances.[/yellow]")
        return None
    
    # Afficher les résultats
    console.print(f"[green]✅ {len(results)} documents trouvés en {duration:.2f}s[/green]")
    
    table = Table(title="Documents pertinents")
    table.add_column("Score", style="cyan", justify="right")
    table.add_column("Document", style="green")
    table.add_column("Extrait", style="yellow")
    
    for result in results:
        score = f"{result['score']:.4f}"
        title = result['metadata'].get('title', 'Sans titre')
        # Tronquer le contenu pour l'affichage
        content = result['content'][:150] + "..." if len(result['content']) > 150 else result['content']
        table.add_row(score, title, content)
    
    console.print(table)
    return results

def test_direct_agent(agent_type, query, data=None):
    """Test direct d'un agent spécifique"""
    agent = None
    
    if agent_type == "gaz":
        agent = GazExpertAgent()
        agent_name = "Expert en Gaz"
        color = "green"
    elif agent_type == "veille":
        agent = VeilleAgent()
        agent_name = "Veille Stratégique"
        color = "blue"
    elif agent_type == "viz":
        agent = VisualizationAgent()
        agent_name = "Visualisation"
        color = "magenta"
        if data is None:
            data = "Consommation en kWh par mois: Janvier: 120, Février: 110, Mars: 95"
    else:
        # Créer l'agent QA avec tous les outils disponibles
        gaz_expert = GazExpertAgent()
        veille_agent = VeilleAgent()
        viz_agent = VisualizationAgent()
        
        agent = QAAgent(
            gaz_expert_tools=gaz_expert.get_tools(),
            veille_tools=veille_agent.get_tools(),
            visualization_tools=viz_agent.get_tools()
        )
        agent_name = "Agent QA"
        color = "yellow"
    
    if not agent:
        console.print(f"[red]Agent {agent_type} non reconnu[/red]")
        return
    
    console.print(Panel.fit(
        f"[bold]Question posée à l'agent {agent_name}:[/bold]\n\n{query}" + 
        (f"\n\nDonnées: {data}" if data and agent_type == "viz" else ""),
        title=f"🤖 Test Agent {agent_name}",
        border_style=color
    ))
    
    # Exécution de l'agent
    start_time = time.time()
    if agent_type == "viz" and data:
        response = agent.process(query, data)
    else:
        response = agent.process(query)
    duration = time.time() - start_time
    
    # Extraire le contenu si c'est un objet de message
    if hasattr(response, 'content'):
        response = response.content
    
    # Afficher la réponse
    console.print(Panel(
        Markdown(str(response)),
        title=f"📝 Réponse ({duration:.2f}s)",
        border_style=color,
        expand=False
    ))
    
    return response

def test_orchestrator(query):
    """Test de l'orchestrateur complet"""
    console.print(Panel.fit(
        f"[bold]Question posée à l'orchestrateur:[/bold]\n\n{query}",
        title="🔄 Test Orchestrateur Multi-Agents",
        border_style="red"
    ))
    
    # Exécution de l'orchestrateur
    start_time = time.time()
    response = run_agent_workflow(query)
    duration = time.time() - start_time
    
    # Afficher la réponse
    console.print(Panel(
        Markdown(str(response)),
        title=f"📝 Réponse Orchestrée ({duration:.2f}s)",
        border_style="red",
        expand=False
    ))
    
    return response

def test_all_components(query, data=None):
    """Test tous les composants avec la même requête"""
    console.print(Panel(
        f"[bold cyan]Test complet du système multi-agent GRDF[/bold cyan]\n\n"
        f"[yellow]Question:[/yellow] {query}\n"
        f"[yellow]Données:[/yellow] {data if data else 'Aucune donnée spécifique fournie'}",
        title="🚀 SYSTÈME MULTI-AGENT GRDF",
        border_style="white"
    ))
    
    # Recherche de documents pour enrichir le contexte
    documents = test_document_search(query)
    
    # Test direct de chaque agent
    console.print("\n[bold]1. Test individuel de chaque agent[/bold]")
    test_direct_agent("gaz", query)
    test_direct_agent("veille", query)
    if data:
        test_direct_agent("viz", query, data)
    test_direct_agent("qa", query)
    
    # Test de l'orchestrateur
    console.print("\n[bold]2. Test de l'orchestrateur complet[/bold]")
    test_orchestrator(query)

def interactive_mode():
    """Mode interactif pour tester le système multi-agent"""
    console.print(Panel(
        "[bold cyan]Mode interactif du système multi-agent GRDF[/bold cyan]\n\n"
        "Posez vos questions pour tester différents agents ou tapez 'exit' pour quitter.",
        title="💬 MODE INTERACTIF",
        border_style="white"
    ))
    
    while True:
        # Demander la question à l'utilisateur
        query = console.input("\n[bold green]Votre question:[/bold green] ")
        
        if query.lower() in ('exit', 'quit', 'q'):
            console.print("[yellow]Au revoir ![/yellow]")
            break
        
        # Demander des données supplémentaires pour la visualisation (optionnel)
        data = None
        need_data = console.input("[bold]Souhaitez-vous fournir des données pour visualisation? (y/n):[/bold] ")
        if need_data.lower() in ('y', 'yes', 'oui'):
            data = console.input("[bold]Données (par exemple, 'Jan: 100, Fév: 120'):[/bold] ")
        
        # Demander quel agent tester
        agent_options = """
Quel agent voulez-vous tester?
1. Expert Gaz
2. Veille Stratégique
3. Visualisation
4. Agent QA (questions-réponses)
5. Orchestrateur (sélection automatique d'agent)
6. Tous les agents
        """
        console.print(Panel(agent_options, title="Choix de l'agent", border_style="blue"))
        choice = console.input("[bold]Votre choix (1-6):[/bold] ")
        
        try:
            choice = int(choice)
            if choice == 1:
                test_direct_agent("gaz", query)
            elif choice == 2:
                test_direct_agent("veille", query)
            elif choice == 3:
                test_direct_agent("viz", query, data)
            elif choice == 4:
                test_direct_agent("qa", query)
            elif choice == 5:
                test_orchestrator(query)
            elif choice == 6:
                test_all_components(query, data)
            else:
                console.print("[red]Choix non valide. Veuillez choisir un nombre entre 1 et 6.[/red]")
        except ValueError:
            console.print("[red]Veuillez entrer un nombre valide.[/red]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test du système multi-agent GRDF")
    
    # Options du mode de test
    parser.add_argument("--mode", choices=["interactive", "direct"], default="interactive",
                       help="Mode de test: interactif ou direct")
    
    # Options pour le mode direct
    parser.add_argument("--agent", choices=["gaz", "veille", "viz", "qa", "orchestrator", "all"],
                       default="orchestrator", help="Agent à tester en mode direct")
    parser.add_argument("--query", type=str, default="Quelles sont les principales normes de sécurité pour les installations de gaz domestiques?",
                       help="Question à poser à l'agent")
    parser.add_argument("--data", type=str, default=None,
                       help="Données à fournir pour la visualisation (uniquement pour l'agent viz)")
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        interactive_mode()
    else:
        if args.agent == "all":
            test_all_components(args.query, args.data)
        elif args.agent == "orchestrator":
            test_orchestrator(args.query)
        else:
            test_direct_agent(args.agent, args.query, args.data)
