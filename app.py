import streamlit as st
import requests
import json
import base64
import os
from datetime import datetime

from aux.go_to import go_to_home, go_to_login, go_to_admin # Funções de navegação postas aqui agora
from aux.git_api import get_github_data, save_github_data # Funções de interação com GitHub

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


# PÁGINA HOME - LEADERBOARD
def home_page():
    st.title("🎮 SECOMP - Sala de Jogos Leaderboard")
    st.markdown("---")
    
    # Botão de refresh
    col_refresh1, col_refresh2, col_refresh3 = st.columns([4, 1, 1])
    with col_refresh2:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.rerun()
    
    # Carregar dados do GitHub
    with st.spinner("Carregando ranking..."):
        data, _ = get_github_data()
        players = data.get("players", {})
    
    if not players:
        st.info("📊 Nenhum jogador cadastrado ainda. Aguarde os administradores adicionarem participantes!")
    else:
        # Ordenar jogadores por pontos (decrescente)
        sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)
        
        # Exibir top 3 com destaque
        st.subheader("🏆 Top 3")
        cols = st.columns(3)
        
        medals = ["🥇", "🥈", "🥉"]
        colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
        
        for idx, (name, points) in enumerate(sorted_players[:3]):
            with cols[idx]:
                st.markdown(f"""
                <div style='text-align: center; padding: 20px; background-color: #1E1E1E; border-radius: 10px; border: 3px solid {colors[idx]}; margin: 10px 0;'>
                    <h1 style='margin: 0; font-size: 48px;'>{medals[idx]}</h1>
                    <h3 style='margin: 10px 0; color: #FAFAFA;'>{name}</h3>
                    <h2 style='color: {colors[idx]}; margin: 0;'>{points} pts</h2>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabela completa de ranking
        st.subheader("📋 Ranking Completo")
        
        for position, (name, points) in enumerate(sorted_players, 1):
            col1, col2, col3 = st.columns([1, 4, 2])
            
            with col1:
                if position <= 3:
                    st.markdown(f"<h3 style='color: #FAFAFA;'>{medals[position-1]}</h3>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h3 style='color: #FAFAFA;'>#{position}</h3>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<h3 style='color: #FAFAFA;'>{name}</h3>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"<h3 style='color: #FF4B4B;'>{points} pontos</h3>", unsafe_allow_html=True)
            
            st.markdown("<hr style='border: 1px solid #262730; margin: 10px 0;'>", unsafe_allow_html=True)
    
    # Botão para área de admin
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔐 Área de Administrador", use_container_width=True, type="primary"):
            go_to_login()
            st.rerun()

# PÁGINA DE LOGIN
def login_page():
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
                if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.admin_username = username
                    go_to_admin()
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Credenciais inválidas!")
        
        with col_btn2:
            if st.button("🏠 Voltar", use_container_width=True):
                go_to_home()
                st.rerun()

# PÁGINA DE ADMINISTRAÇÃO
def admin_page():
    if not st.session_state.logged_in:
        go_to_login()
        st.rerun()
        return
    
    st.title(f"⚙️ Painel de Administração - {st.session_state.admin_username}")
    
    if st.button("🚪 Sair", type="secondary"):
        go_to_home()
        st.rerun()
    
    st.markdown("---")
    
    # Carregar dados
    data, sha = get_github_data()
    players = data.get("players", {})
    
    # Tabs para diferentes ações
    tab1, tab2 = st.tabs(["➕ Cadastrar/Editar Jogador", "📊 Gerenciar Pontos"])
    
    with tab1:
        st.subheader("Cadastrar Novo Jogador ou Editar Existente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            player_name = st.text_input("Nome do Jogador", key="new_player_name")
            initial_points = st.number_input("Pontos Iniciais", min_value=0, value=0, step=10, key="initial_points")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✅ Cadastrar/Atualizar", type="primary", use_container_width=True):
                if player_name.strip():
                    players[player_name.strip()] = initial_points
                    data["players"] = players
                    if save_github_data(data, sha):
                        st.success(f"✅ Jogador '{player_name}' cadastrado com {initial_points} pontos!")
                        st.balloons()
                        st.rerun()
                else:
                    st.error("❌ Digite um nome válido!")
    
    with tab2:
        st.subheader("Adicionar/Remover Pontos")
        
        if not players:
            st.info("📊 Nenhum jogador cadastrado ainda.")
        else:
            selected_player = st.selectbox("Selecione o Jogador", options=sorted(players.keys()))
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Pontos Atuais:** {players.get(selected_player, 0)}")
                points_to_add = st.number_input("Pontos a Adicionar/Remover", value=0, step=10, key="points_change")
                st.info("💡 Use números negativos para remover pontos")
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("➕ Adicionar Pontos", type="primary", use_container_width=True):
                    if selected_player and points_to_add != 0:
                        players[selected_player] = players.get(selected_player, 0) + points_to_add
                        data["players"] = players
                        if save_github_data(data, sha):
                            if points_to_add > 0:
                                st.success(f"✅ {points_to_add} pontos adicionados a {selected_player}!")
                            else:
                                st.success(f"✅ {abs(points_to_add)} pontos removidos de {selected_player}!")
                            st.rerun()
                    else:
                        st.warning("⚠️ Selecione um valor diferente de zero!")
                
                if st.button("🗑️ Remover Jogador", type="secondary", use_container_width=True):
                    if selected_player:
                        if st.session_state.get('confirm_delete') == selected_player:
                            del players[selected_player]
                            data["players"] = players
                            if save_github_data(data, sha):
                                st.success(f"✅ Jogador '{selected_player}' removido!")
                                st.session_state.confirm_delete = None
                                st.rerun()
                        else:
                            st.session_state.confirm_delete = selected_player
                            st.warning("⚠️ Clique novamente para confirmar a exclusão!")
    
    st.markdown("---")
    st.subheader("📋 Lista de Todos os Jogadores")
    
    if players:
        sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)
        for idx, (name, points) in enumerate(sorted_players, 1):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.write(f"**#{idx}**")
            with col2:
                st.write(f"**{name}**")
            with col3:
                st.write(f"**{points}** pts")

# Roteamento de páginas
if st.session_state.current_page == 'home':
    home_page()
elif st.session_state.current_page == 'login':
    login_page()
elif st.session_state.current_page == 'admin':
    admin_page()