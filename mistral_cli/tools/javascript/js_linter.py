from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Linter JavaScript avec ESLint."""
    code = context.data.get("input", "")
    try:
        with open("temp.js", "w") as f:
            f.write(code)

        result = subprocess.run(
            ["eslint", "temp.js"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport ESLint:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    finally:
        if os.path.exists("temp.js"):
            os.remove("temp.js")
    return context
