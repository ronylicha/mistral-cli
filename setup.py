from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path
import subprocess
import sys
import os

# Lire le README
this_directory = Path(__file__).parent
long_description = ""
try:
    long_description = (this_directory / "README.md").read_text(encoding="utf-8")
except:
    pass

class PostInstallCommand(install):
    """Classe pour installer les outils npm après l'installation Python"""
    def run(self):
        # D'abord exécuter l'installation normale
        install.run(self)

        # Ensuite installer les outils npm
        self.install_npm_tools()

    def install_npm_tools(self):
        """Installe les outils npm nécessaires"""
        npm_packages = [
            # Outils JavaScript
            "eslint", "jest", "webpack", "typescript", "jsdoc",
            # Outils PHP
            "phpcs", "psalm", "phpunit",
            # Outils DevOps
            "hadolint", "kubeval", "tflint",
            # Outils Go
            "golangci-lint"
        ]

        print("\n🔧 Installation des outils npm globaux...")

        try:
            # Vérifier si npm est installé
            subprocess.run(["npm", "--version"],
                          check=True,
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)

            for package in npm_packages:
                print(f"   Installation de {package}...")
                try:
                    subprocess.run(["npm", "install", "-g", package],
                                  check=True,
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
                    print(f"   ✅ {package} installé")
                except subprocess.CalledProcessError as e:
                    print(f"   ⚠️ Échec de l'installation de {package}")

        except FileNotFoundError:
            print("   ⚠️ npm non trouvé. Les outils npm ne seront pas installés.")
            print("   Installez Node.js pour utiliser toutes les fonctionnalités.")
        except Exception as e:
            print(f"   ⚠️ Erreur lors de l'installation npm: {str(e)}")

setup(
    name="mistral-cli",
    version="0.1.0",
    description="Outil CLI pour interagir avec Mistral AI avec support npm intégré",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rony Licha",
    author_email="ronylicha@gmail.com",
    url="https://github.com/ronylicha/mistral-cli",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0.0",
        "pydantic>=1.10.0",
        "requests>=2.31.0",
        "cryptography>=41.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "mistral-cli = mistral_cli.__main__:main",
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
    },
    include_package_data=True,
    package_data={
        "mistral_cli": ["config/*.json", "tools/*/*"],
    },
)
