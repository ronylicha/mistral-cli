#!/usr/bin/env python3
"""
Script de test pour les outils d'analyse de fichiers.
"""

import os
import sys
import json
from mistral_cli.cli import Context
from mistral_cli.tools.file_analyzer.file_reader import FileAnalyzer

def test_file_analyzer():
    """Test de base de l'analyseur de fichiers."""
    
    # Créer un fichier de test simple
    test_content = '''
def hello_world():
    print("Hello, World!")
    return "Hello"

def add_numbers(a, b):
    return a + b

if __name__ == "__main__":
    result = hello_world()
    sum_result = add_numbers(5, 3)
    print(f"Sum: {sum_result}")
    '''
    
    test_file = "test_example.py"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        # Note: En production, vous aurez besoin d'une vraie clé API
        print("⚠️ Ce test nécessite une clé API Mistral valide.")
        print("Pour tester réellement, utilisez la commande CLI: mistral-cli")
        print("Puis utilisez: /analyze_file")
        
        # Simulation de test sans API
        print(f"✅ Fichier de test créé: {test_file}")
        print(f"📄 Contenu du fichier: {len(test_content)} caractères")
        
        # Lire le contenu pour vérifier
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
                print(f"📖 Lecture réussie: {len(content)} caractères lus")
        
        print("\n🔍 Types d'analyse disponibles:")
        analysis_types = ["general", "security", "optimization", "documentation", "refactor", "bugs", "style"]
        for i, analysis_type in enumerate(analysis_types, 1):
            print(f"   {i}. {analysis_type}")
        
        print(f"\n✨ Pour tester avec une vraie API:")
        print(f"   1. Lancez: mistral-cli")
        print(f"   2. Utilisez: /analyze_file")
        print(f"   3. Entrez le chemin: {test_file}")
        print(f"   4. Choisissez un type d'analyse")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
    
    finally:
        # Nettoyer
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"🗑️ Fichier de test supprimé: {test_file}")

def test_batch_structure():
    """Test de la structure pour l'analyse par lots."""
    
    # Créer une structure de test
    test_dir = "test_batch_dir"
    os.makedirs(test_dir, exist_ok=True)
    
    # Créer quelques fichiers de test
    files_to_create = {
        "script1.py": "print('Script 1')\ndef function1(): pass",
        "script2.py": "print('Script 2')\ndef function2(): return 42",
        "config.json": '{"setting": "value", "debug": true}',
        "README.md": "# Test Project\nThis is a test project.",
        "app.js": "console.log('Hello from JavaScript');\nfunction greet() { return 'Hi'; }"
    }
    
    try:
        for filename, content in files_to_create.items():
            filepath = os.path.join(test_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
        
        print(f"📁 Répertoire de test créé: {test_dir}")
        print(f"📄 Fichiers créés: {len(files_to_create)}")
        
        # Lister les fichiers créés
        for filename in files_to_create.keys():
            filepath = os.path.join(test_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"   ✅ {filename} ({size} bytes)")
        
        print(f"\n🔍 Pour tester l'analyse par lots:")
        print(f"   1. Lancez: mistral-cli")
        print(f"   2. Utilisez: /analyze_batch")
        print(f"   3. Répertoire: {test_dir}")
        print(f"   4. Patterns: *.py,*.js")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des fichiers de test: {e}")
    
    finally:
        # Nettoyer
        try:
            for filename in files_to_create.keys():
                filepath = os.path.join(test_dir, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
            if os.path.exists(test_dir):
                os.rmdir(test_dir)
            print(f"🗑️ Répertoire de test supprimé: {test_dir}")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage: {e}")

if __name__ == "__main__":
    print("🧪 Test des outils d'analyse de fichiers Mistral CLI\n")
    
    print("=== Test 1: Analyseur de fichier unique ===")
    test_file_analyzer()
    
    print("\n=== Test 2: Structure pour analyse par lots ===")
    test_batch_structure()
    
    print("\n✅ Tests terminés!")
    print("💡 Utilisez 'mistral-cli' pour tester avec une vraie clé API.")