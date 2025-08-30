from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Exécute des tests Swift."""
    try:
        result = subprocess.run(
            ["swift", "test"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Résultats des tests:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
