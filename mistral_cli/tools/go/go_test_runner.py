from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Exécute des tests Go."""
    try:
        result = subprocess.run(
            ["go", "test", "./..."],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Résultats des tests Go:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
