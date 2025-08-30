from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Génère de la documentation avec DocFX."""
    try:
        result = subprocess.run(
            ["docfx", "docfx.json"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Documentation générée dans _site\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
