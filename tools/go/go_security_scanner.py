from mistral_cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Analyse de sécurité avec gosec."""
    try:
        result = subprocess.run(
            ["gosec", "./..."],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport gosec:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
