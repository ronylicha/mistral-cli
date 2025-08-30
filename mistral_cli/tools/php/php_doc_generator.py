from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Génère de la documentation avec phpDocumentor."""
    code_dir = context.data.get("code_dir", ".")
    if not os.path.exists(code_dir):
        context.data["output"] = "Répertoire introuvable."
        return context

    try:
        result = subprocess.run(
            ["phpdoc", "-d", code_dir, "-t", "docs"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Documentation générée dans docs/\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
