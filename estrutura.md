# 📁 Estrutura Completa do Projeto - Guia de Criação

Crie os seguintes arquivos e pastas na raiz do seu projeto:

## 📂 Estrutura de Diretórios

```
secomp-leaderboard/
├── app.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── ESTRUTURA.md
│
├── services/
│   ├── __init__.py
│   ├── github_service.py
│   ├── auth_service.py
│   └── leaderboard_service.py
│
├── views/
│   ├── __init__.py
│   ├── home_view.py
│   ├── login_view.py
│   └── admin_view.py
│
└── utils/
    ├── __init__.py
    ├── navigation.py
    └── styles.py
```

---

## 📄 ARQUIVO 1: `config.py`

```python
"""
Configurações centralizadas da aplicação
"""
import streamlit as st
import os
from dotenv import load_dotenv

class Config:
    """Classe para gerenciar configurações da aplicação"""
    
    def __init__(self):
        self._load_config()
    
    def _load_config(self):
        """Carrega configurações do Streamlit Secrets ou .env"""
        try:
            # Tenta ler do Streamlit Secrets (produção)
            self.GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
            self.GITHUB_REPO = st.secrets["GITHUB_REPO"]
            self.GITHUB_FILE = st.secrets["GITHUB_FILE"]
            self.ADMIN_CREDENTIALS = dict(st.secrets.get("ADMINS", {}))
        except:
            # Fallback para variáveis de ambiente (desenvolvimento)
            load_dotenv()
            
            self.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
            self.GITHUB_REPO = os.getenv("GITHUB_REPO", "")
            self.GITHUB_FILE = os.getenv("GITHUB_FILE", "leaderboard.json")
            
            # Credenciais de admin
            self.ADMIN_CREDENTIALS = {
                os.getenv("ADMIN1_USER", "admin"): os.getenv("ADMIN1_PASS", "secomp2024"),
                os.getenv("ADMIN2_USER", "organizador"): os.getenv("ADMIN2_PASS", "jogos123")
            }
            
            # Aviso se não configurado
            if not self.GITHUB_TOKEN or not self.GITHUB_REPO:
                st.error("⚠️ Configure GITHUB_TOKEN e GITHUB_REPO no .env ou Streamlit Secrets")
    
    def is_configured(self):
        """Verifica se as configurações essenciais estão presentes"""
        return bool(self.GITHUB_TOKEN and self.GITHUB_REPO)

# Instância global de configuração
config = Config()
```

---

## 📄 ARQUIVO 2: `services/__init__.py`

```python
"""
Services Package
Camada de lógica de negócio da aplicação
"""
from .github_service import GitHubService
from .auth_service import AuthService
from .leaderboard_service import LeaderboardService

__all__ = [
    'GitHubService',
    'AuthService',
    'LeaderboardService'
]
```

---

## 📄 ARQUIVO 3: `services/github_service.py`

```python
"""
Serviço para interação com GitHub API
"""
import requests
import json
import base64
import streamlit as st
from datetime import datetime
from typing import Tuple, Dict, Optional

class GitHubService:
    """Serviço para gerenciar dados no GitHub"""
    
    def __init__(self, token: str, repo: str, file: str):
        self.token = token
        self.repo = repo
        self.file = file
        self.base_url = f"https://api.github.com/repos/{repo}/contents/{file}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_data(self) -> Tuple[Dict, Optional[str]]:
        """
        Busca dados do arquivo JSON no GitHub
        
        Returns:
            Tuple[Dict, Optional[str]]: (dados, sha do arquivo)
        """
        if not self.token or not self.repo:
            return {"players": {}}, None
        
        try:
            response = requests.get(self.base_url, headers=self.headers)
            
            if response.status_code == 200:
                content = response.json()
                decoded_content = base64.b64decode(content['content']).decode('utf-8')
                return json.loads(decoded_content), content['sha']
            
            elif response.status_code == 404:
                st.warning("⚠️ Arquivo não encontrado. Será criado ao salvar.")
                return {"players": {}}, None
            
            else:
                st.error(f"❌ Erro ao buscar dados: {response.status_code}")
                return {"players": {}}, None
        
        except Exception as e:
            st.error(f"❌ Erro na conexão: {str(e)}")
            return {"players": {}}, None
    
    def save_data(self, data: Dict, sha: Optional[str] = None) -> bool:
        """
        Salva dados no arquivo JSON do GitHub
        
        Args:
            data: Dicionário com os dados a salvar
            sha: SHA do arquivo existente (para update)
        
        Returns:
            bool: True se salvou com sucesso
        """
        if not self.token or not self.repo:
            st.error("⚠️ Credenciais do GitHub não configuradas")
            return False
        
        try:
            content_encoded = base64.b64encode(
                json.dumps(data, indent=4, ensure_ascii=False).encode()
            ).decode()
            
            payload = {
                "message": f"Update leaderboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "content": content_encoded
            }
            
            if sha:
                payload["sha"] = sha
            
            response = requests.put(self.base_url, headers=self.headers, json=payload)
            
            if response.status_code in [200, 201]:
                return True
            else:
                st.error(f"❌ Erro ao salvar: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            st.error(f"❌ Erro ao salvar: {str(e)}")
            return False
```

