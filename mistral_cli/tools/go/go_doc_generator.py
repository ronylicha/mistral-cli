from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Génère de la documentation Go avec godoc."""
    try:
        result = subprocess.run(
            ["godoc", "-http=:6060"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Documentation disponible sur http://localhost:6060\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
