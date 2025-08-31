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
- `/analyze_file` - Analyser un fichier avec Mistral AI
- `/analyze_batch` - Analyser plusieurs fichiers par lots
- `/execute_command` - Exécuter un ordre sur un dossier entier
- `/set_pipeline` - Définir un pipeline par défaut
- `/servers` - Gérer les serveurs MCP
- `/sessions` - Changer de session
- `/help` - Afficher l'aide
- `/exit` - Quitter

### Analyse de fichiers avec Mistral AI

La nouvelle fonctionnalité d'analyse de fichiers permet d'utiliser l'API Mistral pour analyser et améliorer automatiquement votre code.

#### Analyse d'un fichier unique

```bash
# Dans l'interface Mistral CLI
/analyze_file

# Entrez le chemin du fichier
Chemin du fichier à analyser: ./example.py

# Choisissez le type d'analyse
Type d'analyse (general/security/optimization/documentation/refactor/bugs/style): security

# Appliquer les améliorations automatiquement ?
Appliquer automatiquement les améliorations suggérées ? (y/n): n
```

#### Analyse par lots

```bash
# Analyser plusieurs fichiers d'un répertoire
/analyze_batch

# Configuration
Répertoire à analyser: ./src
Patterns: *.py,*.js,*.ts
Type d'analyse: optimization
Analyse récursive des sous-répertoires ? (y/n): y
Appliquer automatiquement les améliorations ? (y/n): n
```

#### Exécution d'ordres en langage naturel sur dossier complet

```bash
# Exécuter un ordre en français naturel sur un dossier entier
/execute_command

# Exemples d'ordres en langage naturel:
💡 Exemples d'ordres en langage naturel:
  1. « Ajoute des commentaires détaillés partout dans le code »
  2. « Rends ce code plus sûr en ajoutant des validations »
  3. « Améliore les performances de tous ces fichiers »
  4. « Modernise le code avec les dernières pratiques »
  5. « Ajoute une gestion d'erreurs robuste »
  6. « Traduis tous les commentaires en français »
  7. « Génère des tests unitaires pour chaque fonction »
  8. « Applique les principes du Clean Code »

📝 Entrez votre ordre en français (soyez précis):
🗨️ Votre ordre> Ajoute une documentation complète avec des exemples

# Configuration
Dossier à traiter: ./src
Patterns: *.py,*.js,*.java
Appliquer automatiquement les modifications ? (y/n): y
```

#### Types d'analyse disponibles

- **general** : Analyse générale avec suggestions d'amélioration
- **security** : Détection de vulnérabilités et failles de sécurité
- **optimization** : Suggestions d'optimisation de performance
- **documentation** : Amélioration de la documentation et commentaires
- **refactor** : Suggestions de refactorisation du code
- **bugs** : Détection de bugs potentiels et erreurs de logique
- **style** : Vérification des conventions de style et bonnes pratiques

#### Ordres en langage naturel

Le système interprète vos demandes en français et les applique intelligemment :

**📚 Documentation :**
- « Ajoute des commentaires détaillés partout dans le code »
- « Génère une documentation complète pour toutes les fonctions »
- « Écris des docstrings explicatives pour chaque méthode »

**🔒 Sécurité :**
- « Rends ce code plus sûr en ajoutant des validations »
- « Corrige toutes les vulnérabilités de sécurité »
- « Protège le code contre les attaques courantes »

**⚡ Performance :**
- « Améliore les performances de tous ces fichiers »
- « Optimise l'utilisation mémoire »
- « Rends les algorithmes plus efficaces »

**🧹 Clean Code :**
- « Applique les principes du Clean Code »
- « Refactorise pour une meilleure maintenabilité »
- « Élimine le code dupliqué »

**🆕 Modernisation :**
- « Modernise le code avec les dernières pratiques »
- « Convertis le code en utilisant les dernières fonctionnalités »
- « Remplace le code déprécié par les alternatives modernes »

**🌍 Personnalisé :**
- « Traduis tous les commentaires en français »
- « Convertis les fonctions en classes »
- « Remplace print() par logging »

### Exemple d'utilisation

```
Vous> Peux-tu analyser ce code JavaScript et suggérer des améliorations ?

Mistral> Je vais analyser votre code JavaScript. Pouvez-vous me montrer le code ?

Vous> /analyze_file

📄 Fichier analysé: ./app.js
🔍 Type d'analyse: security

📋 ANALYSE:
[Rapport détaillé de l'analyse...]

💡 SUGGESTIONS:
[Suggestions d'amélioration...]
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