---

## 📄 ARQUIVO 4: `services/auth_service.py`

```python
"""
Serviço de autenticação de administradores
"""
import streamlit as st
from typing import Dict

class AuthService:
    """Serviço para gerenciar autenticação de administradores"""
    
    def __init__(self, admin_credentials: Dict[str, str]):
        self.admin_credentials = admin_credentials
        self._init_session_state()
    
    def _init_session_state(self):
        """Inicializa variáveis de sessão"""
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'admin_username' not in st.session_state:
            st.session_state.admin_username = ''
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'home'
    
    def login(self, username: str, password: str) -> bool:
        """
        Realiza login do administrador
        
        Args:
            username: Nome de usuário
            password: Senha
        
        Returns:
            bool: True se login bem-sucedido
        """
        if username in self.admin_credentials and self.admin_credentials[username] == password:
            st.session_state.logged_in = True
            st.session_state.admin_username = username
            return True
        return False
    
    def logout(self):
        """Realiza logout do administrador"""
        st.session_state.logged_in = False
        st.session_state.admin_username = ''
    
    def is_logged_in(self) -> bool:
        """Verifica se usuário está logado"""
        return st.session_state.logged_in
    
    def get_current_user(self) -> str:
        """Retorna nome do usuário logado"""
        return st.session_state.admin_username
    
    def require_auth(self):
        """Decorator para exigir autenticação"""
        if not self.is_logged_in():
            st.error("🔒 Acesso negado. Faça login primeiro.")
            st.stop()
```

---

## 📄 ARQUIVO 5: `services/leaderboard_service.py`

```python
"""
Serviço de gerenciamento do leaderboard
"""
from typing import Dict, List, Tuple
from services.github_service import GitHubService

class LeaderboardService:
    """Serviço para gerenciar o ranking de jogadores"""
    
    def __init__(self, github_service: GitHubService):
        self.github = github_service
    
    def get_players(self) -> Dict[str, int]:
        """
        Retorna todos os jogadores
        
        Returns:
            Dict[str, int]: Dicionário {nome: pontos}
        """
        data, _ = self.github.get_data()
        return data.get("players", {})
    
    def get_sorted_players(self) -> List[Tuple[str, int]]:
        """
        Retorna jogadores ordenados por pontos (decrescente)
        
        Returns:
            List[Tuple[str, int]]: Lista de tuplas (nome, pontos)
        """
        players = self.get_players()
        return sorted(players.items(), key=lambda x: x[1], reverse=True)
    
    def add_player(self, name: str, points: int = 0) -> bool:
        """
        Adiciona ou atualiza um jogador
        
        Args:
            name: Nome do jogador
            points: Pontos iniciais
        
        Returns:
            bool: True se salvou com sucesso
        """
        data, sha = self.github.get_data()
        players = data.get("players", {})
        
        players[name.strip()] = points
        data["players"] = players
        
        return self.github.save_data(data, sha)
    
    def update_points(self, name: str, points_change: int) -> bool:
        """
        Adiciona ou remove pontos de um jogador
        
        Args:
            name: Nome do jogador
            points_change: Quantidade de pontos a adicionar (positivo) ou remover (negativo)
        
        Returns:
            bool: True se salvou com sucesso
        """
        data, sha = self.github.get_data()
        players = data.get("players", {})
        
        if name not in players:
            return False
        
        players[name] = players[name] + points_change
        data["players"] = players
        
        return self.github.save_data(data, sha)
    
    def remove_player(self, name: str) -> bool:
        """
        Remove um jogador do ranking
        
        Args:
            name: Nome do jogador
        
        Returns:
            bool: True se removeu com sucesso
        """
        data, sha = self.github.get_data()
        players = data.get("players", {})
        
        if name not in players:
            return False
        
        del players[name]
        data["players"] = players
        
        return self.github.save_data(data, sha)
    
    def get_player_rank(self, name: str) -> int:
        """
        Retorna a posição de um jogador no ranking
        
        Args:
            name: Nome do jogador
        
        Returns:
            int: Posição no ranking (1-indexed), 0 se não encontrado
        """
        sorted_players = self.get_sorted_players()
        for idx, (player_name, _) in enumerate(sorted_players, 1):
            if player_name == name:
                return idx
        return 0
```

