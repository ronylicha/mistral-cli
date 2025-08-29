import json
import os
import subprocess
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
from pydantic import BaseModel
import requests
from cryptography.fernet import Fernet
import base64
import hashlib
import getpass
import readline

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
    active: bool = True
    encrypted_api_key: Optional[str] = None  # Clé API chiffrée

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

# --- Gestion des fichiers ---
def load_config(file_path: str, model) -> List:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [model(**item) for item in json.load(f)]
    except FileNotFoundError:
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
            self._authenticate()  # Demande une authentification si aucun agent

        self.load_session()

    def _authenticate(self):
        """Interface d'authentification pour ajouter une clé API Mistral."""
        console.print(Panel.fit(
            "[bold yellow]🔐 Authentification requise[/bold yellow]\n"
            "Pour utiliser Mistral CLI, vous devez ajouter une clé API Mistral.\n"
            "Vous pouvez en obtenir une sur [link=https://mistral.ai]https://mistral.ai[/link]."
        ))

        api_key = getpass.getpass("Entrez votre clé API Mistral: ").strip()
        if not api_key:
            console.print("[red]❌ Clé API requise.[/red]")
            exit(1)

        agents_data = self._fetch_mistral_agents(api_key)
        if not agents_data:
            console.print("[red]❌ Impossible de récupérer les agents. Vérifiez votre clé API.[/red]")
            exit(1)

        self._save_agents(agents_data, api_key)
        console.print(f"✅ {len(agents_data)} agents Mistral ajoutés.")

    def _fetch_mistral_agents(self, api_key: str) -> List[Dict[str, Any]]:
        """Récupère les agents depuis l'API Mistral."""
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                "https://api.mistral.ai/v1/agents",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("agents", [])
        except requests.RequestException as e:
            console.print(f"[red]❌ Erreur API:[/red] {e}")
            return []

    def _save_agents(self, agents_data: List[Dict[str, Any]], api_key: str):
        """Sauvegarde les agents avec leur clé API chiffrée."""
        new_agents = []
        for agent_data in agents_data:
            agent = MistralAgent(
                id=agent_data["id"],
                name=agent_data["name"],
                model=agent_data["model"]
            )
            agent.api_key = api_key  # La propriété setter chiffre automatiquement
            new_agents.append(agent)

        existing_agents = load_config(AGENTS_FILE, MistralAgent)
        updated_agents = existing_agents + [
            a for a in new_agents if a.id not in {e.id for e in existing_agents}
        ]

        save_config(AGENTS_FILE, updated_agents)
        self.agents = updated_agents

    # --- Gestion des agents Mistral ---
    def list_agents(self):
        """Liste les agents Mistral disponibles."""
        if not self.agents:
            console.print("Aucun agent Mistral configuré.")
            return

        console.print("\n🤖 [bold]Agents Mistral disponibles:[/bold]")
        for agent in self.agents:
            status = "✅" if agent.id == self.current_session.context.current_agent else "   "
            console.print(f"{status} {agent.name} (Modèle: {agent.model})")

    def select_agent(self):
        """Sélectionne un agent Mistral pour la session."""
        if not self.agents:
            console.print("⚠️ Aucun agent Mistral configuré.")
            return

        choices = [f"{agent.name} ({agent.model})" for agent in self.agents] + ["Annuler"]
        choice = Prompt.ask("Sélectionnez un agent Mistral", choices=choices)

        if choice != "Annuler":
            selected_agent_name = choice.split(" (")[0]
            agent = next(a for a in self.agents if a.name == selected_agent_name)
            self.current_session.context.current_agent = agent.id
            console.print(f"🤖 Agent sélectionné: [bold]{agent.name}[/bold] (Modèle: {agent.model})")

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
        """Charge une session existante ou en crée une nouvelle."""
        sessions = []
        session_files = [f for f in os.listdir("config/sessions") if f.endswith(".json")]
        for file in session_files:
            with open(f"config/sessions/{file}", "r", encoding="utf-8") as f:
                sessions.extend([ChatSession(**s) for s in json.load(f)])

        if not sessions:
            self.current_session = ChatSession(
                session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                context=Context(allowed_dirs=[os.getcwd()])
            )
            console.print("Nouvelle session créée.")
            return

        choices = [f"Session {s.session_id}" for s in sessions] + ["Nouvelle session"]
        choice = Prompt.ask("Charger une session", choices=choices)

        if choice == "Nouvelle session":
            self.current_session = ChatSession(
                session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                context=Context(allowed_dirs=[os.getcwd()])
            )
        else:
            session_id = choice.split(" ")[1]
            self.current_session = next(s for s in sessions if s.session_id == session_id)
            if self.current_session.context.default_pipeline:
                console.print(f"Pipeline par défaut: {self.current_session.context.default_pipeline}")
            if self.current_session.context.current_agent:
                agent = next(a for a in self.agents if a.id == self.current_session.context.current_agent)
                console.print(f"Agent Mistral: {agent.name} ({agent.model})")

    def save_session(self):
        """Sauvegarde la session courante."""
        save_config(f"config/sessions/{self.current_session.session_id}.json", [self.current_session])

    # --- Interface principale ---
    def show_help(self):
        console.print(
            "\n[bold]Commandes disponibles:[/bold]\n"
            "/add_agent      - Ajouter un agent Mistral\n"
            "/select_agent   - Sélectionner un agent\n"
            "/list_agents    - Lister les agents\n"
            "/set_pipeline   - Définir un pipeline par défaut\n"
            "/servers        - Gérer les serveurs MCP\n"
            "/pipelines      - Gérer les pipelines\n"
            "/sessions       - Changer de session\n"
            "/help           - Affiche cette aide\n"
            "/exit           - Quitter\n\n"
            "Sans commande, votre message est envoyé à l'agent Mistral sélectionné."
        )

    def call_mistral_agent(self, prompt: str) -> str:
        """Appelle l'API Mistral avec l'agent sélectionné."""
        if not self.current_session.context.current_agent:
            console.print("⚠️ Aucun agent sélectionné. Utilisez `/select_agent`.")
            return ""

        agent = next(a for a in self.agents if a.id == self.current_session.context.current_agent)
        if not agent.api_key:
            console.print("⚠️ Clé API manquante pour cet agent.")
            return ""

        try:
            headers = {"Authorization": f"Bearer {agent.api_key}"}
            data = {"prompt": prompt, "agent_id": agent.id}

            with Live(Spinner("dots", text="Interrogation de Mistral..."), console=console) as live:
                response = requests.post(
                    "https://api.mistral.ai/v1/chat",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                response.raise_for_status()

            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "Réponse vide.")

        except requests.RequestException as e:
            console.print(f"❌ Erreur API Mistral: {e}")
            return f"Erreur: {str(e)}"

    def start(self):
        """Démarre l'interface conversationnelle."""
        console.print(Panel.fit("[bold green]🚀 Bienvenue dans Mistral CLI![/bold green]"), style="bold blue")

        while True:
            try:
                user_input = console.input("\n[bold green]Vous>[/bold green] ").strip()

                if not user_input:
                    continue

                elif user_input.lower() in ["quit", "exit", "/exit"]:
                    self.save_session()
                    console.print("Au revoir !")
                    break

                elif user_input.lower() == "/add_agent":
                    self._authenticate()  # Réauthentification si besoin

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

                elif user_input.lower() == "/help":
                    self.show_help()

                elif self.current_session.context.current_agent and not user_input.startswith("/"):
                    # Envoyer à l'agent Mistral sélectionné
                    response = self.call_mistral_agent(user_input)
                    console.print(f"\n[bold cyan]Mistral>[/bold cyan] {response}")

                elif self.current_session.context.default_pipeline:
                    # Exécuter le pipeline par défaut
                    self.execute_pipeline(self.current_session.context.default_pipeline, user_input)

                else:
                    console.print(
                        "⚠️ Aucun agent Mistral ou pipeline sélectionné. "
                        "Utilisez `/select_agent` ou `/set_pipeline`."
                    )

            except KeyboardInterrupt:
                console.print("\nOpération annulée.")
            except Exception as e:
                console.print(f"[red]❌ Erreur:[/red] {e}")

# --- Point d'entrée ---
if __name__ == "__main__":
    os.makedirs("config/sessions", exist_ok=True)
    bot = MistralChatBot()
    bot.start()
