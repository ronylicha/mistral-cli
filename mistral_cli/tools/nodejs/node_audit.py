from mistral_cli.cli import Context
import subprocess

def execute(context: Context) -> Context:
    """Audit des dépendances avec npm audit."""
    try:
        result = subprocess.run(
            ["npm", "audit", "--json"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Audit npm:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