---

## 📄 ARQUIVO 6: `utils/__init__.py`

```python
"""
Utils Package
Utilitários da aplicação
"""
from .navigation import Navigation
from .styles import Styles

__all__ = [
    'Navigation',
    'Styles'
]
```

---

## 📄 ARQUIVO 7: `utils/navigation.py`

```python
"""
Utilitários de navegação entre páginas
"""
import streamlit as st

class Navigation:
    """Classe para gerenciar navegação entre páginas"""
    
    @staticmethod
    def go_to_home():
        """Navega para a página inicial"""
        st.session_state.current_page = 'home'
        st.session_state.logged_in = False
    
    @staticmethod
    def go_to_login():
        """Navega para a página de login"""
        st.session_state.current_page = 'login'
    
    @staticmethod
    def go_to_admin():
        """Navega para a página de administração"""
        st.session_state.current_page = 'admin'
    
    @staticmethod
    def get_current_page() -> str:
        """Retorna a página atual"""
        return st.session_state.get('current_page', 'home')
```

---

## 📄 ARQUIVO 8: `utils/styles.py`

```python
"""
Estilos CSS para a aplicação
"""
import streamlit as st

class Styles:
    """Classe para gerenciar estilos CSS"""
    
    # Cores do tema
    COLORS = {
        'background': '#0E1117',
        'text': '#FAFAFA',
        'primary': '#FF4B4B',
        'secondary': '#262730',
        'border': '#262730',
        'gold': '#FFD700',
        'silver': '#C0C0C0',
        'bronze': '#CD7F32',
    }
    
    @staticmethod
    def apply_dark_mode():
        """Aplica CSS para modo escuro"""
        st.markdown("""
        <style>
            .stApp {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            .stButton>button {
                background-color: #FF4B4B;
                color: white;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
            }
            .stTextInput>div>div>input {
                background-color: #262730;
                color: white;
            }
            .stNumberInput>div>div>input {
                background-color: #262730;
                color: white;
            }
            .stSelectbox>div>div>div {
                background-color: #262730;
                color: white;
            }
            h1, h2, h3 {
                color: #FAFAFA;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def player_card(medal: str, name: str, points: int, color: str) -> str:
        """
        Retorna HTML para um card de jogador do pódio
        
        Args:
            medal: Emoji da medalha
            name: Nome do jogador
            points: Pontos do jogador
            color: Cor da borda
        
        Returns:
            str: HTML do card
        """
        return f"""
        <div style='text-align: center; padding: 20px; background-color: #1E1E1E; 
                    border-radius: 10px; border: 3px solid {color}; margin: 10px 0;'>
            <h1 style='margin: 0; font-size: 48px;'>{medal}</h1>
            <h3 style='margin: 10px 0; color: #FAFAFA;'>{name}</h3>
            <h2 style='color: {color}; margin: 0;'>{points} pts</h2>
        </div>
        """
    
    @staticmethod
    def divider():
        """Retorna HTML para um divisor horizontal"""
        return "<hr style='border: 1px solid #262730; margin: 10px 0;'>"
```

---

Continua no próximo artefato...

# 📁 Estrutura Completa - Parte 2

## 📄 ARQUIVO 9: `views/__init__.py`

```python
"""
Views Package
Camada de apresentação da aplicação
"""
from .home_view import HomeView
from .login_view import LoginView
from .admin_view import AdminView

__all__ = [
    'HomeView',
    'LoginView',
    'AdminView'
]
```

---

## 📄 ARQUIVO 10: `views/home_view.py`

