from mistral_cli.cli import Context
import requests
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class FileAnalyzer:
    """Analyseur de fichiers qui utilise l'API Mistral pour l'interprétation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def read_file_content(self, file_path: str) -> str:
        """Lit le contenu d'un fichier."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Si le fichier n'est pas en UTF-8, essayer avec d'autres encodages
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"Erreur de lecture du fichier: {str(e)}"
        except Exception as e:
            return f"Erreur de lecture du fichier: {str(e)}"
    
    def analyze_with_mistral(self, content: str, analysis_type: str = "general", 
                           custom_prompt: str = None) -> str:
        """Envoie le contenu à l'API Mistral pour analyse."""
        
        # Prompts prédéfinis pour différents types d'analyse
        prompts = {
            "general": "Analyse ce code ou fichier et fournis un résumé des fonctionnalités principales, problèmes potentiels et suggestions d'amélioration.",
            "security": "Analyse ce code pour identifier les vulnérabilités de sécurité potentielles, les failles et les bonnes pratiques manquantes.",
            "optimization": "Analyse ce code et suggère des optimisations possibles en termes de performance, lisibilité et maintenabilité.",
            "documentation": "Analyse ce code et génère de la documentation appropriée incluant des commentaires et une documentation d'API si pertinent.",
            "refactor": "Analyse ce code et propose des suggestions de refactorisation pour améliorer sa structure et sa qualité.",
            "bugs": "Analyse ce code pour identifier les bugs potentiels, erreurs de logique et problèmes de robustesse.",
            "style": "Analyse ce code et vérifie s'il respecte les conventions de style et bonnes pratiques du langage."
        }
        
        system_prompt = custom_prompt or prompts.get(analysis_type, prompts["general"])
        
        data = {
            "model": "mistral-large-latest",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Voici le contenu à analyser:\n\n{content}"}
            ],
            "max_tokens": 2000,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "Aucune réponse reçue.")
        
        except requests.RequestException as e:
            return f"Erreur lors de l'appel à l'API Mistral: {str(e)}"
    
    def generate_improvements(self, content: str, analysis_result: str) -> str:
        """Génère des améliorations basées sur l'analyse."""
        
        prompt = f"""
        Basé sur cette analyse:
        {analysis_result}
        
        Et ce code original:
        {content}
        
        Fournis des suggestions concrètes d'amélioration avec des exemples de code corrigé si possible.
        Format de réponse souhaité:
        1. Problèmes identifiés
        2. Solutions proposées 
        3. Code amélioré (si applicable)
        """
        
        data = {
            "model": "mistral-large-latest",
            "messages": [
                {"role": "system", "content": "Tu es un expert en développement logiciel qui fournit des suggestions d'amélioration précises et actionables."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 3000,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "Aucune suggestion générée.")
        
        except requests.RequestException as e:
            return f"Erreur lors de la génération des améliorations: {str(e)}"
    
    def apply_suggestions(self, file_path: str, original_content: str, suggestions: str) -> bool:
        """Applique les suggestions d'amélioration au fichier."""
        
        # Créer un backup du fichier original
        backup_path = f"{file_path}.backup"
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
        except Exception as e:
            print(f"Erreur lors de la création du backup: {str(e)}")
            return False
        
        # Demander à Mistral de générer le code modifié
        prompt = f"""
        Applique les suggestions suivantes au code original et fournis uniquement le code final complet et fonctionnel:
        
        Suggestions:
        {suggestions}
        
        Code original:
        {original_content}
        
        Réponds uniquement avec le code modifié, sans explication ni formatage markdown.
        """
        
        data = {
            "model": "mistral-large-latest",
            "messages": [
                {"role": "system", "content": "Tu es un développeur expert qui applique des modifications de code avec précision. Réponds uniquement avec le code final."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            improved_code = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if improved_code:
                # Nettoyer le code (enlever les balises markdown si présentes)
                improved_code = improved_code.strip()
                if improved_code.startswith("```"):
                    lines = improved_code.split("\n")
                    # Enlever la première ligne (```language)
                    lines = lines[1:]
                    # Enlever la dernière ligne si c'est ```
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    improved_code = "\n".join(lines)
                
                # Écrire le code amélioré
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(improved_code)
                return True
            
        except Exception as e:
            print(f"Erreur lors de l'application des suggestions: {str(e)}")
            # Restaurer le backup en cas d'erreur
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    original = f.read()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(original)
            except:
                pass
        
        return False

def execute(context: Context) -> Context:
    """Point d'entrée principal pour l'analyse de fichiers."""
    
    # Récupérer les paramètres du contexte
    file_path = context.data.get("file_path", "")
    analysis_type = context.data.get("analysis_type", "general")
    custom_prompt = context.data.get("custom_prompt", None)
    apply_improvements = context.data.get("apply_improvements", False)
    
    if not file_path or not os.path.exists(file_path):
        context.data["output"] = "Erreur: Chemin de fichier invalide ou inexistant."
        return context
    
    # Récupérer la clé API (supposons qu'elle soit disponible dans le contexte)
    api_key = context.data.get("api_key")
    if not api_key:
        context.data["output"] = "Erreur: Clé API Mistral manquante."
        return context
    
    try:
        analyzer = FileAnalyzer(api_key)
        
        # 1. Lire le contenu du fichier
        content = analyzer.read_file_content(file_path)
        if content.startswith("Erreur"):
            context.data["output"] = content
            return context
        
        # 2. Analyser avec Mistral
        analysis = analyzer.analyze_with_mistral(content, analysis_type, custom_prompt)
        
        # 3. Générer des suggestions d'amélioration
        suggestions = analyzer.generate_improvements(content, analysis)
        
        # 4. Appliquer les améliorations si demandé
        applied = False
        if apply_improvements:
            applied = analyzer.apply_suggestions(file_path, content, suggestions)
        
        # Préparer la sortie
        output = {
            "file_path": file_path,
            "analysis_type": analysis_type,
            "analysis": analysis,
            "suggestions": suggestions,
            "improvements_applied": applied
        }
        
        context.data["output"] = json.dumps(output, indent=2, ensure_ascii=False)
        
    except Exception as e:
        context.data["output"] = f"Erreur lors de l'analyse: {str(e)}"
    
    return context