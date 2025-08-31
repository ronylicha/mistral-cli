from mistral_cli.cli import Context
import requests
import os
import json
import fnmatch
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class FolderCommandExecutor:
    """Exécuteur de commandes personnalisées sur dossiers et sous-dossiers."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Commandes prédéfinies
        self.predefined_commands = {
            "refactor_all": {
                "description": "Refactoriser tous les fichiers de code pour améliorer la structure",
                "prompt": "Refactorise ce code pour améliorer sa lisibilité, sa maintenabilité et sa performance. Applique les meilleures pratiques du langage."
            },
            "add_documentation": {
                "description": "Ajouter de la documentation manquante à tous les fichiers",
                "prompt": "Ajoute une documentation complète à ce code : docstrings, commentaires explicatifs, et documentation d'API si pertinent."
            },
            "security_audit": {
                "description": "Auditer la sécurité et corriger les vulnérabilités",
                "prompt": "Analyse ce code pour les vulnérabilités de sécurité et applique les corrections nécessaires : validation d'entrée, gestion d'erreurs, protection contre les attaques courantes."
            },
            "optimize_performance": {
                "description": "Optimiser les performances de tous les fichiers",
                "prompt": "Optimise ce code pour de meilleures performances : algorithmes plus efficaces, réduction de la complexité, gestion mémoire améliorée."
            },
            "modernize_code": {
                "description": "Moderniser le code avec les dernières pratiques",
                "prompt": "Modernise ce code en utilisant les dernières fonctionnalités et conventions du langage, supprime le code déprécié."
            },
            "add_error_handling": {
                "description": "Ajouter une gestion d'erreurs robuste",
                "prompt": "Ajoute une gestion d'erreurs complète et robuste à ce code : try-catch appropriés, validation des entrées, messages d'erreur informatifs."
            },
            "clean_code": {
                "description": "Appliquer les principes du Clean Code",
                "prompt": "Nettoie ce code selon les principes du Clean Code : noms explicites, fonctions courtes, suppression du code mort, amélioration de la lisibilité."
            },
            "add_tests": {
                "description": "Générer des tests unitaires pour le code",
                "prompt": "Génère des tests unitaires complets pour ce code : cas de test normaux, cas limites, tests d'erreur. Utilise le framework de test approprié au langage."
            }
        }
    
    def get_file_content(self, file_path: str) -> str:
        """Lit le contenu d'un fichier."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"Erreur de lecture: {str(e)}"
        except Exception as e:
            return f"Erreur de lecture: {str(e)}"
    
    def execute_command_on_file(self, file_path: str, command: str, custom_prompt: str = None) -> Dict[str, Any]:
        """Exécute une commande sur un fichier spécifique."""
        
        # Lire le contenu du fichier
        content = self.get_file_content(file_path)
        if content.startswith("Erreur"):
            return {
                "success": False,
                "error": content,
                "file_path": file_path
            }
        
        # Déterminer le prompt à utiliser
        if custom_prompt:
            prompt = custom_prompt
        elif command in self.predefined_commands:
            prompt = self.predefined_commands[command]["prompt"]
        else:
            prompt = command  # Utiliser la commande directement comme prompt
        
        # Détecter le langage du fichier
        file_extension = Path(file_path).suffix.lower()
        language_info = self._detect_language(file_extension)
        
        # Construire le prompt complet
        full_prompt = f"""
{prompt}

Fichier: {file_path}
Langage: {language_info}

Code original:
{content}

Instructions:
- Respecte la syntaxe et les conventions du {language_info}
- Préserve la fonctionnalité existante
- Améliore uniquement ce qui est nécessaire
- Fournis uniquement le code final, sans explication ni formatage markdown
"""
        
        try:
            # Appeler l'API Mistral
            data = {
                "model": "mistral-large-latest",
                "messages": [
                    {
                        "role": "system", 
                        "content": "Tu es un développeur expert qui améliore le code avec précision. Réponds uniquement avec le code modifié final."
                    },
                    {"role": "user", "content": full_prompt}
                ],
                "max_tokens": 4000,
                "temperature": 0.1
            }
            
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
                improved_code = self._clean_code_response(improved_code)
                
                return {
                    "success": True,
                    "original_content": content,
                    "improved_content": improved_code,
                    "file_path": file_path,
                    "command": command,
                    "changes_detected": content.strip() != improved_code.strip()
                }
            else:
                return {
                    "success": False,
                    "error": "Aucune réponse reçue de l'API",
                    "file_path": file_path
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur API: {str(e)}",
                "file_path": file_path
            }
    
    def execute_command_on_folder(self, folder_path: str, command: str, 
                                 patterns: List[str] = None, 
                                 recursive: bool = True,
                                 custom_prompt: str = None,
                                 apply_changes: bool = False,
                                 max_file_size: int = 100000) -> Dict[str, Any]:
        """Exécute une commande sur tous les fichiers d'un dossier."""
        
        if not os.path.exists(folder_path):
            return {"success": False, "error": f"Dossier inexistant: {folder_path}"}
        
        if patterns is None:
            patterns = ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.php", "*.rb", "*.rs", "*.cpp", "*.c", "*.cs"]
        
        results = []
        errors = []
        files_processed = 0
        files_changed = 0
        files_skipped = 0
        
        # Trouver tous les fichiers
        files_to_process = []
        
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                # Ignorer les répertoires cachés et de build
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                    'node_modules', 'build', 'dist', '__pycache__', 'target', 
                    '.git', '.vscode', '.idea', 'venv', 'env'
                ]]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                        if os.path.getsize(file_path) <= max_file_size:
                            files_to_process.append(file_path)
                        else:
                            files_skipped += 1
        else:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path) and any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                    if os.path.getsize(file_path) <= max_file_size:
                        files_to_process.append(file_path)
                    else:
                        files_skipped += 1
        
        # Traiter chaque fichier
        for file_path in files_to_process:
            print(f"Traitement de: {file_path}")
            
            result = self.execute_command_on_file(file_path, command, custom_prompt)
            
            if result["success"]:
                files_processed += 1
                
                if result.get("changes_detected", False):
                    files_changed += 1
                    
                    # Appliquer les changements si demandé
                    if apply_changes:
                        try:
                            # Créer un backup
                            backup_path = f"{file_path}.backup"
                            with open(backup_path, 'w', encoding='utf-8') as f:
                                f.write(result["original_content"])
                            
                            # Écrire le nouveau contenu
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(result["improved_content"])
                                
                            result["backup_created"] = backup_path
                            result["changes_applied"] = True
                            
                        except Exception as e:
                            result["apply_error"] = str(e)
                            errors.append(f"{file_path}: Erreur d'application - {str(e)}")
                
                results.append(result)
            else:
                errors.append(f"{file_path}: {result['error']}")
        
        # Générer un rapport de synthèse
        summary = self._generate_execution_summary(
            command, folder_path, len(files_to_process), files_processed, 
            files_changed, files_skipped, errors
        )
        
        return {
            "success": True,
            "summary": summary,
            "command": command,
            "folder_path": folder_path,
            "total_files_found": len(files_to_process),
            "files_processed": files_processed,
            "files_changed": files_changed,
            "files_skipped": files_skipped,
            "errors_count": len(errors),
            "errors": errors[:10],  # Limiter les erreurs affichées
            "detailed_results": results[:5] if len(results) <= 5 else results[:5] + [
                {"note": f"... et {len(results)-5} autres fichiers traités"}
            ],
            "apply_changes": apply_changes
        }
    
    def _detect_language(self, file_extension: str) -> str:
        """Détecte le langage basé sur l'extension de fichier."""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.swift': 'Swift',
            '.kt': 'Kotlin'
        }
        return language_map.get(file_extension, 'Code générique')
    
    def _clean_code_response(self, code: str) -> str:
        """Nettoie la réponse de l'API en enlevant les balises markdown."""
        code = code.strip()
        if code.startswith("```"):
            lines = code.split("\n")
            # Enlever la première ligne (```language)
            lines = lines[1:]
            # Enlever la dernière ligne si c'est ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)
        return code
    
    def _generate_execution_summary(self, command: str, folder_path: str, 
                                  total_files: int, processed: int, changed: int, 
                                  skipped: int, errors: List[str]) -> str:
        """Génère un résumé de l'exécution."""
        
        command_name = self.predefined_commands.get(command, {}).get("description", command)
        
        summary = f"""
=== RAPPORT D'EXÉCUTION DE COMMANDE ===

🎯 Commande: {command_name}
📁 Dossier: {folder_path}

📊 Statistiques:
• Fichiers trouvés: {total_files}
• Fichiers traités: {processed}
• Fichiers modifiés: {changed}
• Fichiers ignorés: {skipped} (trop volumineux)
• Erreurs: {len(errors)}

📈 Taux de réussite: {(processed/total_files*100):.1f}% si {total_files > 0} sinon 0.0%
🔄 Taux de modification: {(changed/processed*100):.1f}% si {processed > 0} sinon 0.0%
"""
        
        if errors:
            summary += f"""
⚠️ Erreurs principales:
"""
            for error in errors[:3]:
                summary += f"• {error}\n"
        
        return summary

def execute(context: Context) -> Context:
    """Point d'entrée pour l'exécution de commandes sur dossier."""
    
    # Récupérer les paramètres
    folder_path = context.data.get("folder_path", ".")
    command = context.data.get("command", "")
    patterns = context.data.get("patterns", ["*.py", "*.js", "*.ts"])
    recursive = context.data.get("recursive", True)
    custom_prompt = context.data.get("custom_prompt", None)
    apply_changes = context.data.get("apply_changes", False)
    max_file_size = context.data.get("max_file_size", 100000)
    
    api_key = context.data.get("api_key")
    if not api_key:
        context.data["output"] = "Erreur: Clé API Mistral manquante."
        return context
    
    if not command:
        context.data["output"] = "Erreur: Commande manquante."
        return context
    
    try:
        executor = FolderCommandExecutor(api_key)
        
        result = executor.execute_command_on_folder(
            folder_path=folder_path,
            command=command,
            patterns=patterns,
            recursive=recursive,
            custom_prompt=custom_prompt,
            apply_changes=apply_changes,
            max_file_size=max_file_size
        )
        
        context.data["output"] = json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        context.data["output"] = f"Erreur lors de l'exécution: {str(e)}"
    
    return context