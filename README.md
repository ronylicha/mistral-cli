# Mistral CLI

`mistral-cli` est un outil en ligne de commande pour interagir avec l'API Mistral AI avec support intégré pour les outils de développement multi-langages.

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Fonctionnalités

- **Interface conversationnelle** avec les modèles et agents Mistral AI
- **Agents personnalisés** : création d'agents avec outils intégrés (web search, code interpreter, image generation)
- **Support multi-langages** : JavaScript, Python, PHP, Go, Rust, Java, Kotlin, Swift, C#
- **Outils intégrés** : linting, testing, documentation, sécurité
- **Gestion des sessions** : sauvegarde et reprise des conversations
- **Pipelines configurables** : automatisation des tâches de développement
- **Sécurité** : chiffrement des clés API avec cryptographie

## Installation

### Installation rapide avec le script fourni

```bash
chmod +x install.sh
./install.sh
```

### Installation manuelle

1. **Prérequis**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.12 python3.12-venv python3-pip nodejs npm
   
   # Installer pipx
   sudo apt install pipx
   pipx ensurepath
   ```

2. **Installation de mistral-cli**
   ```bash
   # Depuis le répertoire du projet
   pipx install .
   ```

3. **Outils de développement** (optionnel)
   ```bash
   # Outils JavaScript
   npm install -g eslint jest typescript webpack-cli jsdoc
   
   # Outils PHP
   composer global require squizlabs/php_codesniffer vimeo/psalm phpunit/phpunit
   
   # Autres outils selon vos besoins
   ```

## Utilisation

### Démarrer mistral-cli

```bash
mistral-cli
```

### Première utilisation

1. **Authentification** : Entrez votre clé API Mistral (disponible sur https://mistral.ai)
2. **Sélection d'agent** : Choisissez un agent Mistral pour commencer
3. **Conversation** : Tapez vos messages ou utilisez les commandes spéciales

### Commandes disponibles

- `/add_agent` - Ajouter des modèles/agents Mistral
- `/create_agent` - Créer un agent personnalisé avec outils
- `/select_agent` - Sélectionner un modèle/agent
- `/list_agents` - Lister tous les modèles et agents  
- `/set_pipeline` - Définir un pipeline par défaut
- `/servers` - Gérer les serveurs MCP
- `/sessions` - Changer de session
- `/help` - Afficher l'aide
- `/exit` - Quitter

### Exemple d'utilisation

```
Vous> Peux-tu analyser ce code JavaScript et suggérer des améliorations ?

Mistral> Je vais analyser votre code JavaScript. Pouvez-vous me montrer le code ?

Vous> /set_pipeline js-analysis

✅ Pipeline par défaut: js-analysis

Vous> [Votre code JavaScript ici]
```

## Configuration

### Structure des fichiers de configuration

```
config/
├── agents.json          # Agents Mistral configurés
├── servers.json         # Serveurs MCP
├── pipelines.json       # Pipelines de traitement  
├── secret.key          # Clé de chiffrement (générée automatiquement)
└── sessions/           # Sessions sauvegardées
    └── YYYYMMDD_HHMMSS.json
```

### Outils supportés par langage

- **JavaScript/TypeScript** : ESLint, Jest, Webpack, JSDoc
- **Python** : flake8, black, pytest, bandit
- **PHP** : PHP CodeSniffer, Psalm, PHPUnit
- **Go** : golangci-lint, go test, godoc
- **Rust** : clippy, cargo test, rustdoc
- **Java** : Checkstyle, SpotBugs, JUnit, Javadoc
- **DevOps** : kubeval, TFLint, hadolint

## Sécurité

- Les clés API sont chiffrées avec Fernet (cryptographie)
- Clé de chiffrement unique générée par installation
- Pas de stockage en clair des informations sensibles

## Développement

### Structure du projet

```
mistral_cli/
├── cli.py              # Interface principale
├── tools/              # Modules d'outils par langage
│   ├── javascript/
│   ├── python/
│   ├── php/
│   └── ...
└── config/             # Configuration
```

### Contribuer

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commiter vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Pousser sur la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

## Licence

MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur le repository GitHub.