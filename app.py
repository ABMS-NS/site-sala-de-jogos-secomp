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

import os
os.environ["STREAMLIT_WATCHDOG_ENABLED"] = "false"

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
