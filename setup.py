from setuptools import setup, find_packages
import subprocess
import sys
import os
from pathlib import Path

# Lire les dépendances depuis requirements.txt
def read_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Classe pour installer les dépendances npm après l'installation Python
class PostInstallCommand:
    def __init__(self):
        self.installed = False

    def __call__(self):
        if not self.installed:
            self.installed = True
            self.install_npm_packages()

    def install_npm_packages(self):
        print("\n🔧 Installation des dépendances npm globales...")
        npm_packages = [
            "eslint", "jest", "webpack", "typescript", "jsdoc",
            "phpcs", "psalm", "phpunit",
            "golangci-lint", "hadolint", "kubeval", "tflint"
        ]

        try:
            # Vérifier si npm est installé
            subprocess.run(["npm", "--version"], check=True, capture_output=True)

            for package in npm_packages:
                print(f"   Installation de {package}...")
                try:
                    subprocess.run(
                        ["npm", "install", "-g", package],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                except subprocess.CalledProcessError as e:
                    print(f"   ⚠️ Échec de l'installation de {package}: {e.stderr.decode().strip()}")
        except FileNotFoundError:
            print("   ⚠️ npm non trouvé. Installez Node.js pour utiliser les outils npm.")
        except Exception as e:
            print(f"   ⚠️ Erreur lors de l'installation npm: {str(e)}")

# Lire le contenu du README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="mistral-cli",
    version="0.1.0",
    description="Outil CLI pour interagir avec Mistral AI et automatiser des tâches de développement",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rony Licha",
    author_email="ronylich@gmail.com",
    url="https://github.com/ronylicha/mistral-cli",
    packages=find_packages(),
    py_modules=["mistral_cli"],
    install_requires=read_requirements(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "mistral-cli = mistral_cli:main",
        ],
    },
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    cmdclass={
        'install': PostInstallCommand(),
    },
    include_package_data=True,
    package_data={
        "mistral_cli": ["config/*.json", "tools/*/*"],
    },
)
