from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Analyse de sécurité avec Psalm."""
    code = context.data.get("input", "")
    try:
        with open("temp.php", "w") as f:
            f.write(code)

        result = subprocess.run(
            ["psalm", "--init", "temp.php"],
            capture_output=True,
            text=True
        )

        context.data["output"] = (
            f"Rapport de sécurité Psalm:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    finally:
        if os.path.exists("temp.php"):
            os.remove("temp.php")
    return context
