from mistral_cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Linter Go avec golangci-lint."""
    try:
        result = subprocess.run(
            ["golangci-lint", "run"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport golangci-lint:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
