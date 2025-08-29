from mistral_cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Génère de la documentation avec YARD."""
    try:
        result = subprocess.run(
            ["yard", "doc"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Documentation YARD générée dans doc/\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
