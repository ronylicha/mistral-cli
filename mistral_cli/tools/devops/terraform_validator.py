from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Valide les fichiers Terraform avec tflint."""
    try:
        result = subprocess.run(
            ["tflint"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport TFLint:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
