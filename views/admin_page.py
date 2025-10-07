# PÁGINA DE ADMINISTRAÇÃO


import streamlit as st
from aux.git_api import get_github_data, save_github_data
from aux.go_to import go_to_home, go_to_login




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
