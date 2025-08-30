from mistral_cli.cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Exécute des tests unitaires avec PHPUnit."""
    test_file = context.data.get("test_file", "")
    if not test_file or not os.path.exists(test_file):
        context.data["output"] = "Fichier de test introuvable."
        return context

    try:
        result = subprocess.run(
            ["phpunit", test_file],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Résultats des tests PHPUnit:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
