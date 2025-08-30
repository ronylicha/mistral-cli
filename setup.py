from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import sys
import os
import pkg_resources

class PostInstallCommand(install):
    """Post-installation pour installer les dépendances Python et npm."""
    def run(self):
        # Installer les dépendances Python depuis requirements.txt
        requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
        if os.path.exists(requirements_file):
            with open(requirements_file) as f:
                requirements = f.read().splitlines()
                for req in requirements:
                    if req.strip() and not req.startswith('#'):
                        pkg_resources.require(req.strip())

        # Installer les dépendances npm globales
        npm_packages = [
            # Outils JavaScript/Node.js
            "eslint", "jest", "webpack", "typescript", "jsdoc",
            # Outils PHP
            "phpcs", "psalm", "phpunit",
            # Outils Go
            "golangci-lint",
            # Outils DevOps
            "hadolint", "kubeval", "tflint",
            # Outils Ruby
            "rubocop", "brakeman",
            # Outils divers
            "swiftlint", "ktlint"
        ]

        print("\n🔧 Installation des dépendances npm globales...")
        for package in npm_packages:
            try:
                print(f"   Installation de {package}...")
                subprocess.check_call(["npm", "install", "-g", package])
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ Échec de l'installation de {package}: {e}")
            except FileNotFoundError:
                print(f"   ⚠️ npm non trouvé. Installez Node.js pour utiliser {package}.")

        # Appeler la méthode d'installation par défaut
        install.run(self)

setup(
    name="mistral-cli",
    version="0.1.0",
    py_modules=["mistral_cli"],
    packages=find_packages(),
    install_requires=[
        "rich>=13.0.0",
        "pydantic>=1.10.0",
        "requests>=2.31.0",
        "cryptography>=41.0.0",
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
    entry_points={
        "console_scripts": [
            "mistral-cli = mistral_cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Rony Licha",
    author_email="ronylicha@gmail.com",
    description="Un outil CLI pour interagir avec Mistral AI et automatiser des tâches de développement.",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="mistral ai cli automation devops",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
    ],
    include_package_data=True,
)
