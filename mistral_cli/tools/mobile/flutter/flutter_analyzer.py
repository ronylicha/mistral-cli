from mistral_cli.cli import Context
import subprocess

def execute(context: Context) -> Context:
    """Analyse Flutter avec `flutter analyze`."""
    try:
        result = subprocess.run(
            ["flutter", "analyze"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Analyse Flutter:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
