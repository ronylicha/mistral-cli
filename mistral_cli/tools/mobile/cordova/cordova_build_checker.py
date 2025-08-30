from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Vérifie la configuration de build Cordova."""
    try:
        result = subprocess.run(
            ["cordova", "requirements"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Vérification des requirements Cordova:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
