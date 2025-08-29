from mistral_cli import Context
import subprocess

def execute(context: Context) -> Context:
    """Bundle le code avec esbuild."""
    entry_file = context.data.get("entry_file", "")
    if not entry_file:
        context.data["output"] = "Fichier d'entrée requis."
        return context

    try:
        result = subprocess.run(
            ["esbuild", entry_file, "--bundle", "--outfile=dist/bundle.js"],
            capture_output=True,
            text=True
        )
        context.data["output"] = (
            f"Bundle généré avec esbuild:\n{result.stdout}\n"
            f"Erreurs: {result.stderr}"
        )
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
    return context
