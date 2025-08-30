from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Linter Swift avec SwiftLint."""
    try:
        result = subprocess.run(
            ["swiftlint"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport SwiftLint:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
