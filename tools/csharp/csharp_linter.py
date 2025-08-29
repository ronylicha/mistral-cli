from mistral_cli import Context
import subprocess
import os

def execute(context: Context) -> Context:
    """Linter C# avec dotnet-format."""
    try:
        result = subprocess.run(
            ["dotnet", "format", "--verify-no-changes"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Rapport dotnet-format:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
