from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Analyse de sécurité avec SpotBugs."""
    try:
        result = subprocess.run(
            ["mvn", "spotbugs:check"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport SpotBugs:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
