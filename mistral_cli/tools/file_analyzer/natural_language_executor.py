from mistral_cli.cli import Context
import requests
import os
import json
import fnmatch
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class NaturalLanguageExecutor:
    """Exécuteur de commandes en langage naturel sur dossiers et sous-dossiers."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def interpret_natural_command(self, natural_command: str) -> str:
        """Interprète un ordre en langage naturel et le convertit en prompt technique."""
        
        interpretation_prompt = f"""
Tu es un expert en développement logiciel qui interprète les demandes en langage naturel.

Ordre donné par l'utilisateur: "{natural_command}"

Ton rôle:
1. Comprendre exactement ce que l'utilisateur veut faire avec son code
2. Créer un prompt technique précis pour modifier le code selon sa demande
3. Être très spécifique sur les actions à effectuer

Exemples d'interprétation:
- "Ajoute des commentaires partout" → "Ajoute des commentaires explicatifs détaillés à toutes les fonctions, classes et blocs de code complexes"
- "Rends le code plus sûr" → "Ajoute une validation d'entrée, une gestion d'erreurs robuste, et corrige toutes les vulnérabilités de sécurité"
- "Améliore les performances" → "Optimise les algorithmes, réduis la complexité, améliore la gestion mémoire et élimine les goulots d'étranglement"
- "Modernise ce code" → "Met à jour le code avec les dernières fonctionnalités du langage, supprime le code déprécié, applique les bonnes pratiques actuelles"

Réponds uniquement avec le prompt technique à utiliser pour modifier le code.
"""
        
        try:
            data = {
                "model": "mistral-large-latest",
                "messages": [
                    {"role": "system", "content": "Tu es un expert qui convertit les demandes en langage naturel en instructions techniques précises."},
                    {"role": "user", "content": interpretation_prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            interpreted_prompt = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if interpreted_prompt:
                return interpreted_prompt.strip()
            else:
                # Fallback: utiliser la commande directement
                return natural_command
                
        except Exception as e:
            print(f"⚠️ Erreur d'interprétation, utilisation directe: {e}")
            return natural_command
    
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
    
    def execute_natural_command_on_file(self, file_path: str, natural_command: str, interpreted_prompt: str = None) -> Dict[str, Any]:
        """Exécute un ordre en langage naturel sur un fichier spécifique."""
        
        # Lire le contenu du fichier
        content = self.get_file_content(file_path)
        if content.startswith("Erreur"):
            return {
                "success": False,
                "error": content,
                "file_path": file_path
            }
        
        # Utiliser le prompt interprété ou interpréter maintenant
        if not interpreted_prompt:
            interpreted_prompt = self.interpret_natural_command(natural_command)
        
        # Détecter le langage du fichier
        file_extension = Path(file_path).suffix.lower()
        language_info = self._detect_language(file_extension)
        
        # Construire le prompt complet
        full_prompt = f"""
{interpreted_prompt}

Fichier à modifier: {file_path}
Langage: {language_info}

Code original:
{content}

