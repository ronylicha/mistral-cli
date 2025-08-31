#!/usr/bin/env python3
"""
Script de test pour l'exécuteur de commandes sur dossiers.
"""

import os
import json
from pathlib import Path

def demonstrate_commands():
    """Démontre l'utilisation des commandes prédéfinies."""
    
    print("🧪 Démonstration de l'exécuteur de commandes sur dossiers\n")
    
    # Vérifier que le dossier de test existe
    test_dir = "exemple_dossier_test"
    if not os.path.exists(test_dir):
        print(f"❌ Dossier de test manquant: {test_dir}")
        print("Créez-le d'abord avec quelques fichiers de code.")
        return
    
    # Lister les fichiers de test
    print(f"📁 Contenu du dossier de test '{test_dir}':")
    for file in os.listdir(test_dir):
        file_path = os.path.join(test_dir, file)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            print(f"   • {file} ({size} bytes)")
    
    print("\n⚡ Commandes disponibles pour l'exécution sur dossiers:\n")
    
    # Simuler les commandes disponibles
    commands = {
        "refactor_all": "Refactoriser tous les fichiers de code pour améliorer la structure",
        "add_documentation": "Ajouter de la documentation manquante à tous les fichiers",
        "security_audit": "Auditer la sécurité et corriger les vulnérabilités",
        "optimize_performance": "Optimiser les performances de tous les fichiers",
        "modernize_code": "Moderniser le code avec les dernières pratiques",
        "add_error_handling": "Ajouter une gestion d'erreurs robuste",
        "clean_code": "Appliquer les principes du Clean Code",
        "add_tests": "Générer des tests unitaires pour le code"
    }
    
    for i, (cmd, desc) in enumerate(commands.items(), 1):
        print(f"  {i:2d}. {cmd:<20} - {desc}")
    
    print(f"\n   0. Commande personnalisée")
    
    print("\n🚀 Pour utiliser ces commandes:")
    print("   1. Lancez: mistral-cli")
    print("   2. Utilisez: /execute_command")
    print("   3. Sélectionnez une commande prédéfinie ou entrez une commande personnalisée")
    print("   4. Configurez le dossier, les patterns de fichiers, et les options")
    print("   5. Confirmez l'exécution")
    
    print("\n💡 Exemples d'utilisation:")
    print("   • Refactoriser tout un projet Python: patterns='*.py', command='refactor_all'")
    print("   • Audit de sécurité sur du code web: patterns='*.js,*.php', command='security_audit'")
    print("   • Ajouter de la doc sur du Java: patterns='*.java', command='add_documentation'")
    print("   • Ordre personnalisé: 'Convertis tous les commentaires en français'")
    
    print("\n🔍 Fonctionnalités avancées:")
    print("   ✅ Analyse récursive des sous-dossiers")
    print("   ✅ Prévisualisation avant exécution")  
    print("   ✅ Application automatique optionnelle")
    print("   ✅ Création de backups automatiques")
    print("   ✅ Rapports détaillés avec statistiques")
    print("   ✅ Filtrage par taille de fichier")
    print("   ✅ Exclusion des dossiers système")
    
    print("\n📊 Exemple de sortie:")
    example_output = {
        "command": "add_documentation",
        "folder_path": "./exemple_dossier_test",
        "total_files_found": 4,
        "files_processed": 4,
        "files_changed": 3,
        "files_skipped": 0,
        "errors_count": 0,
        "apply_changes": True
    }
    
    print(json.dumps(example_output, indent=2, ensure_ascii=False))
    
    print("\n⚠️ Important:")
    print("   • Les fichiers originaux sont toujours sauvegardés (.backup)")
    print("   • Vérifiez les modifications avant de supprimer les backups")
    print("   • Les rapports sont sauvegardés automatiquement")
    print("   • La taille max par fichier est configurable (100KB par défaut)")

def create_demo_scenario():
    """Crée un scénario de démonstration complet."""
    
    print("\n🎯 SCÉNARIO DE DÉMONSTRATION")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Audit de sécurité complet",
            "command": "security_audit",
            "patterns": ["*.py", "*.js", "*.php"],
            "description": "Analyse tous les fichiers de code pour identifier les vulnérabilités"
        },
        {
            "name": "Modernisation de projet legacy",
            "command": "modernize_code",
            "patterns": ["*.java", "*.js"],
            "description": "Met à jour le code avec les dernières bonnes pratiques"
        },
        {
            "name": "Amélioration de la documentation",
            "command": "add_documentation",
            "patterns": ["*.py", "*.java", "*.js"],
            "description": "Ajoute une documentation complète à tous les fichiers"
        },
        {
            "name": "Refactorisation générale",
            "command": "refactor_all", 
            "patterns": ["*.py", "*.js", "*.java", "*.go"],
            "description": "Améliore la structure et la lisibilité du code"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Commande: {scenario['command']}")
        print(f"   Patterns: {', '.join(scenario['patterns'])}")
        print(f"   Description: {scenario['description']}")
    
    print(f"\n💻 Pour exécuter un scénario:")
    print(f"   mistral-cli → /execute_command → [suivre les prompts]")

if __name__ == "__main__":
    demonstrate_commands()
    create_demo_scenario()
    
    print(f"\n✅ Démonstration terminée!")
    print(f"🚀 Utilisez 'mistral-cli' puis '/execute_command' pour tester réellement.")