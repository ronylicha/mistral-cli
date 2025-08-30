from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Génère de la documentation avec Javadoc."""
    try:
        result = subprocess.run(
            ["mvn", "javadoc:javadoc"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Documentation Javadoc générée dans target/site/apidocs\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
