from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Linter Rust avec clippy."""
    try:
        result = subprocess.run(
            ["cargo", "clippy"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport Clippy:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
