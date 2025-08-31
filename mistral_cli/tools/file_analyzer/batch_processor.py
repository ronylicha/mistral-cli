from mistral_cli.cli import Context
from .file_reader import FileAnalyzer
import os
import json
from pathlib import Path
from typing import List, Dict, Any
import fnmatch

def execute(context: Context) -> Context:
    """Traitement par lots de fichiers avec analyse Mistral."""
    
    # Récupérer les paramètres
    directory = context.data.get("directory", ".")
    patterns = context.data.get("patterns", ["*.py", "*.js", "*.ts", "*.java", "*.go"])
    analysis_type = context.data.get("analysis_type", "general")
    recursive = context.data.get("recursive", True)
    apply_improvements = context.data.get("apply_improvements", False)
    max_file_size = context.data.get("max_file_size", 100000)  # 100KB max par défaut
    
    api_key = context.data.get("api_key")
    if not api_key:
        context.data["output"] = "Erreur: Clé API Mistral manquante."
        return context
    
    if not os.path.exists(directory):
        context.data["output"] = f"Erreur: Répertoire '{directory}' inexistant."
        return context
    
    try:
        analyzer = FileAnalyzer(api_key)
        results = []
        processed_files = 0
        errors = []
        
        # Trouver tous les fichiers correspondants aux patterns
        files_to_process = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                # Ignorer les répertoires cachés et de build courants
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'build', 'dist', '__pycache__', 'target']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                        if os.path.getsize(file_path) <= max_file_size:
                            files_to_process.append(file_path)
                        else:
                            errors.append(f"Fichier ignoré (trop volumineux): {file_path}")
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path) and any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                    if os.path.getsize(file_path) <= max_file_size:
                        files_to_process.append(file_path)
                    else:
                        errors.append(f"Fichier ignoré (trop volumineux): {file_path}")
        
        # Traiter chaque fichier
        for file_path in files_to_process:
            try:
                print(f"Traitement de: {file_path}")
                
                # Lire le contenu
                content = analyzer.read_file_content(file_path)
                if content.startswith("Erreur"):
                    errors.append(f"{file_path}: {content}")
                    continue
                
                # Analyser
                analysis = analyzer.analyze_with_mistral(content, analysis_type)
                suggestions = analyzer.generate_improvements(content, analysis)
                
                # Appliquer les améliorations si demandé
                applied = False
                if apply_improvements:
                    applied = analyzer.apply_suggestions(file_path, content, suggestions)
                
                file_result = {
                    "file_path": file_path,
                    "file_size": len(content),
                    "analysis": analysis,
                    "suggestions": suggestions,
                    "improvements_applied": applied
                }
                
                results.append(file_result)
                processed_files += 1
                
            except Exception as e:
                errors.append(f"{file_path}: Erreur - {str(e)}")
        
        # Générer un rapport de synthèse
        summary = generate_batch_summary(results, analysis_type)
        
        # Préparer la sortie finale
        output = {
            "summary": summary,
            "total_files_found": len(files_to_process),
            "files_processed": processed_files,
            "files_with_errors": len(errors),
            "analysis_type": analysis_type,
            "directory": directory,
            "patterns": patterns,
            "errors": errors[:10],  # Limiter les erreurs affichées
            "detailed_results": results[:5] if len(results) <= 5 else results[:5] + [{"note": f"... et {len(results)-5} autres fichiers"}]
        }
        
        context.data["output"] = json.dumps(output, indent=2, ensure_ascii=False)
        
    except Exception as e:
        context.data["output"] = f"Erreur lors du traitement par lots: {str(e)}"
    
    return context

def generate_batch_summary(results: List[Dict[str, Any]], analysis_type: str) -> str:
    """Génère un résumé des résultats de l'analyse par lots."""
    
    if not results:
        return "Aucun fichier traité avec succès."
    
    total_files = len(results)
    files_with_improvements = sum(1 for r in results if r.get("improvements_applied", False))
    
    # Compter les types de problèmes les plus fréquents (analyse basique)
    common_issues = {}
    
    for result in results:
        analysis = result.get("analysis", "").lower()
        # Rechercher des mots-clés de problèmes courants
        if "security" in analysis or "sécurité" in analysis:
            common_issues["Sécurité"] = common_issues.get("Sécurité", 0) + 1
        if "performance" in analysis:
            common_issues["Performance"] = common_issues.get("Performance", 0) + 1
        if "bug" in analysis or "erreur" in analysis:
            common_issues["Bugs potentiels"] = common_issues.get("Bugs potentiels", 0) + 1
        if "documentation" in analysis:
            common_issues["Documentation"] = common_issues.get("Documentation", 0) + 1
        if "style" in analysis or "convention" in analysis:
            common_issues["Style/Conventions"] = common_issues.get("Style/Conventions", 0) + 1
    
    summary = f"""
=== RÉSUMÉ DE L'ANALYSE PAR LOTS ===

📊 Statistiques générales:
• Fichiers analysés: {total_files}
• Fichiers améliorés: {files_with_improvements}
• Type d'analyse: {analysis_type}

🔍 Problèmes les plus fréquents:"""
    
    if common_issues:
        for issue, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files) * 100
            summary += f"\n• {issue}: {count} fichiers ({percentage:.1f}%)"
    else:
        summary += "\n• Aucun problème majeur détecté"
    
    summary += f"""

💡 Recommandations:
• Examinez les fichiers avec des problèmes de sécurité en priorité
• Considérez l'amélioration de la documentation manquante
• Appliquez les suggestions de style pour une meilleure lisibilité
"""
    
    return summary