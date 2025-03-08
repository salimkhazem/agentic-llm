import os
import sys
import tempfile

# Ajouter le répertoire parent au path pour pouvoir importer correctement
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from utils.document_processor import process_document

# Charger les variables d'environnement
load_dotenv()

def create_sample_document():
    """Crée et indexe un document échantillon pour tester la récupération de documents"""
    # Créer un fichier temporaire avec quelques informations sur les normes de sécurité gaz
    content = """
    # Normes de sécurité pour les installations de gaz domestiques

    ## Introduction
    Les installations de gaz domestiques sont soumises à des normes de sécurité strictes pour garantir la sécurité des utilisateurs.

    ## Principales normes
    1. **NF DTU 61.1** : Cette norme concerne la conception et la mise en œuvre des installations de gaz naturel et de propane.
    2. **Arrêté du 2 août 1977** : Fixe les règles techniques et de sécurité pour les installations de gaz.
    3. **NF EN 1775** : Norme européenne qui spécifie les exigences techniques pour les installations de gaz dans les bâtiments.

    ## Ventilation et évacuation
    Les locaux contenant des appareils de gaz doivent être correctement ventilés pour :
    - Apporter l'air nécessaire à la combustion
    - Évacuer les produits de combustion
    - Prévenir les risques d'intoxication au monoxyde de carbone

    ## Entretien et vérifications
    Les installations de gaz doivent être vérifiées régulièrement par des professionnels qualifiés pour s'assurer de :
    - L'étanchéité des installations
    - Le bon fonctionnement des appareils
    - La conformité aux normes en vigueur
    """

    try:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp:
            temp.write(content)
            temp_path = temp.name

        # Traiter et indexer le document
        doc_meta = process_document(
            file_path=temp_path,
            title="Normes de sécurité gaz domestique",
            document_type="technique",
            description="Document décrivant les principales normes de sécurité pour les installations de gaz domestiques"
        )

        print(f"✅ Document exemple créé avec succès! ID: {doc_meta.id}")
        print(f"Le document est disponible dans: {doc_meta.file_path}")
        
        # Supprimer le fichier temporaire après traitement
        os.unlink(temp_path)
        
        return doc_meta
    except Exception as e:
        print(f"❌ Erreur lors de la création du document exemple: {str(e)}")
        return None

if __name__ == "__main__":
    print("Création d'un document exemple pour tester la récupération de documents...")
    doc = create_sample_document()
    if doc:
        print("Vous pouvez maintenant exécuter 'python test_agents.py --agent documents' pour tester la recherche.")
