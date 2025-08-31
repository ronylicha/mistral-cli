import json
import os
import subprocess
import fnmatch
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.markdown import Markdown
from pydantic import BaseModel, field_validator
import requests
from cryptography.fernet import Fernet
import base64
import hashlib
import getpass
import readline
import sys

# --- Configuration de la sécurité ---
SECRET_KEY_FILE = "config/secret.key"
AGENTS_FILE = "config/agents.json"
console = Console()

# --- Génération et gestion de la clé de chiffrement ---
def generate_or_load_key() -> bytes:
    """Génère ou charge une clé de chiffrement."""
    os.makedirs("config", exist_ok=True)
    if not os.path.exists(SECRET_KEY_FILE):
        key = Fernet.generate_key()
        with open(SECRET_KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(SECRET_KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

def encrypt_data(data: str, key: bytes) -> str:
    """Chiffre les données sensibles."""
    cipher = Fernet(key)
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """Déchiffre les données."""
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_data.encode()).decode()

# --- Modèles de données ---
class Context(BaseModel):
    data: Dict[str, Any] = {}
    allowed_dirs: List[str] = []
    unsafe_mode: bool = False
    session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_pipeline: Optional[str] = None
    current_agent: Optional[str] = None

class MistralAgent(BaseModel):
    id: str
    name: str
    model: str
    agent_type: str = "model"  # "model" ou "agent"
    description: Optional[str] = None
    instructions: Optional[str] = None
    tools: List[str] = []
    active: bool = True
    encrypted_api_key: Optional[str] = None  # Clé API chiffrée
    created_at: Optional[str] = None
    version: Optional[str] = None

    @field_validator('created_at', mode='before')
    @classmethod
    def validate_created_at(cls, v):
        """Convertit les timestamps Unix en chaînes."""
        if v is None:
            return None
        if isinstance(v, int):
            # Convertir le timestamp Unix en string ISO
            return datetime.fromtimestamp(v).isoformat()
        if isinstance(v, (str, float)):
            # Si c'est déjà une chaîne ou un float, le convertir en string
            if isinstance(v, float):
                return datetime.fromtimestamp(v).isoformat()
            return str(v)
        return v

    @property
    def api_key(self) -> Optional[str]:
        """Déchiffre la clé API à la volée."""
        if not self.encrypted_api_key:
            return None
        key = generate_or_load_key()
        return decrypt_data(self.encrypted_api_key, key)

    @api_key.setter
    def api_key(self, value: str):
        """Chiffre la clé API avant stockage."""
        if value:
            key = generate_or_load_key()
            self.encrypted_api_key = encrypt_data(value, key)

class MCPServer(BaseModel):
    name: str
    type: str  # 'api' ou 'npx'
    url: Optional[str] = None
    package: Optional[str] = None
    encrypted_api_key: Optional[str] = None
    active: bool = True
    install_args: str = "--global"

    @property
    def api_key(self) -> Optional[str]:
        if not self.encrypted_api_key:
            return None
        key = generate_or_load_key()
        return decrypt_data(self.encrypted_api_key, key)

    @api_key.setter
    def api_key(self, value: str):
        if value:
            key = generate_or_load_key()
            self.encrypted_api_key = encrypt_data(value, key)

class PipelineStep(BaseModel):
    step_type: str  # 'api', 'npx', 'python'
    server: str
    action: str
    params: Dict[str, Any]

class Pipeline(BaseModel):
    name: str
    steps: List[PipelineStep]

class ChatSession(BaseModel):
    session_id: str
    context: Context
    history: List[Dict[str, Any]] = []

class NPXCache(BaseModel):
    package: str
    installed: bool = False
    version: Optional[str] = None

# --- Gestion des outils npm ---
def install_npm_tools():
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

    try:
        # Vérifier si npm est installé
        subprocess.run(["npm", "--version"], check=True, capture_output=True, text=True)

        console.print("\n🔧 Installation des outils npm globaux...")

        for package in npm_packages:
            console.print(f"   Installation de {package}...")
            try:
                subprocess.run(
                    ["npm", "install", "-g", package],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                console.print(f"   ✅ {package} installé")
            except subprocess.CalledProcessError as e:
                console.print(f"   ⚠️ Échec de l'installation de {package}")

    except FileNotFoundError:
        console.print("   ⚠️ npm non trouvé. Installez Node.js pour utiliser les outils npm.")
        console.print("   Sur Ubuntu/Debian: sudo apt install nodejs npm")
    except Exception as e:
        console.print(f"   ⚠️ Erreur lors de l'installation npm: {str(e)}")

# --- Gestion des fichiers ---
def load_config(file_path: str, model) -> List:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            agents = []
            for item in data:
                try:
                    agents.append(model(**item))
                except Exception as e:
                    console.print(f"[dim red]Erreur lors du chargement de {item.get('id', 'inconnu')}: {e}[/dim red]")
                    continue
            return agents
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        console.print(f"[dim red]Erreur de format JSON dans {file_path}[/dim red]")
        return []

def save_config(file_path: str, data: List):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([item.dict() for item in data], f, indent=2, ensure_ascii=False)

# --- Classe principale ---
class MistralChatBot:
    def __init__(self):
        self.current_session = None
        self.servers = load_config("config/servers.json", MCPServer)
        self.pipelines = load_config("config/pipelines.json", Pipeline)
        self.npx_cache = load_config("config/npx_cache.json", NPXCache)
        self.agents = load_config(AGENTS_FILE, MistralAgent)
        self._initialize_session()

    def _initialize_session(self):
        """Initialise une session ou charge une existante."""
        if not self.agents:
            self._authenticate()
        self.load_session()

    def _authenticate(self):
        """Interface d'authentification pour ajouter une clé API Mistral."""
        auth_text = Text()
        auth_text.append("🔐 Authentification requise\n\n", style="bold yellow")
        auth_text.append("Pour utiliser Mistral CLI, vous devez ajouter une clé API Mistral.\n\n", style="white")
        auth_text.append("🔗 Obtenez votre clé sur: ", style="dim")
        auth_text.append("https://mistral.ai", style="link https://mistral.ai")
        auth_text.append("\n\n📝 Une fois connecté, je récupérerai automatiquement vos modèles et agents.", style="dim cyan")
        
        console.print(Panel.fit(
            auth_text,
            title="[bold yellow]🎆 Configuration initiale[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        ))
        api_key = getpass.getpass("Entrez votre clé API Mistral: ").strip()
        if not api_key:
            console.print("[red]❌ Clé API requise.[/red]")
            exit(1)

        agents_data = self._fetch_mistral_agents(api_key)
        if not agents_data:
            error_text = Text()
            error_text.append("❌ Impossible de récupérer les données\n\n", style="bold red")
            error_text.append("🔍 Vérifiez votre clé API Mistral\n", style="red")
            error_text.append("🌐 Assurez-vous d'avoir une connexion Internet\n", style="red")
            error_text.append("💳 Vérifiez que votre compte a des crédits", style="red")
            
            console.print(Panel.fit(
                error_text,
                title="[bold red]⚠️ Erreur d'authentification[/bold red]",
                border_style="red",
                padding=(1, 2)
            ))
            exit(1)

        self._save_agents(agents_data, api_key)
        # Affichage des agents ajoutés avec style
        models_count = len([a for a in agents_data if a.get("agent_type") == "model"])
        agents_count = len([a for a in agents_data if a.get("agent_type") == "agent"])
        
        success_text = Text()
        success_text.append("✅ ", style="green")
        success_text.append(f"{len(agents_data)} éléments ajoutés: ", style="bold green")
        if models_count > 0:
            success_text.append(f"{models_count} modèles 📚", style="cyan")
        if agents_count > 0:
            if models_count > 0:
                success_text.append(", ", style="white")
            success_text.append(f"{agents_count} agents 🤖", style="magenta")
        
        console.print(Panel.fit(success_text, border_style="green"))

        # Sélectionner automatiquement le premier modèle par défaut
        self._auto_select_first_model()

        # Installer les outils npm après l'authentification
        if Confirm.ask("Souhaitez-vous installer les outils npm nécessaires ?", default=True):
            install_npm_tools()

    def _fetch_mistral_agents(self, api_key: str) -> List[Dict[str, Any]]:
        """Récupère les modèles et agents depuis l'API Mistral."""
        agents_list = []
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            # Récupérer les modèles disponibles
            response = requests.get(
                "https://api.mistral.ai/v1/models",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            try:
                models_response = response.json()
            except ValueError as json_err:
                console.print(f"[red]❌ Erreur de parsing JSON pour les modèles:[/red] {json_err}")
                models_response = []
            
            # Gérer les différents formats de réponse API
            if isinstance(models_response, dict):
                models = models_response.get("data", [])
            elif isinstance(models_response, list):
                models = models_response
            else:
                models = []
            
            for model in models:
                # Vérifier que le modèle a les clés requises
                if not isinstance(model, dict) or "id" not in model:
                    console.print(f"[dim red]Modèle ignoré (format invalide): {model}[/dim red]")
                    continue
                    
                agents_list.append({
                    "id": f"model-{model['id']}",
                    "name": model["id"].replace("-", " ").title(),
                    "model": model["id"],
                    "agent_type": "model",
                    "description": f"Modèle {model['id']}",
                    "tools": [],
                    "created_at": model.get("created"),
                })
                
        except requests.RequestException as e:
            console.print(f"[red]❌ Erreur lors de la récupération des modèles:[/red] {e}")
            if hasattr(e, 'response') and e.response:
                try:
                    console.print(f"[dim red]Réponse API: {e.response.text}[/dim red]")
                except:
                    pass
        
        try:
            # Récupérer les agents personnalisés (API Beta)
            response = requests.get(
                "https://api.mistral.ai/v1/agents",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            agents_response = response.json()
            
            # Gérer les différents formats de réponse API pour les agents
            if isinstance(agents_response, dict):
                agents = agents_response.get("data", [])
            elif isinstance(agents_response, list):
                agents = agents_response
            else:
                agents = []
            
            for agent in agents:
                # Vérifier que l'agent a les clés requises
                if not isinstance(agent, dict) or "id" not in agent:
                    console.print(f"[dim yellow]Agent ignoré (format invalide): {agent}[/dim yellow]")
                    continue
                    
                tools_list = [tool.get("type", "") for tool in agent.get("tools", [])]
                agents_list.append({
                    "id": agent["id"],
                    "name": agent.get("name", f"Agent {agent['id'][:8]}"),
                    "model": agent.get("model", ""),
                    "agent_type": "agent",
                    "description": agent.get("description", ""),
                    "instructions": agent.get("instructions", ""),
                    "tools": tools_list,
                    "created_at": agent.get("created_at"),
                    "version": agent.get("version")
                })
                
        except requests.RequestException as e:
            console.print(f"[yellow]⚠️ Agents API non disponible (Beta):[/yellow] {e}")
            if hasattr(e, 'response') and e.response:
                try:
                    console.print(f"[dim yellow]Réponse API: {e.response.text}[/dim yellow]")
                except:
                    pass
            
        return agents_list

    def _save_agents(self, agents_data: List[Dict[str, Any]], api_key: str):
        """Sauvegarde les agents avec leur clé API chiffrée."""
        new_agents = []
        for agent_data in agents_data:
            try:
                agent = MistralAgent(
                    id=agent_data["id"],
                    name=agent_data["name"],
                    model=agent_data["model"],
                    agent_type=agent_data.get("agent_type", "model"),
                    description=agent_data.get("description"),
                    instructions=agent_data.get("instructions"),
                    tools=agent_data.get("tools", []),
                    created_at=agent_data.get("created_at"),
                    version=agent_data.get("version")
                )
                agent.api_key = api_key  # La propriété setter chiffre automatiquement
                new_agents.append(agent)
            except Exception as e:
                console.print(f"[dim red]Erreur lors de la création de l'agent {agent_data.get('id', 'inconnu')}: {e}[/dim red]")
                console.print(f"[dim red]Données: {agent_data}[/dim red]")
                continue

        existing_agents = load_config(AGENTS_FILE, MistralAgent)
        updated_agents = existing_agents + [
            a for a in new_agents if a.id not in {e.id for e in existing_agents}
        ]

        save_config(AGENTS_FILE, updated_agents)
        self.agents = updated_agents

    def _auto_select_first_model(self):
        """Sélectionne automatiquement le premier modèle disponible."""
        if not self.agents:
            return
            
        # Chercher le premier modèle dans la liste
        models = [a for a in self.agents if a.agent_type == "model"]
        if models:
            first_model = models[0]
            self.current_session.context.current_agent = first_model.id
            
            console.print(f"\n🎯 [bold cyan]Modèle par défaut sélectionné:[/bold cyan] [cyan]{first_model.name}[/cyan]")
            console.print(f"   [dim]Vous pouvez changer avec [cyan]/select_agent[/cyan][/dim]")

    def create_custom_agent(self):
        """Crée un agent personnalisé via l'API Mistral."""
        if not self.agents:
            console.print("⚠️ Vous devez d'abord ajouter une clé API avec /add_agent")
            return
            
        # Prendre la clé API du premier agent disponible
        api_key = next((a.api_key for a in self.agents if a.api_key), None)
        if not api_key:
            console.print("⚠️ Aucune clé API disponible")
            return

        console.print("\n🤖 [bold]Création d'un agent personnalisé[/bold]")
        
        # Récupérer les modèles disponibles pour la sélection
        available_models = [a.model for a in self.agents if a.agent_type == "model"]
        if not available_models:
            console.print("⚠️ Aucun modèle disponible")
            return

        name = Prompt.ask("Nom de l'agent")
        if not name:
            return

        description = Prompt.ask("Description de l'agent", default="")
        instructions = Prompt.ask("Instructions système (optionnel)", default="")
        
        # Sélection du modèle de base
        model = Prompt.ask("Modèle de base", choices=available_models, default=available_models[0])
        
        # Sélection des outils
        available_tools = ["web_search", "code_interpreter", "image_generation"]
        console.print(f"Outils disponibles: {', '.join(available_tools)}")
        tools_input = Prompt.ask("Outils à activer (séparés par des virgules)", default="")
        tools = [t.strip() for t in tools_input.split(",") if t.strip() in available_tools]

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            agent_data = {
                "model": model,
                "name": name,
                "description": description,
                "instructions": instructions if instructions else None,
                "tools": [{"type": tool} for tool in tools]
            }
            
            # Retirer les clés None
            agent_data = {k: v for k, v in agent_data.items() if v is not None}

            with Live(Spinner("dots", text="Création de l'agent..."), console=console):
                response = requests.post(
                    "https://api.mistral.ai/v1/agents",
                    headers=headers,
                    json=agent_data,
                    timeout=30
                )
                response.raise_for_status()

            result = response.json()
            
            # Ajouter le nouvel agent à la liste
            new_agent = MistralAgent(
                id=result["id"],
                name=result.get("name", name),
                model=result.get("model", model),
                agent_type="agent",
                description=result.get("description", description),
                instructions=result.get("instructions", instructions),
                tools=[tool.get("type", "") for tool in result.get("tools", [])],
                created_at=result.get("created_at"),
                version=result.get("version")
            )
            new_agent.api_key = api_key
            
            self.agents.append(new_agent)
            save_config(AGENTS_FILE, self.agents)
            
            # Affichage de succès avec style
            success_text = Text()
            success_text.append("✅ Agent ", style="bold green")
            success_text.append(f"'{name}'", style="bold magenta")
            success_text.append(" créé avec succès!\n\n", style="bold green")
            success_text.append(f"🏷️ ID: ", style="dim")
            success_text.append(f"{result['id']}\n", style="cyan")
            if tools:
                success_text.append(f"🔧 Outils: ", style="dim")
                success_text.append(f"{', '.join(tools)}", style="yellow")
            
            console.print(Panel.fit(
                success_text,
                title="[bold green]🎉 Nouvel Agent Créé[/bold green]",
                border_style="green",
                padding=(1, 2)
            ))

        except requests.RequestException as e:
            error_text = Text()
            error_text.append("❌ Erreur lors de la création de l'agent\n\n", style="bold red")
            error_text.append(f"🔴 {str(e)}\n", style="red")
            
            if hasattr(e, 'response') and e.response:
                try:
                    error_detail = e.response.json()
                    error_text.append(f"\n📝 Détails: {error_detail}", style="dim red")
                except:
                    error_text.append(f"\n📝 Réponse: {e.response.text}", style="dim red")
            
            console.print(Panel.fit(
                error_text,
                title="[bold red]⚠️ Erreur API[/bold red]",
                border_style="red",
                padding=(1, 2)
            ))

    # --- Gestion des agents Mistral ---
    def list_agents(self):
        """Liste les agents Mistral disponibles."""
        if not self.agents:
            console.print("Aucun agent Mistral configuré.")
            return

        console.print("\n🤖 [bold]Agents Mistral disponibles:[/bold]")
        
        # Séparer les modèles et les agents
        models = [a for a in self.agents if a.agent_type == "model"]
        agents = [a for a in self.agents if a.agent_type == "agent"]
        
        # Liste numérotée pour la cohérence avec select_agent
        current_number = 1
        
        if models:
            console.print("\n[bold cyan]📚 Modèles disponibles:[/bold cyan]")
            for model in models:
                status = "✅" if model.id == self.current_session.context.current_agent else " "
                console.print(f" {status} {current_number:2d}. [cyan]{model.name}[/cyan] [dim]({model.model})[/dim]")
                current_number += 1
        
        if agents:
            console.print("\n[bold magenta]🤖 Agents personnalisés:[/bold magenta]")
            for agent in agents:
                status = "✅" if agent.id == self.current_session.context.current_agent else " "
                tools_str = f" [dim yellow]🔧 {', '.join(agent.tools)}[/dim yellow]" if agent.tools else ""
                console.print(f" {status} {current_number:2d}. [magenta]{agent.name}[/magenta]{tools_str}")
                if agent.description:
                    console.print(f"     [dim italic]💭 {agent.description}[/dim italic]")
                current_number += 1
        
        # Statistiques finales et conseil
        total_count = len(models) + len(agents)
        console.print(f"\n[dim]📊 Total: {total_count} éléments ({len(models)} modèles, {len(agents)} agents)[/dim]")
        
        if total_count > 0:
            console.print(f"[dim]💡 Utilisez [cyan]/select_agent[/cyan] puis tapez un numéro pour sélectionner rapidement[/dim]")

    def select_agent(self):
        """Sélectionne un agent Mistral pour la session avec numérotation."""
        if not self.agents:
            console.print("⚠️ Aucun agent Mistral configuré.")
            return

        # Séparer les modèles et les agents
        models = [a for a in self.agents if a.agent_type == "model"]
        agents = [a for a in self.agents if a.agent_type == "agent"]
        
        # Créer une liste numérotée
        console.print("\n[bold cyan]🎯 Sélection d'agent/modèle[/bold cyan]")
        
        numbered_agents = []
        current_number = 1
        
        if models:
            console.print(f"\n[bold cyan]📚 Modèles disponibles:[/bold cyan]")
            for model in models:
                status = "✅" if model.id == self.current_session.context.current_agent else " "
                console.print(f" {status} {current_number:2d}. [cyan]{model.name}[/cyan] [dim]({model.model})[/dim]")
                numbered_agents.append(model)
                current_number += 1
        
        if agents:
            console.print(f"\n[bold magenta]🤖 Agents personnalisés:[/bold magenta]")
            for agent in agents:
                status = "✅" if agent.id == self.current_session.context.current_agent else " "
                tools_str = f" [dim yellow]🔧 {', '.join(agent.tools[:2])}{'...' if len(agent.tools) > 2 else ''}[/dim yellow]" if agent.tools else ""
                console.print(f" {status} {current_number:2d}. [magenta]{agent.name}[/magenta]{tools_str}")
                if agent.description:
                    console.print(f"     [dim italic]💭 {agent.description}[/dim italic]")
                numbered_agents.append(agent)
                current_number += 1
        
        console.print(f"\n  0. [red]❌ Annuler[/red]")
        
        # Demander le choix par numéro
        try:
            choice = Prompt.ask(
                f"\n[bold]Entrez le numéro de votre choix (0-{len(numbered_agents)})[/bold]",
                choices=[str(i) for i in range(len(numbered_agents) + 1)]
            )
            
            choice_num = int(choice)
            
            if choice_num == 0:
                console.print("[dim]Sélection annulée.[/dim]")
                return
            
            # Sélectionner l'agent correspondant
            selected_agent = numbered_agents[choice_num - 1]
            self.current_session.context.current_agent = selected_agent.id
            
            # Affichage de confirmation de sélection
            if selected_agent.agent_type == "model":
                selection_text = Text()
                selection_text.append("📚 Modèle sélectionné: ", style="bold cyan")
                selection_text.append(f"{selected_agent.name}", style="bold white")
                console.print(Panel.fit(selection_text, border_style="cyan"))
            else:
                selection_text = Text()
                selection_text.append("🤖 Agent sélectionné: ", style="bold magenta")
                selection_text.append(f"{selected_agent.name}\n", style="bold white")
                
                if selected_agent.description:
                    selection_text.append(f"\n💭 {selected_agent.description}\n", style="italic")
                
                if selected_agent.tools:
                    selection_text.append(f"\n🔧 Outils actifs: ", style="bold yellow")
                    selection_text.append(f"{', '.join(selected_agent.tools)}", style="yellow")
                
                console.print(Panel.fit(
                    selection_text,
                    title="[bold magenta]✨ Agent Actif[/bold magenta]",
                    border_style="magenta",
                    padding=(1, 2)
                ))
                
        except (ValueError, IndexError):
            console.print("[red]❌ Choix invalide.[/red]")

    # --- Gestion des serveurs MCP ---
    def display_servers(self):
        console.print("\n🌐 [bold]Gestion des serveurs MCP[/bold]")
        for server in self.servers:
            status = "✅ [green]Actif[/green]" if server.active else "❌ [red]Inactif[/red]"
            server_type = "API" if server.type == "api" else "Outils npx"
            console.print(f"- {server.name} ({server_type}): {server.url or server.package} {status}")

    def add_server(self):
        server_type = Prompt.ask("Type de serveur", choices=["api", "npx"])
        name = Prompt.ask("Nom du serveur")

        if server_type == "api":
            url = Prompt.ask("URL du serveur")
            api_key = Prompt.ask("Clé API (optionnel)", password=True) or None
            server = MCPServer(type="api", name=name, url=url)
            if api_key:
                server.api_key = api_key  # Chiffrement automatique
            self.servers.append(server)
        else:  # npx
            package = Prompt.ask("Package npx (ex: @mistralai/tool-x)")
            install_args = Prompt.ask("Arguments d'installation", default="--global")
            self.servers.append(MCPServer(type="npx", name=name, package=package, install_args=install_args))

        save_config("config/servers.json", self.servers)
        console.print(f"✅ Serveur [bold]{name}[/bold] ajouté.")

    def manage_servers(self):
        while True:
            self.display_servers()
            action = Prompt.ask(
                "Action",
                choices=["Ajouter", "Modifier", "Basculer", "Supprimer", "Retour"]
            )

            if action == "Ajouter":
                self.add_server()
            elif action == "Modifier":
                self.edit_server()
            elif action == "Basculer":
                self.toggle_server()
            elif action == "Supprimer":
                self.remove_server()
            elif action == "Retour":
                break

    def edit_server(self):
        """Modifier un serveur existant"""
        if not self.servers:
            console.print("Aucun serveur configuré.")
            return

        choices = [server.name for server in self.servers] + ["Annuler"]
        server_name = Prompt.ask("Sélectionnez un serveur à modifier", choices=choices)

        if server_name == "Annuler":
            return

        server = next(s for s in self.servers if s.name == server_name)

        if server.type == "api":
            server.url = Prompt.ask("Nouvelle URL", default=server.url)
            if Prompt.ask("Mettre à jour la clé API?", choices=["Oui", "Non"], default="Non") == "Oui":
                api_key = Prompt.ask("Nouvelle clé API", password=True)
                server.api_key = api_key
        else:  # npx
            server.package = Prompt.ask("Nouveau package", default=server.package)
            server.install_args = Prompt.ask("Nouveaux arguments d'installation", default=server.install_args)

        save_config("config/servers.json", self.servers)
        console.print(f"✅ Serveur {server.name} mis à jour.")

    def toggle_server(self):
        """Active/désactive un serveur"""
        if not self.servers:
            console.print("Aucun serveur configuré.")
            return

        choices = [server.name for server in self.servers] + ["Annuler"]
        server_name = Prompt.ask("Sélectionnez un serveur", choices=choices)

        if server_name == "Annuler":
            return

        server = next(s for s in self.servers if s.name == server_name)
        server.active = not server.active
        save_config("config/servers.json", self.servers)
        status = "activé" if server.active else "désactivé"
        console.print(f"✅ Serveur {server.name} {status}.")

    def remove_server(self):
        """Supprime un serveur"""
        if not self.servers:
            console.print("Aucun serveur configuré.")
            return

        choices = [server.name for server in self.servers] + ["Annuler"]
        server_name = Prompt.ask("Sélectionnez un serveur à supprimer", choices=choices)

        if server_name == "Annuler":
            return

        if Confirm.ask(f"Êtes-vous sûr de vouloir supprimer {server_name} ?"):
            self.servers = [s for s in self.servers if s.name != server_name]
            save_config("config/servers.json", self.servers)
            console.print(f"✅ Serveur {server_name} supprimé.")

    # --- Gestion des pipelines ---
    def display_pipelines(self):
        console.print("\n🔧 [bold]Gestion des pipelines[/bold]")
        for pipeline in self.pipelines:
            console.print(f"- [bold]{pipeline.name}[/bold] ({len(pipeline.steps)} étapes)")

    def set_default_pipeline(self):
        if not self.pipelines:
            console.print("⚠️ Aucun pipeline disponible.")
            return

        choices = [p.name for p in self.pipelines]
        choice = Prompt.ask("Pipeline par défaut", choices=choices)
        self.current_session.context.default_pipeline = choice
        console.print(f"✅ Pipeline par défaut: [bold]{choice}[/bold]")

    def execute_pipeline(self, pipeline_name: str, user_input: str):
        pipeline = next(p for p in self.pipelines if p.name == pipeline_name)
        console.print(f"\n🚀 Exécution du pipeline [bold]{pipeline.name}[/bold]:")

        reasoning = []
        current_data = user_input

        for step in pipeline.steps:
            server = next((s for s in self.servers if s.name == step.server and s.active), None)
            if not server:
                reasoning.append(f"❌ Serveur {step.server} non disponible.")
                continue

            reasoning.append(f"🔹 Étape [bold]{step.step_type}[/bold]: {step.server} ({step.action})")

            if step.step_type == "api":
                reasoning.append(f"   Appel API à {server.url}...")
                current_data = f"Réponse simulée pour '{current_data[:30]}...'"

            elif step.step_type == "npx":
                if not server.package:
                    reasoning.append(f"   ❌ Package npx non configuré pour {step.server}.")
                    continue

                if not self.install_npx_package(server.package, server.install_args):
                    continue

                output = self.run_npx_command(server.package, step.action, step.params)
                if output:
                    current_data = output

            elif step.step_type == "python":
                try:
                    module_path = f"tools.{step.server.replace('/', '.')}"
                    module = __import__(module_path, fromlist=[''])
                    self.current_session.context.data["input"] = current_data
                    self.current_session.context = module.execute(self.current_session.context)
                    current_data = self.current_session.context.data.get("output", current_data)
                except Exception as e:
                    reasoning.append(f"   ❌ Erreur avec {step.server}: {e}")

        self.current_session.history.append({
            "input": user_input,
            "output": current_data,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        })

        console.print(Panel.fit("\n".join(reasoning)), style="blue", title="Raisonnement")
        console.print(f"\n[bold]Sortie>[/bold] {current_data}")

    # --- Gestion des outils npx ---
    def install_npx_package(self, package: str, install_args: str = "--global") -> bool:
        cached = next((c for c in self.npx_cache if c.package == package), None)
        if cached and cached.installed:
            console.print(f"✅ {package} est déjà installé.")
            return True

        if Confirm.ask(f"Installer {package} ?"):
            try:
                console.print(f"🔧 Installation de {package}...")
                subprocess.run(f"npm install {install_args} {package}", shell=True, check=True)
                if cached:
                    cached.installed = True
                else:
                    self.npx_cache.append(NPXCache(package=package, installed=True))
                save_config("config/npx_cache.json", self.npx_cache)
                console.print(f"✅ {package} installé.")
                return True
            except subprocess.CalledProcessError as e:
                console.print(f"❌ Échec de l'installation: {e}")
                return False
        return False

    def run_npx_command(self, package: str, action: str, params: Dict[str, Any]) -> str:
        cmd = ["npx", package, action]
        for key, value in params.items():
            cmd.extend([f"--{key}", str(value)])
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Erreur avec {package}: {e.stderr}")
            return ""

    # --- Gestion des sessions ---
    def load_session(self):
        """Charge une session existante ou en crée une nouvelle avec interface numérotée."""
        try:
            os.makedirs("config/sessions", exist_ok=True)
            sessions = []
            session_files = [f for f in os.listdir("config/sessions") if f.endswith(".json")]
            
            for file in session_files:
                try:
                    with open(f"config/sessions/{file}", "r", encoding="utf-8") as f:
                        sessions.extend([ChatSession(**s) for s in json.load(f)])
                except Exception as e:
                    console.print(f"[dim red]Erreur lors du chargement de {file}: {e}[/dim red]")
                    continue

            if not sessions:
                self.current_session = ChatSession(
                    session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                    context=Context(allowed_dirs=[os.getcwd()])
                )
                console.print("✨ [bold cyan]Nouvelle session créée[/bold cyan]")
                # Sélectionner automatiquement le premier modèle
                self._auto_select_first_model()
                return

            # Trier les sessions par date (plus récente en premier)
            sessions.sort(key=lambda s: s.session_id, reverse=True)

            # Interface de sélection avec numérotation
            console.print("\n[bold cyan]💾 Sélection de session[/bold cyan]")
            console.print("\n[bold cyan]📝 Sessions disponibles:[/bold cyan]")
            
            for i, session in enumerate(sessions, 1):
                # Formatter la date pour l'affichage
                try:
                    session_date = datetime.strptime(session.session_id, "%Y%m%d_%H%M%S")
                    formatted_date = session_date.strftime("%d/%m/%Y à %H:%M")
                except:
                    formatted_date = session.session_id
                
                # Informations sur la session
                agent_info = ""
                if session.context.current_agent:
                    try:
                        agent = next(a for a in self.agents if a.id == session.context.current_agent)
                        agent_icon = "📚" if agent.agent_type == "model" else "🤖"
                        agent_info = f" [dim yellow]{agent_icon} {agent.name}[/dim yellow]"
                    except:
                        agent_info = " [dim red]Agent non trouvé[/dim red]"
                
                pipeline_info = ""
                if session.context.default_pipeline:
                    pipeline_info = f" [dim green]🔧 {session.context.default_pipeline}[/dim green]"
                
                # Nombre de messages dans l'historique
                msg_count = len(session.history)
                history_info = f" [dim]({msg_count} messages)[/dim]" if msg_count > 0 else " [dim](nouvelle)[/dim]"
                
                console.print(f"  {i:2d}. [cyan]{formatted_date}[/cyan]{agent_info}{pipeline_info}{history_info}")
            
            console.print(f"\n   0. [green]✨ Nouvelle session[/green]")
            
            # Demander le choix
            try:
                choice = Prompt.ask(
                    f"\n[bold]Entrez le numéro de votre choix (0-{len(sessions)})[/bold]",
                    choices=[str(i) for i in range(len(sessions) + 1)]
                )
                
                choice_num = int(choice)
                
                if choice_num == 0:
                    # Nouvelle session
                    self.current_session = ChatSession(
                        session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                        context=Context(allowed_dirs=[os.getcwd()])
                    )
                    console.print("✨ [bold cyan]Nouvelle session créée[/bold cyan]")
                    # Sélectionner automatiquement le premier modèle
                    self._auto_select_first_model()
                else:
                    # Charger session existante
                    self.current_session = sessions[choice_num - 1]
                    
                    # Afficher les informations de la session chargée
                    session_date = datetime.strptime(self.current_session.session_id, "%Y%m%d_%H%M%S")
                    formatted_date = session_date.strftime("%d/%m/%Y à %H:%M")
                    
                    console.print(f"📂 [bold cyan]Session chargée:[/bold cyan] {formatted_date}")
                    
                    if self.current_session.context.current_agent:
                        try:
                            agent = next(a for a in self.agents if a.id == self.current_session.context.current_agent)
                            agent_icon = "📚" if agent.agent_type == "model" else "🤖"
                            console.print(f"   {agent_icon} Agent actif: [bold]{agent.name}[/bold]")
                        except:
                            console.print(f"   [dim red]⚠️ Agent précédent non trouvé, sélection du premier modèle...[/dim red]")
                            self._auto_select_first_model()
                    else:
                        # Aucun agent sélectionné dans cette session, sélectionner le premier modèle
                        self._auto_select_first_model()
                    
                    if self.current_session.context.default_pipeline:
                        console.print(f"   🔧 Pipeline: [bold]{self.current_session.context.default_pipeline}[/bold]")
                    
                    msg_count = len(self.current_session.history)
                    if msg_count > 0:
                        console.print(f"   💬 Historique: [dim]{msg_count} messages[/dim]")
                        
            except (ValueError, IndexError):
                console.print("[red]❌ Choix invalide, nouvelle session créée.[/red]")
                self.current_session = ChatSession(
                    session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                    context=Context(allowed_dirs=[os.getcwd()])
                )
                self._auto_select_first_model()
                
        except Exception as e:
            console.print(f"[red]❌ Erreur lors du chargement des sessions: {e}[/red]")
            self.current_session = ChatSession(
                session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                context=Context(allowed_dirs=[os.getcwd()])
            )
            self._auto_select_first_model()

    def save_session(self):
        """Sauvegarde la session courante."""
        save_config(f"config/sessions/{self.current_session.session_id}.json", [self.current_session])

    # --- Interface principale ---
    def show_help(self):
        help_text = Text()
        help_text.append("Commandes disponibles:\n\n", style="bold cyan")
        
        # Commandes principales
        commands = [
            ("/add_agent", "Ajouter des agents/modèles Mistral", "🔗"),
            ("/create_agent", "Créer un agent personnalisé", "🎨"),
            ("/select_agent", "Sélectionner un agent/modèle", "🎯"),
            ("/list_agents", "Lister tous les agents/modèles", "📊"),
            ("/analyze_file", "Analyser un fichier avec Mistral AI", "🔍"),
            ("/analyze_batch", "Analyser plusieurs fichiers par lots", "📁"),
            ("/execute_command", "Exécuter un ordre sur un dossier entier", "⚡"),
            ("/set_pipeline", "Définir un pipeline par défaut", "🔧"),
            ("/servers", "Gérer les serveurs MCP", "🌐"),
            ("/pipelines", "Gérer les pipelines", "⚙️"),
            ("/sessions", "Changer de session", "📝"),
            ("/install-npm", "Installer les outils npm", "📦"),
            ("/help", "Affiche cette aide", "❓"),
            ("/exit", "Quitter", "🚑")
        ]
        
        for cmd, desc, icon in commands:
            help_text.append(f"{icon} ", style="")
            help_text.append(f"{cmd:<15}", style="bold green")
            help_text.append(f" - {desc}\n", style="white")
        
        help_text.append("\n", style="")
        help_text.append("📚 Modèles", style="bold cyan")
        help_text.append(" : Chat direct avec les modèles Mistral\n", style="")
        help_text.append("🤖 Agents", style="bold magenta")
        help_text.append(" : Agents avec outils intégrés (web search, code, etc.)\n\n", style="")
        help_text.append("🗨️ Sans commande, votre message est envoyé à l'agent/modèle sélectionné.", style="italic dim")
        
        console.print(Panel(
            help_text,
            title="[bold blue]📚 Guide d'utilisation[/bold blue]",
            border_style="blue",
            padding=(0, 1)
        ))

    def call_mistral_agent(self, prompt: str) -> str:
        """Appelle l'API Mistral avec l'agent/modèle sélectionné."""
        if not self.current_session.context.current_agent:
            console.print("⚠️ Aucun agent sélectionné. Utilisez `/select_agent`.")
            return ""

        agent = next(a for a in self.agents if a.id == self.current_session.context.current_agent)
        if not agent.api_key:
            console.print("⚠️ Clé API manquante pour cet agent.")
            return ""

        try:
            headers = {
                "Authorization": f"Bearer {agent.api_key}",
                "Content-Type": "application/json"
            }
            
            if agent.agent_type == "agent":
                # Utiliser l'API Conversations pour les agents personnalisés
                return self._call_agent_conversation(agent, prompt, headers)
            else:
                # Utiliser l'API Chat Completions pour les modèles
                return self._call_model_completion(agent, prompt, headers)

        except requests.RequestException as e:
            console.print(f"❌ Erreur API Mistral: {e}")
            return f"Erreur: {str(e)}"
    
    def _call_model_completion(self, agent: MistralAgent, prompt: str, headers: dict) -> str:
        """Appelle l'API Chat Completions pour un modèle."""
        data = {
            "model": agent.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        with Live(Spinner("dots", text="Interrogation du modèle Mistral..."), console=console):
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()

        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "Réponse vide.")
    
    def _call_agent_conversation(self, agent: MistralAgent, prompt: str, headers: dict) -> str:
        """Appelle l'API Conversations pour un agent personnalisé."""
        # Créer une nouvelle conversation avec l'agent
        conversation_data = {
            "agent_id": agent.id,
            "inputs": [{"role": "user", "content": prompt}]
        }

        with Live(Spinner("dots", text=f"Interrogation de l'agent {agent.name}..."), console=console):
            response = requests.post(
                "https://api.mistral.ai/v1/agents/completions",
                headers=headers,
                json=conversation_data,
                timeout=30
            )
            response.raise_for_status()

        result = response.json()
        # Extraire la réponse de l'agent
        choices = result.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "Réponse vide.")
        
        # Fallback pour d'autres formats de réponse
        return result.get("output", "Réponse vide.")

    def _display_session_status(self):
        """Affiche le statut de la session actuelle."""
        status_parts = []
        
        if self.current_session.context.current_agent:
            agent = next(a for a in self.agents if a.id == self.current_session.context.current_agent)
            if agent.agent_type == "model":
                status_parts.append(f"📚 [cyan]{agent.name}[/cyan]")
            else:
                status_parts.append(f"🤖 [green]{agent.name}[/green]")
                if agent.tools:
                    status_parts.append(f"🔧 [dim]{', '.join(agent.tools[:2])}[/dim]")
        else:
            status_parts.append("⚠️ [red]Aucun agent sélectionné[/red]")
        
        if self.current_session.context.default_pipeline:
            status_parts.append(f"🔧 [yellow]{self.current_session.context.default_pipeline}[/yellow]")
        
        status_text = " | ".join(status_parts)
        console.print(f"\n[dim]Statut: {status_text}[/dim]")
        console.print("[dim]Tapez [cyan]/help[/cyan] pour voir les commandes disponibles[/dim]\n")

    def analyze_file(self):
        """Analyse un fichier unique avec Mistral AI."""
        if not self.agents:
            console.print("⚠️ Vous devez d'abord ajouter une clé API avec /add_agent")
            return
        
        # Prendre la clé API du premier agent disponible
        api_key = next((a.api_key for a in self.agents if a.api_key), None)
        if not api_key:
            console.print("⚠️ Aucune clé API disponible")
            return
        
        console.print("\n🔍 [bold]Analyse de fichier avec Mistral AI[/bold]")
        
        # Demander le chemin du fichier
        file_path = Prompt.ask("Chemin du fichier à analyser")
        if not file_path or not os.path.exists(file_path):
            console.print("❌ Fichier inexistant ou chemin invalide.")
            return
        
        # Type d'analyse
        analysis_types = ["general", "security", "optimization", "documentation", "refactor", "bugs", "style"]
        analysis_type = Prompt.ask(
            "Type d'analyse", 
            choices=analysis_types, 
            default="general"
        )
        
        # Demander si on applique les améliorations
        apply_improvements = Confirm.ask("Appliquer automatiquement les améliorations suggérées ?", default=False)
        
        try:
            from mistral_cli.tools.file_analyzer.file_reader import FileAnalyzer
            
            with Live(Spinner("dots", text="Analyse en cours..."), console=console):
                analyzer = FileAnalyzer(api_key)
                
                # Lire le fichier
                content = analyzer.read_file_content(file_path)
                if content.startswith("Erreur"):
                    console.print(f"❌ {content}")
                    return
                
                # Analyser
                analysis = analyzer.analyze_with_mistral(content, analysis_type)
                suggestions = analyzer.generate_improvements(content, analysis)
                
                # Appliquer les améliorations si demandé
                applied = False
                if apply_improvements:
                    applied = analyzer.apply_suggestions(file_path, content, suggestions)
            
            # Afficher les résultats
            console.print(f"\n📄 [bold cyan]Fichier analysé:[/bold cyan] {file_path}")
            console.print(f"🔍 [bold]Type d'analyse:[/bold] {analysis_type}")
            
            console.print("\n[bold green]📋 ANALYSE:[/bold green]")
            console.print(Panel(Markdown(analysis), border_style="green"))
            
            console.print("\n[bold yellow]💡 SUGGESTIONS:[/bold yellow]")
            console.print(Panel(Markdown(suggestions), border_style="yellow"))
            
            if apply_improvements:
                if applied:
                    console.print("\n✅ [bold green]Améliorations appliquées avec succès ![/bold green]")
                    console.print(f"📁 Backup créé: {file_path}.backup")
                else:
                    console.print("\n❌ [bold red]Échec de l'application des améliorations.[/bold red]")
            
        except ImportError:
            console.print("❌ Module d'analyse de fichier non trouvé.")
        except Exception as e:
            console.print(f"❌ Erreur lors de l'analyse: {str(e)}")

    def analyze_batch(self):
        """Analyse par lots de fichiers avec Mistral AI."""
        if not self.agents:
            console.print("⚠️ Vous devez d'abord ajouter une clé API avec /add_agent")
            return
        
        # Prendre la clé API du premier agent disponible
        api_key = next((a.api_key for a in self.agents if a.api_key), None)
        if not api_key:
            console.print("⚠️ Aucune clé API disponible")
            return
        
        console.print("\n📁 [bold]Analyse par lots avec Mistral AI[/bold]")
        
        # Demander le répertoire
        directory = Prompt.ask("Répertoire à analyser", default=".")
        if not os.path.exists(directory):
            console.print("❌ Répertoire inexistant.")
            return
        
        # Patterns de fichiers
        console.print("Patterns de fichiers (séparés par des virgules):")
        console.print("Exemples: *.py,*.js,*.ts,*.java,*.go,*.php,*.rb,*.rs")
        patterns_input = Prompt.ask("Patterns", default="*.py,*.js,*.ts")
        patterns = [p.strip() for p in patterns_input.split(",")]
        
        # Type d'analyse
        analysis_types = ["general", "security", "optimization", "documentation", "refactor", "bugs", "style"]
        analysis_type = Prompt.ask(
            "Type d'analyse", 
            choices=analysis_types, 
            default="general"
        )
        
        # Options avancées
        recursive = Confirm.ask("Analyse récursive des sous-répertoires ?", default=True)
        apply_improvements = Confirm.ask("Appliquer automatiquement les améliorations ?", default=False)
        max_file_size = int(Prompt.ask("Taille max par fichier (bytes)", default="100000"))
        
        try:
            from mistral_cli.tools.file_analyzer.batch_processor import execute
            
            # Préparer le contexte
            context = Context()
            context.data = {
                "directory": directory,
                "patterns": patterns,
                "analysis_type": analysis_type,
                "recursive": recursive,
                "apply_improvements": apply_improvements,
                "max_file_size": max_file_size,
                "api_key": api_key
            }
            
            with Live(Spinner("dots", text="Analyse par lots en cours..."), console=console):
                result_context = execute(context)
            
            # Afficher les résultats
            output_data = json.loads(result_context.data["output"])
            
            console.print(f"\n📊 [bold cyan]RÉSULTATS DE L'ANALYSE PAR LOTS[/bold cyan]")
            console.print(f"📁 Répertoire: {directory}")
            console.print(f"🔍 Type: {analysis_type}")
            console.print(f"📄 Fichiers trouvés: {output_data['total_files_found']}")
            console.print(f"✅ Fichiers traités: {output_data['files_processed']}")
            console.print(f"❌ Erreurs: {output_data['files_with_errors']}")
            
            if output_data.get('summary'):
                console.print("\n[bold green]📋 RÉSUMÉ:[/bold green]")
                console.print(Panel(output_data['summary'], border_style="green"))
            
            if output_data.get('errors'):
                console.print("\n[bold red]⚠️ ERREURS:[/bold red]")
                for error in output_data['errors'][:5]:
                    console.print(f"• {error}")
            
            # Sauvegarder le rapport détaillé
            report_file = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            console.print(f"\n💾 [bold blue]Rapport détaillé sauvegardé:[/bold blue] {report_file}")
            
        except ImportError:
            console.print("❌ Module d'analyse par lots non trouvé.")
        except Exception as e:
            console.print(f"❌ Erreur lors de l'analyse par lots: {str(e)}")

    def execute_command_on_folder(self):
        """Exécute un ordre en langage naturel sur un dossier entier et ses sous-dossiers."""
        if not self.agents:
            console.print("⚠️ Vous devez d'abord ajouter une clé API avec /add_agent")
            return
        
        # Prendre la clé API du premier agent disponible
        api_key = next((a.api_key for a in self.agents if a.api_key), None)
        if not api_key:
            console.print("⚠️ Aucune clé API disponible")
            return
        
        console.print("\n🗣️ [bold]Exécution d'ordre en langage naturel sur dossier[/bold]")
        
        # Afficher des exemples d'ordres
        console.print("\n[bold cyan]💡 Exemples d'ordres en langage naturel:[/bold cyan]")
        examples = [
            "Ajoute des commentaires détaillés partout dans le code",
            "Rends ce code plus sûr en ajoutant des validations",
            "Améliore les performances de tous ces fichiers", 
            "Modernise le code avec les dernières pratiques",
            "Ajoute une gestion d'erreurs robuste",
            "Traduis tous les commentaires en français",
            "Génère des tests unitaires pour chaque fonction",
            "Optimise l'utilisation mémoire",
            "Applique les principes du Clean Code",
            "Convertis le code en utilisant les dernières fonctionnalités du langage"
        ]
        
        for i, example in enumerate(examples, 1):
            console.print(f"  {i:2d}. [dim italic]« {example} »[/dim italic]")
        
        console.print("\n[bold yellow]📝 Entrez votre ordre en français (soyez précis sur ce que vous voulez):[/bold yellow]")
        
        # Demander l'ordre en langage naturel
        natural_command = console.input("[bold green]🗨️ Votre ordre>[/bold green] ").strip()
        
        if not natural_command:
            console.print("❌ Ordre requis.")
            return
            
        console.print(f"\n[dim]💭 Ordre reçu: « {natural_command} »[/dim]")
        
        # Configuration
        folder_path = Prompt.ask("Dossier à traiter", default=".")
        if not os.path.exists(folder_path):
            console.print("❌ Dossier inexistant.")
            return
        
        # Patterns de fichiers
        console.print("\n[dim]Patterns de fichiers (séparés par des virgules):[/dim]")
        console.print("[dim]Exemples: *.py,*.js,*.ts,*.java,*.go,*.php,*.rb,*.rs[/dim]")
        patterns_input = Prompt.ask("Patterns", default="*.py,*.js,*.ts,*.java")
        patterns = [p.strip() for p in patterns_input.split(",")]
        
        # Options avancées
        recursive = Confirm.ask("Analyse récursive des sous-répertoires ?", default=True)
        
        # Prévisualisation
        files_found = []
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                    'node_modules', 'build', 'dist', '__pycache__', 'target'
                ]]
                for file in files:
                    file_path = os.path.join(root, file)
                    if any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                        files_found.append(file_path)
        else:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path) and any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                    files_found.append(file_path)
        
        console.print(f"\n📊 [bold]Prévisualisation:[/bold]")
        console.print(f"📁 Dossier: {folder_path}")
        console.print(f"🗣️ Ordre: « {natural_command} »")
        console.print(f"📄 Fichiers trouvés: {len(files_found)}")
        
        if len(files_found) <= 10:
            for file_path in files_found:
                console.print(f"   • {file_path}")
        else:
            for file_path in files_found[:5]:
                console.print(f"   • {file_path}")
            console.print(f"   ... et {len(files_found)-5} autres fichiers")
        
        if not files_found:
            console.print("⚠️ Aucun fichier trouvé avec ces patterns.")
            return
        
        # Confirmation
        if not Confirm.ask(f"\n[bold yellow]Continuer avec le traitement de {len(files_found)} fichiers ?[/bold yellow]"):
            console.print("Opération annulée.")
            return
        
        apply_changes = Confirm.ask("Appliquer automatiquement les modifications ?", default=False)
        max_file_size = int(Prompt.ask("Taille max par fichier (bytes)", default="100000"))
        
        # Exécution avec le nouveau système de langage naturel
        try:
            console.print(f"\n🧠 [bold green]Démarrage de l'interprétation et exécution...[/bold green]")
            
            with Live(Spinner("dots", text="Interprétation et exécution en cours..."), console=console):
                # Préparer le contexte pour le système de langage naturel
                context = Context()
                context.data = {
                    "folder_path": folder_path,
                    "natural_command": natural_command,
                    "patterns": patterns,
                    "recursive": recursive,
                    "apply_changes": apply_changes,
                    "max_file_size": max_file_size,
                    "api_key": api_key
                }
                
                from mistral_cli.tools.file_analyzer.natural_language_executor import execute
                result_context = execute(context)
            
            # Afficher les résultats
            try:
                output_data = json.loads(result_context.data["output"])
                
                console.print(f"\n✅ [bold green]EXÉCUTION TERMINÉE[/bold green]")
                console.print(f"🗣️ Ordre: « {natural_command} »")
                console.print(f"📁 Dossier: {folder_path}")
                console.print(f"📄 Fichiers trouvés: {output_data.get('total_files_found', 0)}")
                console.print(f"✅ Fichiers traités: {output_data.get('files_processed', 0)}")
                console.print(f"🔄 Fichiers modifiés: {output_data.get('files_changed', 0)}")
                console.print(f"⏭️ Fichiers ignorés: {output_data.get('files_skipped', 0)}")
                console.print(f"❌ Erreurs: {output_data.get('errors_count', 0)}")
                
                if output_data.get('summary'):
                    console.print("\n[bold green]📋 RAPPORT DÉTAILLÉ:[/bold green]")
                    console.print(Panel(output_data['summary'], border_style="green"))
                
                if output_data.get('errors'):
                    console.print("\n[bold red]⚠️ ERREURS:[/bold red]")
                    for error in output_data['errors']:
                        console.print(f"• {error}")
                
                # Sauvegarder le rapport
                report_file = f"natural_language_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                
                console.print(f"\n💾 [bold blue]Rapport détaillé sauvegardé:[/bold blue] {report_file}")
                
                if apply_changes and output_data.get('files_changed', 0) > 0:
                    console.print(f"\n🔄 [bold yellow]MODIFICATIONS APPLIQUÉES[/bold yellow]")
                    console.print(f"📁 Les fichiers originaux sont sauvegardés avec l'extension .backup")
                    console.print(f"⚠️ Vérifiez les modifications avant de supprimer les backups")
                
            except json.JSONDecodeError:
                console.print(f"❌ Erreur lors du parsing des résultats: {result_context.data['output']}")
                
        except ImportError:
            console.print("❌ Module d'exécution en langage naturel non trouvé.")
        except Exception as e:
            console.print(f"❌ Erreur lors de l'exécution: {str(e)}")
    
    def start(self):
        """Démarre l'interface conversationnelle."""
        # Affichage de bienvenue amélioré
        welcome_text = Text()
        welcome_text.append("🚀 Bienvenue dans ", style="bold cyan")
        welcome_text.append("Mistral CLI", style="bold magenta")
        welcome_text.append(" v0.1.0", style="dim cyan")
        welcome_text.append("\n\n", style="")
        welcome_text.append("✨ Votre assistant IA avec modèles et agents personnalisés", style="italic blue")
        
        console.print(Panel.fit(
            welcome_text,
            title="[bold green]🤖 Mistral AI CLI[/bold green]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        # Afficher le statut actuel
        self._display_session_status()

        while True:
            try:
                # Prompt personnalisé avec informations contextuelles
                prompt_parts = []
                
                # Indicateur d'agent actuel
                if self.current_session.context.current_agent:
                    agent = next(a for a in self.agents if a.id == self.current_session.context.current_agent)
                    if agent.agent_type == "model":
                        prompt_parts.append(f"[dim cyan]📚 {agent.name}[/dim cyan]")
                    else:
                        prompt_parts.append(f"[dim green]🤖 {agent.name}[/dim green]")
                else:
                    prompt_parts.append("[dim red]⚠️ Aucun agent[/dim red]")
                
                # Pipeline actuel
                if self.current_session.context.default_pipeline:
                    prompt_parts.append(f"[dim yellow]🔧 {self.current_session.context.default_pipeline}[/dim yellow]")
                
                prompt_text = " | ".join(prompt_parts) + "\n[bold green]🗨️ Vous>[/bold green] "
                user_input = console.input(prompt_text).strip()

                if not user_input:
                    continue
                elif user_input.lower() in ["quit", "exit", "/exit"]:
                    self.save_session()
                    goodbye_text = Text()
                    goodbye_text.append("👋 Au revoir !", style="bold cyan")
                    goodbye_text.append("\n\n✨ Merci d'avoir utilisé Mistral CLI", style="italic dim")
                    console.print(Panel.fit(
                        goodbye_text,
                        title="[bold green]🎆 À bientôt ![/bold green]",
                        border_style="green",
                        padding=(1, 2)
                    ))
                    break
                elif user_input.lower() == "/add_agent":
                    self._authenticate()
                elif user_input.lower() == "/create_agent":
                    self.create_custom_agent()
                elif user_input.lower() == "/select_agent":
                    self.select_agent()
                elif user_input.lower() == "/list_agents":
                    self.list_agents()
                elif user_input.lower() == "/set_pipeline":
                    self.set_default_pipeline()
                elif user_input.lower() == "/servers":
                    self.manage_servers()
                elif user_input.lower() == "/pipelines":
                    self.display_pipelines()
                    if self.pipelines:
                        self.set_default_pipeline()
                elif user_input.lower() == "/sessions":
                    self.load_session()
                elif user_input.lower() == "/analyze_file":
                    self.analyze_file()
                elif user_input.lower() == "/analyze_batch":
                    self.analyze_batch()
                elif user_input.lower() == "/execute_command":
                    self.execute_command_on_folder()
                elif user_input.lower() == "/install-npm":
                    install_npm_tools()
                elif user_input.lower() == "/help":
                    self.show_help()
                    # Afficher aussi le statut actuel après l'aide
                    self._display_session_status()
                elif self.current_session.context.current_agent and not user_input.startswith("/"):
                    response = self.call_mistral_agent(user_input)
                    
                    # Affichage de la réponse avec formatting amélioré
                    agent = next(a for a in self.agents if a.id == self.current_session.context.current_agent)
                    if agent.agent_type == "model":
                        header = f"[bold cyan]📚 {agent.name}>[/bold cyan]"
                    else:
                        header = f"[bold magenta]🤖 {agent.name}>[/bold magenta]"
                    
                    # Afficher la réponse dans un panel si elle est longue
                    if len(response) > 200:
                        console.print(f"\n{header}")
                        console.print(Panel(
                            Markdown(response),
                            border_style="cyan" if agent.agent_type == "model" else "magenta",
                            padding=(0, 1)
                        ))
                    else:
                        console.print(f"\n{header} {response}")
                elif self.current_session.context.default_pipeline:
                    self.execute_pipeline(self.current_session.context.default_pipeline, user_input)
                else:
                    console.print(Panel.fit(
                        "⚠️ [bold yellow]Aucun agent ou pipeline sélectionné[/bold yellow]\n\n"
                        "🔹 Utilisez [cyan]/select_agent[/cyan] pour choisir un modèle/agent\n"
                        "🔹 Ou [cyan]/create_agent[/cyan] pour créer un agent personnalisé\n"
                        "🔹 Ou [cyan]/set_pipeline[/cyan] pour définir un pipeline",
                        border_style="yellow",
                        title="[bold yellow]🎆 Action requise[/bold yellow]"
                    ))
            except KeyboardInterrupt:
                console.print("\n[yellow]⏸️ Opération annulée[/yellow]")
            except Exception as e:
                error_panel = Panel.fit(
                    f"❌ [bold red]Erreur inattendue[/bold red]\n\n🔴 {str(e)}",
                    border_style="red",
                    title="[red]⚠️ Exception[/red]"
                )
                console.print(error_panel)

# --- Point d'entrée ---
def main():
    """Point d'entrée principal de l'application."""
    import sys
    
    # Gérer les arguments de ligne de commande
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ['--help', '-h']:
            print("""
🤖 Mistral CLI v0.1.0 - Assistant IA avec modèles et agents personnalisés

Usage: mistral-cli [options]

Options:
  -h, --help     Affiche cette aide
  --version      Affiche la version

Fonctionnalités:
  📚 Modèles Mistral - Chat direct avec les modèles
  🤖 Agents personnalisés - Agents avec outils intégrés
  🔧 Outils de développement multi-langages
  💾 Sessions persistantes
  🔒 Chiffrement des clés API

Pour commencer:
  1. Lancez 'mistral-cli' 
  2. Entrez votre clé API Mistral (https://mistral.ai)
  3. Sélectionnez un agent ou créez-en un nouveau

Commandes disponibles dans l'interface:
  /create_agent  - Créer un agent avec outils
  /list_agents   - Voir tous les agents disponibles
  /help         - Aide complète
            """)
            return
        elif arg in ['--version', '-v']:
            print("mistral-cli 0.1.0")
            return
    
    os.makedirs("config/sessions", exist_ok=True)
    bot = MistralChatBot()
    bot.start()

if __name__ == "__main__":
    main()