```python
"""
View da página Home/Leaderboard
"""
import streamlit as st
from services.leaderboard_service import LeaderboardService
from utils.navigation import Navigation
from utils.styles import Styles

class HomeView:
    """View da página inicial com o leaderboard"""
    
    def __init__(self, leaderboard_service: LeaderboardService):
        self.leaderboard = leaderboard_service
        self.nav = Navigation()
    
    def render(self):
        """Renderiza a página home"""
        st.title("🎮 SECOMP - Sala de Jogos Leaderboard")
        st.markdown("---")
        
        # Botão de refresh
        self._render_refresh_button()
        
        # Carregar e exibir ranking
        players = self.leaderboard.get_players()
        
        if not players:
            st.info("📊 Nenhum jogador cadastrado ainda. Aguarde os administradores adicionarem participantes!")
        else:
            sorted_players = self.leaderboard.get_sorted_players()
            self._render_top_three(sorted_players)
            st.markdown("---")
            self._render_full_ranking(sorted_players)
        
        # Botão para área admin
        self._render_admin_button()
    
    def _render_refresh_button(self):
        """Renderiza botão de atualização"""
        col1, col2, col3 = st.columns([4, 1, 1])
        with col2:
            if st.button("🔄 Atualizar", use_container_width=True):
                st.rerun()
    
    def _render_top_three(self, sorted_players: list):
        """Renderiza o top 3 jogadores"""
        st.subheader("🏆 Top 3")
        cols = st.columns(3)
        
        medals = ["🥇", "🥈", "🥉"]
        colors = [Styles.COLORS['gold'], Styles.COLORS['silver'], Styles.COLORS['bronze']]
        
        for idx, (name, points) in enumerate(sorted_players[:3]):
            with cols[idx]:
                st.markdown(
                    Styles.player_card(medals[idx], name, points, colors[idx]),
                    unsafe_allow_html=True
                )
    
    def _render_full_ranking(self, sorted_players: list):
        """Renderiza ranking completo"""
        st.subheader("📋 Ranking Completo")
        
        medals = ["🥇", "🥈", "🥉"]
        
        for position, (name, points) in enumerate(sorted_players, 1):
            col1, col2, col3 = st.columns([1, 4, 2])
            
            with col1:
                if position <= 3:
                    st.markdown(f"<h3 style='color: #FAFAFA;'>{medals[position-1]}</h3>", 
                              unsafe_allow_html=True)
                else:
                    st.markdown(f"<h3 style='color: #FAFAFA;'>#{position}</h3>", 
                              unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<h3 style='color: #FAFAFA;'>{name}</h3>", 
                          unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"<h3 style='color: #FF4B4B;'>{points} pontos</h3>", 
                          unsafe_allow_html=True)
            
            st.markdown(Styles.divider(), unsafe_allow_html=True)
    
    def _render_admin_button(self):
        """Renderiza botão para área administrativa"""
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔐 Área de Administrador", use_container_width=True, type="primary"):
                self.nav.go_to_login()
                st.rerun()
```

---

## 📄 ARQUIVO 11: `views/login_view.py`

```python
"""
View da página de Login
"""
import streamlit as st
from services.auth_service import AuthService
from utils.navigation import Navigation

class LoginView:
    """View da página de login de administradores"""
    
    def __init__(self, auth_service: AuthService):
        self.auth = auth_service
        self.nav = Navigation()
    
    def render(self):
        """Renderiza a página de login"""
        st.title("🔐 Login de Administrador")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.subheader("Acesso Restrito")
            
            username = st.text_input("Usuário", key="login_username")
            password = st.text_input("Senha", type="password", key="login_password")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🔓 Entrar", use_container_width=True, type="primary"):
                    self._handle_login(username, password)
            
            with col_btn2:
                if st.button("🏠 Voltar", use_container_width=True):
                    self.nav.go_to_home()
                    st.rerun()
    
    def _handle_login(self, username: str, password: str):
        """
        Processa tentativa de login
        
        Args:
            username: Nome de usuário
            password: Senha
        """
        if self.auth.login(username, password):
            self.nav.go_to_admin()
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Credenciais inválidas!")
```

---

## 📄 ARQUIVO 12: `views/admin_view.py`

