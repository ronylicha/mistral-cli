from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Linter Kotlin avec ktlint."""
    file_path = context.data.get("file_path", "")
    if not file_path or not os.path.exists(file_path):
        context.data["output"] = "Fichier Kotlin introuvable."
        return context

    try:
        result = subprocess.run(
            ["ktlint", file_path],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport ktlint:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
