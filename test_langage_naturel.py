#!/usr/bin/env python3
"""
Script de test pour le système d'exécution d'ordres en langage naturel.
"""

import os

def demo_ordres_langage_naturel():
    """Démonstration des ordres en langage naturel."""
    
    print("🗣️ Système d'ordres en langage naturel pour Mistral CLI\n")
    
    print("Le nouveau système permet d'utiliser des ordres en français naturel plutôt que des commandes prédéfinies.")
    print("L'IA interprète vos demandes et les applique intelligemment à chaque fichier.\n")
    
    print("📝 [bold]Exemples d'ordres en langage naturel:[/bold]\n")
    
    # Exemples d'ordres par catégorie
    categories = {
        "📚 Documentation": [
            "Ajoute des commentaires détaillés partout dans le code",
            "Génère une documentation complète pour toutes les fonctions",
            "Écris des docstrings explicatives pour chaque méthode",
            "Ajoute des commentaires d'explication pour le code complexe"
        ],
        "🔒 Sécurité": [
            "Rends ce code plus sûr en ajoutant des validations",
            "Corrige toutes les vulnérabilités de sécurité",
            "Ajoute une validation d'entrée partout où c'est nécessaire",
            "Protège le code contre les attaques courantes"
        ],
        "⚡ Performance": [
            "Améliore les performances de tous ces fichiers",
            "Optimise l'utilisation mémoire",
            "Rends les algorithmes plus efficaces",
            "Élimine les goulots d'étranglement de performance"
        ],
        "🧹 Clean Code": [
            "Applique les principes du Clean Code",
            "Améliore la lisibilité du code",
            "Refactorise pour une meilleure maintenabilité", 
            "Élimine le code dupliqué"
        ],
        "🆕 Modernisation": [
            "Modernise le code avec les dernières pratiques",
            "Convertis le code en utilisant les dernières fonctionnalités",
            "Met à jour le code vers les standards actuels",
            "Remplace le code déprécié par les alternatives modernes"
        ],
        "🛠️ Gestion d'erreurs": [
            "Ajoute une gestion d'erreurs robuste",
            "Améliore la gestion des exceptions",
            "Ajoute des try-catch appropriés partout",
            "Renforce la robustesse du code"
        ],
        "🧪 Tests": [
            "Génère des tests unitaires pour chaque fonction",
            "Crée une suite de tests complète",
            "Ajoute des tests d'intégration",
            "Écris des tests pour tous les cas limites"
        ],
        "🌍 Localisation": [
            "Traduis tous les commentaires en français",
            "Convertis la documentation en anglais",
            "Traduis les messages d'erreur",
            "Localise toutes les chaînes de caractères"
        ],
        "🎨 Style": [
            "Formate le code selon les conventions du langage",
            "Améliore le style et l'indentation",
            "Uniformise le style de codage",
            "Applique les conventions de nommage"
        ],
        "🔄 Personnalisé": [
            "Remplace toutes les boucles for par des list comprehensions",
            "Convertis les fonctions en classes",
            "Ajoute des logs de débogage partout",
            "Remplace print() par logging"
        ]
    }
    
    for category, orders in categories.items():
        print(f"{category}")
        for order in orders:
            print(f"   • « {order} »")
        print()
    
    print("🚀 [bold]Comment utiliser:[/bold]\n")
    print("1. Lancez: mistral-cli")
    print("2. Utilisez: /execute_command")
    print("3. Entrez votre ordre en français naturel")
    print("4. Configurez le dossier et options")
    print("5. L'IA interprète et applique votre demande\n")
    
    print("🧠 [bold]Fonctionnement de l'interprétation:[/bold]\n")
    print("L'IA fait deux étapes:")
    print("1. Interprète votre ordre en français → prompt technique précis")
    print("2. Applique le prompt technique à chaque fichier selon son contexte\n")
    
    print("💡 [bold]Avantages du langage naturel:[/bold]\n")
    print("✅ Plus intuitif et flexible que les commandes prédéfinies")
    print("✅ S'adapte automatiquement à chaque langage de programmation") 
    print("✅ Comprend les nuances et intentions derrière vos demandes")
    print("✅ Permet des demandes très spécifiques et personnalisées")
    print("✅ Combine plusieurs actions en une seule demande\n")
    
    print("📊 [bold]Exemples concrets d'utilisation:[/bold]\n")
    
    scenarios = [
        {
            "situation": "Projet legacy sans documentation",
            "ordre": "Ajoute une documentation complète avec des exemples d'usage",
            "resultat": "Génère docstrings, commentaires et documentation API"
        },
        {
            "situation": "Code avec problèmes de sécurité", 
            "ordre": "Rends ce code sécurisé pour la production",
            "resultat": "Ajoute validation, sanitisation et gestion d'erreurs"
        },
        {
            "situation": "Application lente",
            "ordre": "Optimise ce code pour de meilleures performances",
            "resultat": "Améliore algorithmes, cache et gestion mémoire"
        },
        {
            "situation": "Code difficile à maintenir",
            "ordre": "Refactorise ce code selon les principes SOLID",
            "resultat": "Restructure en classes, sépare responsabilités"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. [bold]{scenario['situation']}[/bold]")
        print(f"   Ordre: « {scenario['ordre']} »")
        print(f"   Résultat: {scenario['resultat']}\n")
    
    print("⚠️ [bold]Conseils pour de meilleurs résultats:[/bold]\n")
    print("• Soyez précis dans vos demandes")
    print("• Mentionnez le contexte si nécessaire (production, développement, etc.)")
    print("• Combinez plusieurs actions: 'Ajoute des commentaires ET améliore les performances'")
    print("• Utilisez des exemples: 'Comme dans les bonnes pratiques de React'")
    print("• Spécifiez le niveau: 'documentation niveau débutant' vs 'documentation technique'\n")

def test_interpretation():
    """Teste l'interprétation d'ordres basiques."""
    
    print("🧪 [bold]Test d'interprétation (simulation)[/bold]\n")
    
    test_cases = [
        {
            "ordre": "Ajoute des commentaires partout",
            "interpretation_attendue": "Ajoute des commentaires explicatifs détaillés à toutes les fonctions, classes et blocs de code complexes"
        },
        {
            "ordre": "Rends le code plus sûr",
            "interpretation_attendue": "Ajoute une validation d'entrée, une gestion d'erreurs robuste, et corrige toutes les vulnérabilités de sécurité"
        },
        {
            "ordre": "Optimise les performances",
            "interpretation_attendue": "Optimise les algorithmes, réduis la complexité, améliore la gestion mémoire et élimine les goulots d'étranglement"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}:")
        print(f"   Ordre utilisateur: « {test['ordre']} »")
        print(f"   Interprétation IA: « {test['interpretation_attendue']} »\n")
    
    print("💭 L'IA adapte ensuite cette interprétation au contexte de chaque fichier (langage, complexité, etc.)")

if __name__ == "__main__":
    demo_ordres_langage_naturel()
    print("\n" + "="*60 + "\n")
    test_interpretation()
    
    print("\n✅ Démonstration terminée!")
    print("🚀 Utilisez 'mistral-cli' puis '/execute_command' pour tester avec une vraie clé API.")