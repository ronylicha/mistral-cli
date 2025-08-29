from mistral_cli import Context
import subprocess

def execute(context: Context) -> Context:
    """Linter React Native avec ESLint."""
    try:
        result = subprocess.run(
            ["npx", "eslint", "."],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Linting React Native:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
