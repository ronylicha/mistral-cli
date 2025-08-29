from mistral_cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Linter Python avec flake8."""
    code = context.data.get("input", "")
    try:
        with open("temp.py", "w") as f:
            f.write(code)

        result = subprocess.run(
            ["flake8", "temp.py"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport flake8:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    finally:
        if os.path.exists("temp.py"):
            os.remove("temp.py")
    return context
