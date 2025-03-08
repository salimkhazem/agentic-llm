# Système Multi-Agent GRDF

Ce projet implémente un système multi-agent intelligent pour GRDF (Gaz Réseau Distribution France), permettant de répondre à des questions techniques, effectuer une veille stratégique et créer des visualisations de données.

![Architecture du système](https://i.imgur.com/5XFVmk7.png)

## 🚀 Fonctionnalités

Le système se compose de quatre agents spécialisés :

1. **Agent Expert en Gaz** : Répond aux questions techniques sur le gaz et les infrastructures gazières.
2. **Agent de Veille** : Fournit des analyses sur la concurrence, les tendances et les évolutions réglementaires.
3. **Agent de Visualisation** : Crée des instructions pour produire des graphiques et rapports à partir de données.
4. **Agent QA** : Agent généraliste qui utilise les autres agents pour répondre à des questions diverses.

Un orchestrateur coordonne ces agents, en choisissant le plus adapté à chaque requête utilisateur.

## 💾 Installation

### Prérequis
- Python 3.8+ 
- Clé API Azure OpenAI
- Optionnel : Clé API SerpAPI pour la recherche web

### Installation

1. Clonez ce dépôt :
```bash
git clone <repository-url>
cd GRDF
```

2. Initialisez l'environnement :
```bash
python run_app.py init
```

3. Configurez les variables d'environnement dans le fichier `.env` :
```
AZURE_OPENAI_API_KEY="your-api-key"
AZURE_OPENAI_ENDPOINT="your-endpoint"
AZURE_DEPLOYMENT_NAME="deployment-name"
AZURE_API_VERSION="2023-03-15-preview"
AZURE_EMBEDDINGS_DEPLOYMENT="text-embedding-ada-002"
AZURE_EMBEDDINGS_MODEL="text-embedding-ada-002"
SERPER_API_KEY="your-api-key"
```

## 📖 Utilisation

### Mode test interactif

Pour tester le système avec une interface interactive :

```bash
python test_system.py
# ou
python run_app.py tests
```

### Tests directs

Pour tester un agent spécifique avec une question précise :

```bash
# Tester l'agent expert en gaz
python test_system.py --mode direct --agent gaz --query "Comment fonctionne le réseau de distribution de gaz?"

# Tester l'agent de visualisation avec des données
python test_system.py --mode direct --agent viz --query "Créer un graphique de consommation" --data "Jan:100, Fév:120, Mar:90"

# Tester l'orchestrateur
python test_system.py --mode direct --agent orchestrator --query "Quels sont les concurrents de GRDF?"

# Tester tous les agents avec la même question
python test_system.py --mode direct --agent all --query "Quelles sont les normes de sécurité pour les installations de gaz?"
```

### API Web

Une API web sera bientôt disponible pour intégrer le système dans d'autres applications.

## 📚 Base de connaissances

Le système peut être enrichi avec des documents spécifiques à GRDF :

1. Placez vos documents PDF, DOCX, TXT ou PPT dans le dossier `documents_rice`.
2. Exécutez l'importation :
```bash
python utils/import_rice_documents.py --dir /Users/salimkhazem/workspace/AgenticAI/GRDF/documents_rice
```

3. Explorez les documents importés :
```bash
python utils/advanced_search.py --list
```

4. Recherchez dans la base de connaissances :
```bash
python utils/advanced_search.py --query "normes de sécurité gaz"
```

## 🧩 Architecture technique

### Structure des fichiers

```
GRDF/
├── agents/                 # Agents spécialisés
│   ├── gaz_expert.py       # Agent expert en gaz
│   ├── veille_agent.py     # Agent de veille stratégique
│   ├── visualization_agent.py  # Agent de visualisation
│   ├── qa_agent.py         # Agent généraliste
│   └── orchestrator.py     # Orchestrateur
├── utils/                  # Utilitaires
│   ├── azure_client.py     # Client pour Azure OpenAI
│   ├── document_processor.py  # Traitement des documents
│   ├── ppt_converter.py    # Convertisseur de fichiers PPT
│   └── advanced_search.py  # Recherche avancée dans les documents
├── vectordb/              # Base de données vectorielle
├── uploads/               # Documents importés
├── documents_rice/        # Documents à importer
├── config.py              # Configuration globale
├── test_system.py         # Interface de test
└── run_app.py             # Script de gestion principale
```

### Technologies utilisées

- **LangChain** : Framework pour la création d'applications basées sur des LLM
- **LangGraph** : Orchestration des agents
- **Azure OpenAI** : Modèles de langage et embeddings
- **Chroma DB** : Base de données vectorielle pour la recherche sémantique
- **Rich** : Affichage console amélioré

## 🔒 Sécurité

Les clés API et configurations sensibles doivent être stockées dans le fichier `.env` qui ne doit pas être commité dans le dépôt git.

## 📝 Licence

Tous droits réservés GRDF, 2023-2024.

## 👥 Contributeurs

- Salim Khazem
