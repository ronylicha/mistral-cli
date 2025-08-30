from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Analyse de sécurité avec bandit."""
    code = context.data.get("input", "")
    try:
        with open("temp.py", "w") as f:
            f.write(code)

        result = subprocess.run(
            ["bandit", "temp.py"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport Bandit:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    finally:
        if os.path.exists("temp.py"):
            os.remove("temp.py")
    return context