```python
"""
View da página de Administração
"""
import streamlit as st
from services.auth_service import AuthService
from services.leaderboard_service import LeaderboardService
from utils.navigation import Navigation

class AdminView:
    """View da página de administração"""
    
    def __init__(self, auth_service: AuthService, leaderboard_service: LeaderboardService):
        self.auth = auth_service
        self.leaderboard = leaderboard_service
        self.nav = Navigation()
    
    def render(self):
        """Renderiza a página de administração"""
        # Verificar autenticação
        if not self.auth.is_logged_in():
            self.nav.go_to_login()
            st.rerun()
            return
        
        # Header
        current_user = self.auth.get_current_user()
        st.title(f"⚙️ Painel de Administração - {current_user}")
        
        if st.button("🚪 Sair", type="secondary"):
            self.nav.go_to_home()
            st.rerun()
        
        st.markdown("---")
        
        # Tabs principais
        tab1, tab2 = st.tabs(["➕ Cadastrar/Editar Jogador", "📊 Gerenciar Pontos"])
        
        with tab1:
            self._render_player_management()
        
        with tab2:
            self._render_points_management()
        
        # Lista de todos os jogadores
        st.markdown("---")
        self._render_all_players()
    
    def _render_player_management(self):
        """Renderiza seção de cadastro/edição de jogadores"""
        st.subheader("Cadastrar Novo Jogador ou Editar Existente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            player_name = st.text_input("Nome do Jogador", key="new_player_name")
            initial_points = st.number_input(
                "Pontos Iniciais", 
                min_value=0, 
                value=0, 
                step=10, 
                key="initial_points"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✅ Cadastrar/Atualizar", type="primary", use_container_width=True):
                if player_name.strip():
                    if self.leaderboard.add_player(player_name.strip(), initial_points):
                        st.success(f"✅ Jogador '{player_name}' cadastrado com {initial_points} pontos!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Erro ao cadastrar jogador!")
                else:
                    st.error("❌ Digite um nome válido!")
    
    def _render_points_management(self):
        """Renderiza seção de gerenciamento de pontos"""
        st.subheader("Adicionar/Remover Pontos")
        
        players = self.leaderboard.get_players()
        
        if not players:
            st.info("📊 Nenhum jogador cadastrado ainda.")
            return
        
        selected_player = st.selectbox(
            "Selecione o Jogador", 
            options=sorted(players.keys())
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_points = players.get(selected_player, 0)
            st.markdown(f"**Pontos Atuais:** {current_points}")
            points_to_add = st.number_input(
                "Pontos a Adicionar/Remover", 
                value=0, 
                step=10, 
                key="points_change"
            )
            st.info("💡 Use números negativos para remover pontos")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Botão adicionar pontos
            if st.button("➕ Adicionar Pontos", type="primary", use_container_width=True):
                if selected_player and points_to_add != 0:
                    if self.leaderboard.update_points(selected_player, points_to_add):
                        if points_to_add > 0:
                            st.success(f"✅ {points_to_add} pontos adicionados a {selected_player}!")
                        else:
                            st.success(f"✅ {abs(points_to_add)} pontos removidos de {selected_player}!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao atualizar pontos!")
                else:
                    st.warning("⚠️ Selecione um valor diferente de zero!")
            
            # Botão remover jogador
            if st.button("🗑️ Remover Jogador", type="secondary", use_container_width=True):
                if selected_player:
                    if st.session_state.get('confirm_delete') == selected_player:
                        if self.leaderboard.remove_player(selected_player):
                            st.success(f"✅ Jogador '{selected_player}' removido!")
                            st.session_state.confirm_delete = None
                            st.rerun()
                        else:
                            st.error("❌ Erro ao remover jogador!")
                    else:
                        st.session_state.confirm_delete = selected_player
                        st.warning("⚠️ Clique novamente para confirmar a exclusão!")
    
    def _render_all_players(self):
        """Renderiza lista de todos os jogadores"""
        st.subheader("📋 Lista de Todos os Jogadores")
        
        sorted_players = self.leaderboard.get_sorted_players()
        
        if not sorted_players:
            st.info("📊 Nenhum jogador cadastrado.")
            return
        
        for idx, (name, points) in enumerate(sorted_players, 1):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.write(f"**#{idx}**")
            with col2:
                st.write(f"**{name}**")
            with col3:
                st.write(f"**{points}** pts")
```

---

## 📄 ARQUIVO 13: `app.py` (PRINCIPAL)

