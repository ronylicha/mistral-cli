from mistral_cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Analyse de sécurité avec Brakeman."""
    try:
        result = subprocess.run(
            ["brakeman"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport Brakeman:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
