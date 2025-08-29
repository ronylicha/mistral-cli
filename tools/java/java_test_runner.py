from mistral_cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Exécute des tests JUnit."""
    try:
        result = subprocess.run(
            ["mvn", "test"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Résultats des tests JUnit:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
