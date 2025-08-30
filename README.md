# Mistral CLI

**Outil polyvalent en ligne de commande pour interagir avec les agents Mistral AI**

![Mistral CLI Demo](https://via.placeholder.com/800x400/0078D4/FFFFFF?text=Mistral+CLI)

---

## Table des matières

1. [Fonctionnalités](#fonctionnalités)
2. [Prérequis](#prérequis)
3. [Installation](#installation)
4. [Authentification](#authentification)
5. [Architecture](#architecture)
6. [Utilisation](#utilisation)
7. [Outils disponibles](#outils-disponibles)
8. [Exemples de pipelines](#exemples-de-pipelines)
9. [Personnalisation](#personnalisation)
10. [Contribuer](#contribuer)

## Fonctionnalités

### Intégration Mistral AI

- Sélection parmi différents modèles (Tiny, Small, Medium, Large)
- Gestion sécurisée des clés API avec chiffrement AES-256
- Interface conversationnelle optimisée
- Sessions persistantes avec historique complet

### Automatisation

- Pipelines personnalisables avec chaînage d'opérations
- Support de 15+ langages (PHP, JS, Python, Java, etc.)
- Exécution parallèle optimisée
- Intégration transparente avec outils locaux/distants

### Sécurité

- Chiffrement des données sensibles
- Gestion fine des permissions
- Journalisation complète
- Validation des entrées/sorties

## Prérequis

### Obligatoires

- Python 3.8+
- pipx
- Node.js 16+
- Git

### Installation des dépendances de base

```bash
# Sur Debian/Ubuntu
sudo apt update
sudo apt install -y python3-pip python3-venv git nodejs npm
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

### Optionnels


| Langage | Prérequis        |
| --------- | ------------------- |
| PHP     | PHP 8+            |
| Java    | JDK 11+           |
| Go      | Go 1.18+          |
| Ruby    | Ruby 3+           |
| C#      | .NET SDK 6+       |
| Rust    | Rust 1.60+        |
| Swift   | Xcode (macOS)     |
| Docker  | Docker Engine 20+ |

## Installation

### Méthode recommandée avec pipx

1. Cloner le dépôt:

```bash
git clone https://github.com/votre-org/mistral-cli.git
cd mistral-cli
```

2. Installer avec pipx:

```
pipx install .
```

3. Vérifier l'installation:

```
mistral-cli --version
```

> Cette commande installe:
> * Les dépendances Python depuis requirements.txt
> * Les outils npm globaux nécessaires
> * Crée la commande globale mistral-cli
> * Configure l'environnement sécurisé


## Authentification

### Première utilisation
À la première exécution, Mistral CLI vous guidera:
```
🔐 Authentification requise
Entrez votre clé API Mistral: ************
✅ 3 agents Mistral disponibles:

Mistral-Tiny (mistral-tiny)
Mistral-Small (mistral-small)
Mistral-Medium (mistral-medium)
Sélectionnez un agent [1-3]: 2
✅ Agent Mistral-Small sélectionné
```


### Commandes de sécurité
```bash
# Lister les agents
mistral-cli agents list

# Révoquer un agent
mistral-cli agents revoke mistral-tiny

# Mettre à jour la clé
mistral-cli auth update
```

## Architecture

### Agents Mistral
| Agent          | Modèle          | Tokens Max | Cas d'usage          |
|----------------|-----------------|------------|-----------------------|
| Mistral-Tiny   | mistral-tiny    | 8K         | Tâches simples        |
| Mistral-Small  | mistral-small   | 32K        | Développement standard|
| Mistral-Medium | mistral-medium  | 128K       | Tâches complexes      |

### Structure d'un pipeline
```json
{
  "name": "exemple_pipeline",
  "steps": [
    {
      "name": "ESLint",
      "type": "npx",
      "tool": "eslint",
      "params": {
        "config": ".eslintrc.json"
      }
    }
  ]
}
```

## 🛠 Outils Disponibles

### PHP
| Outil                     | Description                          |
|---------------------------|--------------------------------------|
| `php_linter`              | Linting avec PHP_CodeSniffer (PSR-12) |
| `php_security_scanner`    | Analyse de sécurité avec Psalm       |
| `php_unit_test`           | Tests unitaires avec PHPUnit         |
| `php_doc_generator`       | Génération de docs avec phpDocumentor|

### JavaScript/Node.js
| Outil               | Description               |
|---------------------|---------------------------|
| `js_linter`         | Linting avec ESLint       |
| `js_bundler`        | Bundling avec Webpack     |
| `js_test_runner`    | Tests avec Jest           |
| `js_doc_generator`  | Génération de docs avec JSDoc |
| `node_audit`        | Audit des dépendances npm |
| `node_bundler`      | Bundling avec esbuild     |

### Python
| Outil               | Description               |
|---------------------|---------------------------|
| `py_linter`         | Linting avec flake8       |
| `py_test_runner`    | Tests avec pytest         |
| `py_doc_generator`  | Génération de docs avec Sphinx |
| `py_security_scanner`| Analyse avec Bandit      |

### Java
| Outil               | Description               |
|---------------------|---------------------------|
| `java_linter`       | Linting avec Checkstyle   |
| `java_test_runner`  | Tests avec JUnit          |
| `java_doc_generator`| Génération de docs avec Javadoc |
| `java_security_scanner` | Analyse avec SpotBugs  |

### Ruby
| Outil               | Description               |
|---------------------|---------------------------|
| `ruby_linter`       | Linting avec RuboCop      |
| `ruby_test_runner`  | Tests avec RSpec          |
| `ruby_doc_generator`| Génération de docs avec YARD |
| `ruby_security_scanner` | Analyse avec Brakeman  |

### Go
| Outil               | Description               |
|---------------------|---------------------------|
| `go_linter`         | Linting avec golangci-lint|
| `go_test_runner`    | Tests Go                  |
| `go_doc_generator`  | Génération de docs avec godoc |
| `go_security_scanner` | Analyse avec gosec     |

### C#
| Outil               | Description               |
|---------------------|---------------------------|
| `csharp_linter`     | Linting avec dotnet-format|
| `csharp_test_runner`| Tests avec dotnet test    |
| `csharp_doc_generator` | Génération de docs avec DocFX |

### Rust
| Outil               | Description               |
|---------------------|---------------------------|
| `rust_linter`       | Linting avec Clippy       |
| `rust_test_runner`  | Tests Rust                |
| `rust_doc_generator`| Génération de docs        |

### Swift
| Outil               | Description               |
|---------------------|---------------------------|
| `swift_linter`      | Linting avec SwiftLint    |
| `swift_test_runner` | Tests Swift               |

### Kotlin
| Outil               | Description               |
|---------------------|---------------------------|
| `kotlin_linter`     | Linting avec ktlint       |
| `kotlin_test_runner`| Tests avec Gradle         |

### Mobile
| Outil                     | Description                          |
|---------------------------|--------------------------------------|
| `react_native_linter`     | Linting React Native avec ESLint     |
| `react_native_test_runner`| Tests avec Jest                      |
| `flutter_analyzer`        | Analyse Flutter                      |
| `flutter_test_runner`     | Tests Flutter                        |
| `cordova_linter`          | Linting Cordova                      |
| `cordova_build_checker`   | Vérification des requirements Cordova |

### DevOps
| Outil                     | Description                          |
|---------------------------|--------------------------------------|
| `docker_linter`           | Linting des Dockerfiles avec hadolint|
| `kubernetes_validator`    | Validation des fichiers Kubernetes   |
| `terraform_validator`     | Validation des fichiers Terraform    |

## Exemples de Pipelines

Pipeline CI JavaScript complet:
```
    {
      "name": "javascript_ci_pipeline",
      "description": "Pipeline CI complet pour projets JavaScript/TypeScript",
      "steps": [
        {
          "name": "ESLint",
          "type": "npx",
          "tool": "eslint",
          "params": {
            "config": ".eslintrc.json",
            "ext": ".js,.jsx,.ts,.tsx",
            "fix": true
          },
          "on_failure": "warn"
        },
        {
          "name": "TypeScript Compilation",
          "type": "npx",
          "tool": "tsc",
          "params": {
            "project": "tsconfig.json",
            "noEmit": false
          },
          "depends_on": ["ESLint"]
        }
      ]
    }
```
## Personnalisation

### Créer un outil personnalisé

1. Créer le fichier dans tools/[langage]/mon_outil.py:
```python

    from mistral_cli import Context
    from rich.console import Console

    console = Console()

    def execute(context: Context) -> Context:
        """
        Mon outil personnalisé pour Mistral CLI
        """
        input_data = context.data.get("input", "")
        console.print("Exécution de mon_outil")

        result = f"Résultat traité: {input_data[:50]}..."
        context.data["output"] = result
        return context
```
2. Déclarer l'outil dans un pipeline:
```json
    {
      "name": "mon_pipeline_personnalise",
      "steps": [
        {
          "name": "Mon outil personnalisé",
          "type": "python",
          "tool": "mon_outil",
          "params": {
            "param1": "valeur1"
          }
        }
      ]
    }
```
### Bonnes pratiques:

1. Testez vos outils:
   mistral-cli test mon_outil --input "données de test"

2. Documentez vos outils avec des commentaires clairs

3. Validez les entrées:
```
    if not input_data:
        context.data["output"] = "Erreur: aucune donnée d'entrée"
        return context
```
4. Gérez les erreurs:
```
    try:
        # Votre code
    except Exception as e:
        context.data["output"] = f"Erreur: {str(e)}"
```

## Contribuer

1. Fork le dépôt
2. Créez une branche: `git checkout -b ma-fonctionnalite`
3. Commitez: `git commit -am 'Ajout ma-fonctionnalite'`
4. Poussez: `git push origin ma-fonctionnalite`
5. Ouvrez une Pull Request

## Licence

MIT - Voir [LICENSE](LICENSE) pour plus de détails.

---
© 2025 Rony Licha. Tous droits réservés.
