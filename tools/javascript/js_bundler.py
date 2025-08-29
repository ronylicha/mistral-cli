from mistral_cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Bundle le code avec Webpack."""
    entry_file = context.data.get("entry_file", "")
    if not entry_file or not os.path.exists(entry_file):
        context.data["output"] = "Fichier d'entrée introuvable."
        return context

    try:
        result = subprocess.run(
            ["webpack", entry_file, "-o", "dist/bundle.js"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Bundle généré dans dist/bundle.js\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
