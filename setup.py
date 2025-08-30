from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
this_directory = Path(__file__).parent
long_description = ""
try:
    long_description = (this_directory / "README.md").read_text(encoding="utf-8")
except:
    pass

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
    include_package_data=True,
    package_data={
        "mistral_cli": ["config/*.json", "tools/*/*"],
    },
)
