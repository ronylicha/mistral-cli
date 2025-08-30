from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Linter Dockerfile avec hadolint."""
    dockerfile_path = context.data.get("dockerfile_path", "Dockerfile")
    if not os.path.exists(dockerfile_path):
        context.data["output"] = "Dockerfile introuvable."
        return context

    try:
        result = subprocess.run(
            ["hadolint", dockerfile_path],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport Hadolint:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