```python
"""
SECOMP - Sala de Jogos Leaderboard
Aplicação principal refatorada
"""
import streamlit as st

# Importações dos módulos
from config import config
from services.github_service import GitHubService
from services.auth_service import AuthService
from services.leaderboard_service import LeaderboardService
from views.home_view import HomeView
from views.login_view import LoginView
from views.admin_view import AdminView
from utils.navigation import Navigation
from utils.styles import Styles

# Configuração da página
st.set_page_config(
    page_title="SECOMP - Sala de Jogos Leaderboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Aplicar estilos
Styles.apply_dark_mode()

# Inicializar serviços
github_service = GitHubService(
    token=config.GITHUB_TOKEN,
    repo=config.GITHUB_REPO,
    file=config.GITHUB_FILE
)

auth_service = AuthService(
    admin_credentials=config.ADMIN_CREDENTIALS
)

leaderboard_service = LeaderboardService(
    github_service=github_service
)

# Inicializar views
home_view = HomeView(leaderboard_service)
login_view = LoginView(auth_service)
admin_view = AdminView(auth_service, leaderboard_service)

# Roteamento de páginas
def main():
    """Função principal da aplicação"""
    current_page = Navigation.get_current_page()
    
    if current_page == 'home':
        home_view.render()
    elif current_page == 'login':
        login_view.render()
    elif current_page == 'admin':
        admin_view.render()
    else:
        # Fallback para home
        Navigation.go_to_home()
        st.rerun()

if __name__ == "__main__":
    main()
```

---

## 📄 ARQUIVO 14: `requirements.txt`

```
streamlit==1.31.0
requests==2.31.0
python-dotenv==1.0.0
```

---

## 📄 ARQUIVO 15: `.env` (Exemplo)

```bash
# GitHub API Configuration
GITHUB_TOKEN=ghp_seu_token_aqui
GITHUB_REPO=usuario/repositorio
GITHUB_FILE=leaderboard.json

# Admin Credentials
ADMIN1_USER=admin
ADMIN1_PASS=secomp2024
ADMIN2_USER=organizador
ADMIN2_PASS=jogos123
```

---

## 📄 ARQUIVO 16: `.gitignore`

```
# Environment Variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Streamlit
.streamlit/secrets.toml

# Logs
*.log

# Testing
.pytest_cache/
.coverage
htmlcov/

# Backup files
*.bak
*.backup

# Temporary files
*.tmp
temp/
tmp/
```

---

## 🚀 INSTRUÇÕES DE INSTALAÇÃO

### Passo 1: Criar a estrutura de pastas

```bash
mkdir secomp-leaderboard
cd secomp-leaderboard

mkdir services
mkdir views
mkdir utils
```

### Passo 2: Criar os arquivos

Crie cada arquivo mencionado acima copiando o conteúdo correspondente.

**Arquivos na raiz:**
- `app.py`
- `config.py`
- `requirements.txt`
- `.env`
- `.gitignore`

**Pasta services/:**
- `__init__.py`
- `github_service.py`
- `auth_service.py`
- `leaderboard_service.py`

**Pasta views/:**
- `__init__.py`
- `home_view.py`
- `login_view.py`
- `admin_view.py`

**Pasta utils/:**
- `__init__.py`
- `navigation.py`
- `styles.py`

### Passo 3: Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Configurar o .env

Edite o arquivo `.env` com suas credenciais do GitHub.

### Passo 5: Executar

```bash
streamlit run app.py
```

---

## 📋 CHECKLIST DE VERIFICAÇÃO

- [ ] Todas as pastas criadas (services/, views/, utils/)
- [ ] Todos os arquivos `__init__.py` criados
- [ ] Arquivo `app.py` na raiz
- [ ] Arquivo `config.py` na raiz
- [ ] Arquivo `.env` configurado com token do GitHub
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Aplicação rodando sem erros

---

## 🎯 PRÓXIMOS PASSOS

1. **Teste localmente**: Execute `streamlit run app.py`
2. **Faça commit no GitHub**: 
   ```bash
   git init
   git add .
   git commit -m "Projeto modularizado"
   git push
   ```
3. **Deploy no Streamlit Cloud**: Configure as secrets conforme README.md

---

## 💡 DICAS

- Cada arquivo pode ser copiado individualmente
- Use um editor de código (VS Code, PyCharm) para facilitar
- Os arquivos `__init__.py` podem estar vazios ou com imports
- O `.env` NÃO deve ir para o GitHub (já está no .gitignore)