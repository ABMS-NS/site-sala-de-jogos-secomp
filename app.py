import streamlit as st
import requests
import json
import base64
import os
from datetime import datetime

from aux.go_to import go_to_home, go_to_login, go_to_admin # Funções de navegação postas aqui agora
from aux.git_api import get_github_data, save_github_data # Funções de interação com GitHub
from views.home import home_page # Página inicial (leaderboard)
from views.pagina_login import login_page # Página de login
from views.admin_page import admin_page # Página de administração

# Configuração da página em modo escuro
st.set_page_config(
    page_title="SECOMP - Sala de Jogos Leaderboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS para forçar modo escuro
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

# Configurações do GitHub
# Lê das secrets do Streamlit Cloud ou variáveis de ambiente
try:
    # Tenta ler do Streamlit Secrets (quando hospedado no Streamlit Cloud)
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    GITHUB_REPO = st.secrets["GITHUB_REPO"]
    GITHUB_FILE = st.secrets["GITHUB_FILE"]
except:
    # Fallback para variáveis de ambiente locais (desenvolvimento)
    from dotenv import load_dotenv
    load_dotenv()
    
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "")
    GITHUB_FILE = os.getenv("GITHUB_FILE", "leaderboard.json")
    
    # Aviso se as credenciais não estiverem configuradas
    if not GITHUB_TOKEN or not GITHUB_REPO:
        st.error("⚠️ Configure as variáveis GITHUB_TOKEN e GITHUB_REPO no arquivo .env ou nas Secrets do Streamlit Cloud")

# Credenciais de admin
# Lê das secrets do Streamlit Cloud ou variáveis de ambiente
try:
    # Tenta ler do Streamlit Secrets
    ADMIN_CREDENTIALS = dict(st.secrets.get("ADMINS", {}))
except:
    # Fallback para variáveis de ambiente ou hardcoded (desenvolvimento)
    admin1_user = os.getenv("ADMIN1_USER", "admin")
    admin1_pass = os.getenv("ADMIN1_PASS", "secomp2024")
    admin2_user = os.getenv("ADMIN2_USER", "organizador")
    admin2_pass = os.getenv("ADMIN2_PASS", "jogos123")
    
    ADMIN_CREDENTIALS = {
        admin1_user: admin1_pass,
        admin2_user: admin2_pass
    }



# Inicialização do session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'admin_username' not in st.session_state:
    st.session_state.admin_username = ''

# Roteamento de páginas
if st.session_state.current_page == 'home':
    home_page()
elif st.session_state.current_page == 'login':
    login_page()
elif st.session_state.current_page == 'admin':
    admin_page()