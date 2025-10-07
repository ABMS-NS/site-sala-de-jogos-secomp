import streamlit as st
from aux.git_api import get_github_data
from aux.go_to import go_to_login


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