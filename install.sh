#!/bin/bash

# mistral-cli/install.sh
# Version finale ultra-robuste avec vérification complète

set -e  # Quitter en cas d'erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
function message {
    echo -e "${YELLOW}[*]${NC} $1"
}

function success {
    echo -e "${GREEN}[✅]${NC} $1"
}

function error {
    echo -e "${RED}[❌]${NC} $1" >&2
}

function install_tool {
    local name=$1
    local install_cmd=$2
    local verify_cmd=$3
    local alt_message=$4

    message "Installation de $name..."
    if eval "$install_cmd"; then
        if eval "$verify_cmd"; then
            success "$name installé avec succès"
        else
            error "Installation de $name échouée (vérification)"
            echo -e "  ${alt_message}"
        fi
    else
        error "Installation de $name échouée"
        echo -e "  ${alt_message}"
    fi
}

# Vérifier que le script est exécuté depuis le bon répertoire
if [ ! -f "setup.py" ]; then
    error "Veuillez exécuter ce script depuis le répertoire racine du projet mistral-cli"
    exit 1
fi

# 1. Installer pipx
install_tool "pipx" "sudo apt update && sudo apt install -y pipx && pipx ensurepath" \
    "command -v pipx" "Installez manuellement avec: sudo apt install pipx"

# 2. Installer les dépendances système
message "Installation des dépendances système de base..."
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip nodejs npm composer curl wget

# 3. Créer un environnement virtuel temporaire pour le build
message "Création de l'environnement virtuel pour le build..."
python3.12 -m venv .venv-build
source .venv-build/bin/activate
pip install --upgrade pip build
python -m build
deactivate
rm -rf .venv-build

# 4. Installer mistral-cli avec pipx
install_tool "mistral-cli" "pipx install --python python3.12 ." \
    "command -v mistral-cli" "Vérifiez que le build a réussi et réessayez"

# Installation des outils avec méthodes alternatives

# Outils JavaScript
install_tool "ESLint" "npm install -g eslint" \
    "command -v eslint" "Installez avec: npm install -g eslint"

install_tool "Jest" "npm install -g jest" \
    "command -v jest" "Installez avec: npm install -g jest"

install_tool "Webpack" "npm install -g webpack webpack-cli" \
    "command -v webpack" "Installez avec: npm install -g webpack webpack-cli"

install_tool "TypeScript" "npm install -g typescript" \
    "command -v tsc" "Installez avec: npm install -g typescript"

install_tool "JSDoc" "npm install -g jsdoc" \
    "command -v jsdoc" "Installez avec: npm install -g jsdoc"

# Outils PHP
install_tool "PHP Code Sniffer" "sudo apt install -y php-codesniffer" \
    "command -v phpcs" "Installez avec: composer global require squizlabs/php_codesniffer"

install_tool "PSalm" "composer global require vimeo/psalm && echo 'export PATH=\"$PATH:$HOME/.composer/vendor/bin\"' >> ~/.bashrc" \
    "command -v psalm" "Installez avec: composer global require vimeo/psalm"

install_tool "PHPUnit" "composer global require phpunit/phpunit && echo 'export PATH=\"$PATH:$HOME/.composer/vendor/bin\"' >> ~/.bashrc" \
    "command -v phpunit" "Installez avec: composer global require phpunit/phpunit"

# Outils DevOps
install_tool "kubeval" "wget https://github.com/instrumenta/kubeval/releases/latest/download/kubeval-linux-amd64.tar.gz && tar xf kubeval-linux-amd64.tar.gz && sudo mv kubeval /usr/local/bin/ && rm kubeval-linux-amd64.tar.gz" \
    "command -v kubeval" "Téléchargez depuis: https://github.com/instrumenta/kubeval/releases"

install_tool "TFLint" "curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash" \
    "command -v tflint" "Installez avec: curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash"

install_tool "golangci-lint" "curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b /usr/local/bin v1.52.2" \
    "command -v golangci-lint" "Installez avec: curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh"

# Vérification finale
message "\n=== Vérification finale des outils installés ==="
echo -e "\n${GREEN}Outils JavaScript:${NC}"
for tool in eslint jest webpack tsc jsdoc; do
    if command -v $tool &> /dev/null; then
        echo -e "  ✅ $tool"
    else
        echo -e "  ❌ $tool"
    fi
done

echo -e "\n${GREEN}Outils PHP:${NC}"
for tool in phpcs psalm phpunit; do
    if command -v $tool &> /dev/null; then
        echo -e "  ✅ $tool"
    else
        echo -e "  ❌ $tool"
    fi
done

echo -e "\n${GREEN}Outils DevOps:${NC}"
for tool in kubeval tflint golangci-lint; do
    if command -v $tool &> /dev/null; then
        echo -e "  ✅ $tool"
    else
        echo -e "  ❌ $tool"
    fi
done

echo -e "\n${GREEN}Application:${NC}"
if command -v mistral-cli &> /dev/null; then
    echo -e "  ✅ mistral-cli"
    mistral-cli --version
else
    echo -e "  ❌ mistral-cli"
fi

echo -e "\n${GREEN}Installation terminée${NC}"
echo -e "\nPour utiliser les outils installés:"
echo -e "  - Les outils npm sont disponibles globalement"
echo -e "  - Les outils PHP sont dans ~/.composer/vendor/bin (ajoutez au PATH si nécessaire)"
echo -e "  - Les outils binaires sont dans /usr/local/bin"
echo -e "\nSi certains outils manquent, utilisez les commandes d'installation alternative affichées ci-dessus."
