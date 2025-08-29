from mistral_cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Exécute des tests avec Jest."""
    try:
        result = subprocess.run(
            ["jest"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Résultats des tests Jest:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
