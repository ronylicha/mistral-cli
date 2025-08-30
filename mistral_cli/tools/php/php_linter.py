from mistral_cli.cli import Context
from rich.console import Console
import subprocess

console = Console()

def execute(context: Context) -> Context:
    """Linter PHP avec PHP_CodeSniffer."""
    code = context.data.get("input", "")
    try:
        # Sauvegarder le code dans un fichier temporaire
        with open("temp.php", "w") as f:
            f.write(code)

        # Exécuter PHP_CodeSniffer
        result = subprocess.run(
            ["phpcs", "--standard=PSR12", "temp.php"],
            capture_output=True,
            text=True
        )

        context.data["output"] = (
            f"Rapport de linting PHP (PSR-12):\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    finally:
        if os.path.exists("temp.php"):
            os.remove("temp.php")
    return context
