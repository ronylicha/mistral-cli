from mistral_cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Linter Java avec Checkstyle."""
    file_path = context.data.get("file_path", "")
    if not file_path or not os.path.exists(file_path):
        context.data["output"] = "Fichier Java introuvable."
        return context

    try:
        result = subprocess.run(
            ["java", "-jar", "checkstyle.jar", "-c", "/google_checks.xml", file_path],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport Checkstyle:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