Instructions importantes:
- Applique exactement ce qui est demandé: "{natural_command}"
- Respecte la syntaxe et les conventions du {language_info}
- Préserve toute la fonctionnalité existante
- Fournis uniquement le code final modifié, sans explication ni formatage markdown
- Si aucune modification n'est nécessaire, reproduis le code original à l'identique
"""
        
        try:
            # Appeler l'API Mistral
            data = {
                "model": "mistral-large-latest",
                "messages": [
                    {
                        "role": "system", 
                        "content": f"Tu es un développeur expert en {language_info} qui modifie le code selon les instructions précises. Réponds uniquement avec le code final."
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
            modified_code = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if modified_code:
                # Nettoyer le code (enlever les balises markdown si présentes)
                modified_code = self._clean_code_response(modified_code)
                
                return {
                    "success": True,
                    "original_content": content,
                    "modified_content": modified_code,
                    "file_path": file_path,
                    "natural_command": natural_command,
                    "interpreted_prompt": interpreted_prompt,
                    "changes_detected": content.strip() != modified_code.strip()
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
    
    def execute_natural_command_on_folder(self, folder_path: str, natural_command: str, 
                                        patterns: List[str] = None, 
                                        recursive: bool = True,
                                        apply_changes: bool = False,
                                        max_file_size: int = 100000) -> Dict[str, Any]:
        """Exécute un ordre en langage naturel sur tous les fichiers d'un dossier."""
        
        if not os.path.exists(folder_path):
            return {"success": False, "error": f"Dossier inexistant: {folder_path}"}
        
        if patterns is None:
            patterns = ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.php", "*.rb", "*.rs", "*.cpp", "*.c", "*.cs"]
        
        # Interpréter la commande une seule fois pour tous les fichiers
        print(f"🧠 Interprétation de l'ordre: '{natural_command}'...")
        interpreted_prompt = self.interpret_natural_command(natural_command)
        print(f"💭 Interprétation: {interpreted_prompt[:100]}...")
        
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
        for i, file_path in enumerate(files_to_process, 1):
            print(f"📄 Traitement de: {file_path} ({i}/{len(files_to_process)})")
            
            result = self.execute_natural_command_on_file(file_path, natural_command, interpreted_prompt)
            
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
                                f.write(result["modified_content"])
                                
                            result["backup_created"] = backup_path
                            result["changes_applied"] = True
                            
                        except Exception as e:
                            result["apply_error"] = str(e)
                            errors.append(f"{file_path}: Erreur d'application - {str(e)}")
                
                results.append(result)
            else:
                errors.append(f"{file_path}: {result['error']}")
        
        # Générer un rapport de synthèse
        summary = self._generate_natural_execution_summary(
            natural_command, interpreted_prompt, folder_path, 
            len(files_to_process), files_processed, files_changed, files_skipped, errors
        )
        
        return {
            "success": True,
            "summary": summary,
            "natural_command": natural_command,
            "interpreted_prompt": interpreted_prompt,
            "folder_path": folder_path,
            "total_files_found": len(files_to_process),
            "files_processed": files_processed,
            "files_changed": files_changed,
            "files_skipped": files_skipped,
            "errors_count": len(errors),
            "errors": errors[:10],  # Limiter les erreurs affichées
            "detailed_results": results[:3] if len(results) <= 3 else results[:3] + [
                {"note": f"... et {len(results)-3} autres fichiers traités"}
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
    
    def _generate_natural_execution_summary(self, natural_command: str, interpreted_prompt: str,
                                          folder_path: str, total_files: int, processed: int, 
                                          changed: int, skipped: int, errors: List[str]) -> str:
        """Génère un résumé de l'exécution d'ordre en langage naturel."""
        
        summary = f"""
=== RAPPORT D'EXÉCUTION D'ORDRE EN LANGAGE NATUREL ===

🗣️ Ordre donné: "{natural_command}"
🧠 Interprétation technique: "{interpreted_prompt[:150]}{'...' if len(interpreted_prompt) > 150 else ''}"
📁 Dossier traité: {folder_path}

📊 Statistiques:
• Fichiers trouvés: {total_files}
• Fichiers traités: {processed}
• Fichiers modifiés: {changed}
• Fichiers ignorés: {skipped} (trop volumineux)
• Erreurs: {len(errors)}

📈 Taux de réussite: {(processed/total_files*100):.1f}% si {total_files > 0} else 0.0%
🔄 Taux de modification: {(changed/processed*100):.1f}% si {processed > 0} else 0.0%

💡 L'IA a interprété votre demande et l'a appliquée intelligemment à chaque fichier selon son contexte et son langage.
"""
        
        if errors:
            summary += f"""
⚠️ Erreurs principales:
"""
            for error in errors[:3]:
                summary += f"• {error}\n"
        
        return summary

def execute(context: Context) -> Context:
    """Point d'entrée pour l'exécution d'ordres en langage naturel sur dossier."""
    
    # Récupérer les paramètres
    folder_path = context.data.get("folder_path", ".")
    natural_command = context.data.get("natural_command", "")
    patterns = context.data.get("patterns", ["*.py", "*.js", "*.ts"])
    recursive = context.data.get("recursive", True)
    apply_changes = context.data.get("apply_changes", False)
    max_file_size = context.data.get("max_file_size", 100000)
    
    api_key = context.data.get("api_key")
    if not api_key:
        context.data["output"] = "Erreur: Clé API Mistral manquante."
        return context
    
    if not natural_command:
        context.data["output"] = "Erreur: Ordre en langage naturel manquant."
        return context
    
    try:
        executor = NaturalLanguageExecutor(api_key)
        
        result = executor.execute_natural_command_on_folder(
            folder_path=folder_path,
            natural_command=natural_command,
            patterns=patterns,
            recursive=recursive,
            apply_changes=apply_changes,
            max_file_size=max_file_size
        )
        
        context.data["output"] = json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        context.data["output"] = f"Erreur lors de l'exécution: {str(e)}"
    
    return context